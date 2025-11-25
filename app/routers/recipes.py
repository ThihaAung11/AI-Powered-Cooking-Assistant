from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File
from pydantic import BaseModel

from ..schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut, RecipeSearchFilter
from ..utils.pagination import PaginationParams, PaginatedResponse
from ..services.recipe_service import (
    create_recipe, get_recipe, get_enriched_recipe, 
    list_recipes, list_enriched_recipes,
    search_recipes, search_enriched_recipes, 
    update_recipe, delete_recipe
)
from ..services.storage_service import storage_service
from ..deps import CurrentUser, OptionalCurrentUser, SessionDep

router = APIRouter()


# Schema for LLM recommendation request
class RecipeRecommendationRequest(BaseModel):
    query: str
    max_results: int = 5
    # Same filters as recipe search
    search: Optional[str] = None  # Search in title, description, ingredients
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    min_time: Optional[int] = None  # Minimum cooking time in minutes
    max_time: Optional[int] = None  # Maximum cooking time in minutes
    ingredients: Optional[str] = None  # Search for specific ingredients
    created_by: Optional[int] = None  # Filter by creator


class RecipeRecommendationResponse(BaseModel):
    recommendations: List[RecipeOut]
    explanation: str
    query: str


@router.post("/recommend", response_model=RecipeRecommendationResponse)
async def recommend_recipes_with_llm(
    request: RecipeRecommendationRequest,
    db: SessionDep
):
    """
    Get AI-powered recipe recommendations based on natural language query using LangChain.
    Results are cached for 30 minutes to reduce API calls.
    
    Query examples:
    - "I want something spicy for dinner"
    - "Quick lunch recipes under 30 minutes"
    - "Healthy vegetarian meals"
    - "Italian pasta dishes"
    
    Additional filters (same as recipe search):
    - **search**: Text search in title, description, ingredients
    - **cuisine**: Filter by cuisine type (e.g., "Italian", "Thai")
    - **difficulty**: Filter by difficulty level (Easy, Medium, Hard)
    - **min_time/max_time**: Filter by cooking time range in minutes
    - **ingredients**: Search for specific ingredients
    - **created_by**: Show recipes from a specific user ID
    
    The AI will analyze your query and recommend the best matching recipes from the filtered set.
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from pydantic import BaseModel as PydanticBaseModel, Field
    from ..core.config import settings
    from sqlalchemy.orm import joinedload
    from ..models.recipe import Recipe
    from ..utils.cache import recommendation_cache
    import json
    
    # Generate cache key from request parameters
    cache_key = recommendation_cache._generate_key(
        query=request.query,
        max_results=request.max_results,
        search=request.search,
        cuisine=request.cuisine,
        difficulty=request.difficulty,
        min_time=request.min_time,
        max_time=request.max_time,
        ingredients=request.ingredients,
        created_by=request.created_by
    )
    
    # Check cache first
    cached_result = recommendation_cache.get(cache_key)
    if cached_result:
        # Return cached result with recipe objects from DB
        cached_ids = cached_result.get("recipe_ids", [])
        cached_explanation = cached_result.get("explanation", "")
        
        # Fetch fresh recipe data (in case recipes were updated)
        recipes = db.query(Recipe).options(joinedload(Recipe.creator)).filter(
            Recipe.id.in_(cached_ids),
            Recipe.is_public == True
        ).all()
        
        if recipes:
            return RecipeRecommendationResponse(
                recommendations=recipes,
                explanation=f"{cached_explanation} (cached)",
                query=request.query
            )
    
    # Get all available recipes
    query = db.query(Recipe).options(joinedload(Recipe.creator)).filter(Recipe.is_public == True)
    
    # Apply filters (same as recipe search)
    if request.search:
        search_term = f"%{request.search}%"
        query = query.filter(
            (Recipe.title.ilike(search_term)) |
            (Recipe.description.ilike(search_term)) |
            (Recipe.ingredients.ilike(search_term))
        )
    
    if request.cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{request.cuisine}%"))
    
    if request.difficulty:
        query = query.filter(Recipe.difficulty.ilike(f"%{request.difficulty}%"))
    
    if request.min_time is not None:
        query = query.filter(Recipe.total_time >= request.min_time)
    
    if request.max_time is not None:
        query = query.filter(Recipe.total_time <= request.max_time)
    
    if request.ingredients:
        ingredients_term = f"%{request.ingredients}%"
        query = query.filter(Recipe.ingredients.ilike(ingredients_term))
    
    if request.created_by:
        query = query.filter(Recipe.created_by == request.created_by)
    
    all_recipes = query.limit(50).all()  # Limit to 50 for performance
    
    if not all_recipes:
        return RecipeRecommendationResponse(
            recommendations=[],
            explanation="No recipes found matching your criteria.",
            query=request.query
        )
    
    # Prepare recipe data for LLM
    recipes_context = []
    for recipe in all_recipes:
        recipes_context.append({
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description or "",
            "cuisine": recipe.cuisine or "Unknown",
            "difficulty": recipe.difficulty or "Unknown",
            "total_time": recipe.total_time or 0,
            "ingredients": recipe.ingredients[:200]  # Truncate for token limit
        })
    
    # Define output schema for LangChain
    class LLMRecommendation(PydanticBaseModel):
        recommended_recipe_ids: list[int] = Field(description="List of recommended recipe IDs")
        explanation: str = Field(description="Explanation of why these recipes were chosen")
    
    try:
        # Initialize LangChain components
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        
        parser = PydanticOutputParser(pydantic_object=LLMRecommendation)
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful cooking assistant. Your job is to recommend recipes based on user queries.
You will receive a list of available recipes and a user query.
Analyze the query and select the most relevant recipes (up to {max_results}).
Consider: ingredients, cuisine type, difficulty, cooking time, and user preferences.

{format_instructions}"""),
            ("user", """User query: "{query}"
Max results: {max_results}

Available recipes:
{recipes_json}

Select the best matching recipes and explain your choices.""")
        ])
        
        # Create chain
        chain = prompt | llm | parser
        
        # Execute chain
        result = chain.invoke({
            "query": request.query,
            "max_results": request.max_results,
            "recipes_json": json.dumps(recipes_context, indent=2),
            "format_instructions": parser.get_format_instructions()
        })
        
        # Get full recipe objects
        recommended_recipes = [r for r in all_recipes if r.id in result.recommended_recipe_ids]
        
        # Cache the result (store only IDs and explanation)
        recommendation_cache.set(cache_key, {
            "recipe_ids": result.recommended_recipe_ids,
            "explanation": result.explanation
        })
        
        return RecipeRecommendationResponse(
            recommendations=recommended_recipes[:request.max_results],
            explanation=result.explanation,
            query=request.query
        )
        
    except Exception as e:
        # Fallback: simple keyword matching
        query_lower = request.query.lower()
        scored_recipes = []
        
        for recipe in all_recipes:
            score = 0
            # Simple keyword matching
            searchable_text = f"{recipe.title} {recipe.description} {recipe.ingredients} {recipe.cuisine}".lower()
            
            for word in query_lower.split():
                if word in searchable_text:
                    score += 1
            
            if score > 0:
                scored_recipes.append((recipe, score))
        
        # Sort by score and get top results
        scored_recipes.sort(key=lambda x: x[1], reverse=True)
        recommended = [r[0] for r in scored_recipes[:request.max_results]]
        
        return RecipeRecommendationResponse(
            recommendations=recommended,
            explanation=f"Showing recipes matching keywords from your query. (Fallback mode active)",
            query=request.query
        )


@router.post("/", response_model=RecipeOut)
def create(payload: RecipeCreate, db: SessionDep, current_user: CurrentUser):
    """
    Create a new recipe.
    
    Set is_public=True to share with everyone, or is_public=False to keep it private.
    """
    recipe = create_recipe(
        db,
        title=payload.title,
        description=payload.description,
        cuisine=payload.cuisine,
        difficulty=payload.difficulty,
        total_time=payload.total_time,
        ingredients=payload.ingredients,
        image_url=payload.image_url,
        is_public=payload.is_public,
        steps=payload.steps,
        user_id=current_user.id,
    )
    return recipe


@router.get("/", response_model=PaginatedResponse[RecipeOut])
def list_all(
    db: SessionDep,
    current_user: OptionalCurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    List all public recipes with pagination.
    Includes saved status and save count for each recipe.
    """
    params = PaginationParams(page=page, page_size=page_size)
    user_id = current_user.id if current_user else None
    return list_enriched_recipes(db, params, user_id)


@router.get("/search", response_model=PaginatedResponse[RecipeOut])
def search(
    db: SessionDep,
    current_user: OptionalCurrentUser,
    search: Optional[str] = Query(None, description="Search in title, description, ingredients"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (Easy, Medium, Hard)"),
    min_time: Optional[int] = Query(None, ge=0, description="Minimum cooking time in minutes"),
    max_time: Optional[int] = Query(None, ge=0, description="Maximum cooking time in minutes"),
    ingredients: Optional[str] = Query(None, description="Search for specific ingredients"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    include_private: bool = Query(False, description="Include your private recipes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """
    Search and filter recipes with advanced options.
    Includes saved status and save count for each recipe.
    
    - **search**: Search in title, description, and ingredients
    - **cuisine**: Filter by cuisine type (e.g., "Italian", "Burmese")
    - **difficulty**: Filter by difficulty level
    - **min_time/max_time**: Filter by cooking time range
    - **ingredients**: Search for specific ingredients
    - **created_by**: Show recipes from a specific user
    - **include_private**: Include your own private recipes (requires authentication)
    
    Only public recipes are shown by default. Private recipes are only visible to their creators.
    """
    filters = RecipeSearchFilter(
        search=search,
        cuisine=cuisine,
        difficulty=difficulty,
        min_time=min_time,
        max_time=max_time,
        ingredients=ingredients,
        created_by=created_by,
        include_private=include_private
    )
    
    params = PaginationParams(page=page, page_size=page_size)
    user_id = current_user.id if current_user else None
    
    return search_enriched_recipes(db, filters, user_id, params)


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_one(recipe_id: int, db: SessionDep, current_user: OptionalCurrentUser):
    """
    Get a specific recipe by ID.
    Includes saved status and save count.
    """
    user_id = current_user.id if current_user else None
    return get_enriched_recipe(db, recipe_id, user_id)


@router.put("/{recipe_id}", response_model=RecipeOut)
def update(recipe_id: int, payload: RecipeUpdate, db: SessionDep, current_user: CurrentUser):
    return update_recipe(
        db,
        recipe_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        cuisine=payload.cuisine,
        difficulty=payload.difficulty,
        total_time=payload.total_time,
        ingredients=payload.ingredients,
        image_url=payload.image_url,
        steps=payload.steps,
    )


@router.post("/{recipe_id}/upload-image", response_model=RecipeOut)
async def upload_recipe_image(
    recipe_id: int,
    db: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    """
    Upload an image for a recipe.
    
    Accepts:
    - Image types: JPEG, PNG, WebP, GIF
    - Max size: 10MB
    
    Returns:
    - Updated recipe with new image_url
    """
    # Verify recipe exists and user owns it
    recipe = get_recipe(db, recipe_id)
    if recipe.created_by != current_user.id:
        from ..exceptions import UnauthorizedException
        raise UnauthorizedException("You are not allowed to modify this recipe")
    
    # Upload to Supabase Storage
    image_url = storage_service.upload_recipe_image(file, recipe_id)
    
    # Update recipe with new image URL
    return update_recipe(
        db,
        recipe_id,
        user_id=current_user.id,
        image_url=image_url
    )


@router.post("/{recipe_id}/steps/{step_number}/upload-media", response_model=RecipeOut)
async def upload_step_media(
    recipe_id: int,
    step_number: int,
    db: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    """
    Upload media (image/video) for a cooking step.
    
    Accepts:
    - Image types: JPEG, PNG, WebP, GIF
    - Video types: MP4, WebM, QuickTime
    - Max size: 10MB for images, 50MB for videos
    
    Returns:
    - Updated recipe with step media_url
    """
    # Verify recipe exists and user owns it
    recipe = get_recipe(db, recipe_id)
    if recipe.created_by != current_user.id:
        from ..exceptions import UnauthorizedException
        raise UnauthorizedException("You are not allowed to modify this recipe")
    
    # Upload to Supabase Storage
    media_url = storage_service.upload_cooking_step_media(file, recipe_id, step_number)
    
    # Update the specific cooking step
    from ..models.recipe import CookingStep
    step = db.query(CookingStep).filter(
        CookingStep.recipe_id == recipe_id,
        CookingStep.step_number == step_number
    ).first()
    
    if not step:
        from ..exceptions import NotFoundException
        raise NotFoundException(f"Step {step_number} not found for recipe {recipe_id}")
    
    step.media_url = media_url
    db.commit()
    db.refresh(recipe)
    
    return recipe


@router.delete("/{recipe_id}")
def delete(recipe_id: int, db: SessionDep, current_user: CurrentUser):
    delete_recipe(db, recipe_id, user_id=current_user.id)
    return {"detail": "Deleted"}
