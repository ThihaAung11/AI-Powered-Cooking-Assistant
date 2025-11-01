from typing import List
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut
from ..utils.pagination import PaginationParams, PaginatedResponse
from ..services.recipe_service import create_recipe, get_recipe, list_recipes, update_recipe, delete_recipe
from ..services.storage_service import storage_service
from ..core.security import get_current_user
from ..models import User
from ..deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=RecipeOut)
def create(payload: RecipeCreate, db: SessionDep, current_user: CurrentUser):
    recipe = create_recipe(
        db,
        title=payload.title,
        description=payload.description,
        cuisine=payload.cuisine,
        difficulty=payload.difficulty,
        total_time=payload.total_time,
        ingredients=payload.ingredients,
        image_url=payload.image_url,
        steps=payload.steps,
        user_id=current_user.id,
    )
    return recipe


@router.get("/", response_model=PaginatedResponse[RecipeOut])
def list_all(
    db: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    params = PaginationParams(page=page, page_size=page_size)
    return list_recipes(db, params)


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_one(recipe_id: int, db: SessionDep):
    return get_recipe(db, recipe_id)


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
    file: UploadFile = File(...),
    db: SessionDep = None,
    current_user: CurrentUser = None
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
    file: UploadFile = File(...),
    db: SessionDep = None,
    current_user: CurrentUser = None
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
def delete(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_recipe(db, recipe_id, user_id=current_user.id)
    return {"detail": "Deleted"}
