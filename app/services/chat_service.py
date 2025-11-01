"""
Cooking Assistant Chat Service using LangGraph
"""
from typing import Optional, List, Dict
import re
import json
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from sqlalchemy.orm import Session
import httpx

from ..models import User, UserPreference, Recipe, CookingStep, Message
from ..core.config import settings


def get_llm():
    """Get configured ChatOpenAI instance"""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not configured in environment variables")
    
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )


def node_user_context(state: dict, db: Session) -> dict:
    """Fetch user context and preferences"""
    user_id = state["user_id"]
    user = db.query(User).filter_by(id=user_id).first()
    
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    prefs = db.query(UserPreference).filter_by(user_id=user_id).first()

    context = {
        "username": user.username,
        "name": user.name,
        "diet": prefs.diet_type if prefs else "omnivore",
        "spice_level": str(prefs.spice_level.value) if prefs and prefs.spice_level else "medium",
        "cuisine": prefs.preferred_cuisine if prefs else "Burmese",
        "language": prefs.language.value if prefs and prefs.language else "english",
    }
    state["user_context"] = context
    state["language"] = context["language"]
    return state


def node_recipe_list(state: dict, db: Session) -> dict:
    """Query recipes based on user preferences"""
    context = state["user_context"]
    query = db.query(Recipe)

    if context.get("diet") == "vegetarian":
        query = query.filter(Recipe.description.ilike("%vegetarian%"))
    
    if context.get("spice_level") == "low":
        query = query.filter(~Recipe.description.ilike("%spicy%"))
    
    if context.get("cuisine"):
        query = query.filter(Recipe.cuisine.ilike(f"%{context['cuisine']}%"))

    recipes = query.limit(10).all()
    recipe_list = [
        {
            "id": r.id,
            "title": r.title,
            "cuisine": r.cuisine or "Unknown",
            "difficulty": r.difficulty or "Medium",
            "total_time": r.total_time,
            "description": r.description[:120] if r.description else ""
        }
        for r in recipes
    ]
    state["recipes"] = recipe_list
    return state


def node_analyze_intent(state: dict) -> dict:
    """Analyze user intent to determine what type of response is needed"""
    user_input = state["user_input"].lower()
    
    # Detect intent
    needs_image_search = any(word in user_input for word in [
        "show", "image", "picture", "photo", "video", "how does", "what does", "look like"
    ])
    
    needs_health_info = any(word in user_input for word in [
        "health", "nutrition", "calorie", "vitamin", "protein", "carb", "fat",
        "benefit", "nutrient", "healthy", "diet", "allergy", "allergic"
    ])
    
    needs_recipe = any(word in user_input for word in [
        "recipe", "cook", "make", "prepare", "ingredient", "step"
    ])
    
    state["needs_image_search"] = needs_image_search
    state["needs_health_info"] = needs_health_info
    state["needs_recipe"] = needs_recipe
    
    return state


def node_search_images(state: dict) -> dict:
    """Search for cooking-related images and videos"""
    if not state.get("needs_image_search"):
        state["media_results"] = []
        return state
    
    user_input = state["user_input"]
    
    # Extract food/cooking terms from user input
    search_query = user_input
    
    # Use a simple approach: search for cooking images
    # In production, you'd use Google Custom Search API, Unsplash API, or similar
    media_results = [
        {
            "type": "image",
            "title": f"Visual guide for {search_query}",
            "description": "Search for images on Google Images or YouTube for visual demonstrations",
            "suggestion": f"Try searching: '{search_query} cooking tutorial' on YouTube"
        }
    ]
    
    state["media_results"] = media_results
    return state


def node_health_nutrition(state: dict) -> dict:
    """Provide health and nutrition information"""
    if not state.get("needs_health_info"):
        state["health_info"] = None
        return state
    
    user_input = state["user_input"]
    language = state.get("language", "english")
    
    llm = get_llm()
    
    if language == "burmese":
        health_prompt = f"""မြန်မာဘာသာဖြင့် ပြန်ကြားပါ။

အသုံးပြုသူ၏မေးခွန်း: "{user_input}"

ကျန်းမာရေးနှင့် အာဟာရဆိုင်ရာ အချက်အလက်များကို အသေးစိတ်ရှင်းပြပါ:
- အာဟာရတန်ဖိုး
- ကျန်းမာရေးအကျိုးကျေးဇူးများ
- အကြံပြုချက်များ
"""
    else:
        health_prompt = f"""User question: "{user_input}"

Provide detailed health and nutrition information including:
- Nutritional values (calories, protein, carbs, fats, vitamins, minerals)
- Health benefits
- Dietary considerations (allergies, restrictions)
- Recommendations for healthy cooking methods

Be specific and evidence-based.
"""
    
    result = llm.invoke([HumanMessage(content=health_prompt)])
    state["health_info"] = result.content
    
    return state


def node_recommend_recipe(state: dict) -> dict:
    """Use LLM to recommend a recipe based on user input"""
    recipes = state["recipes"]
    context = state["user_context"]
    user_input = state["user_input"]
    language = state.get("language", "english")
    health_info = state.get("health_info")
    media_results = state.get("media_results", [])
    
    llm = get_llm()
    
    if language == "burmese":
        system_msg = """သင်သည် ချက်ပြုတ်ရေးအကူအညီပေးသော AI လုပ်ဆောင်ချက်ဖြစ်သည်။ 
ကျန်းမာရေး၊ အာဟာရ၊ နှင့် ချက်ပြုတ်နည်းများကို ကျွမ်းကျင်စွာ ရှင်းပြနိုင်သည်။"""
        lang_instruction = "Please respond in Burmese (Myanmar) language."
    else:
        system_msg = """You are a friendly cooking assistant AI with expertise in:
- Recipe recommendations and cooking guidance
- Health and nutrition information
- Food safety and dietary considerations
- Visual cooking demonstrations

Provide helpful, accurate, and engaging responses."""
        lang_instruction = "Please respond in English."

    recipe_text = "\n".join([
        f"- Recipe ID {r['id']}: {r['title']} ({r['cuisine']}, {r['difficulty']}, {r['total_time']} mins)"
        for r in recipes
    ]) if recipes else "No recipes available."
    
    # Build comprehensive prompt
    prompt_parts = [lang_instruction, f"\nThe user asked: \"{user_input}\""]
    
    prompt_parts.append(f"""\nUser preferences:
- Diet: {context['diet']}
- Spice level: {context['spice_level']}
- Preferred cuisine: {context['cuisine']}""")
    
    if health_info:
        prompt_parts.append(f"\n\nHealth & Nutrition Information:\n{health_info}")
    
    if media_results:
        media_text = "\n".join([f"- {m['suggestion']}" for m in media_results])
        prompt_parts.append(f"\n\nVisual Resources:\n{media_text}")
    
    prompt_parts.append(f"\n\nAvailable recipes:\n{recipe_text}")
    prompt_parts.append("\n\nProvide a helpful response and ask what they want to do next.")
    
    prompt = "".join(prompt_parts)
    
    messages = [
        SystemMessage(content=system_msg),
        HumanMessage(content=prompt)
    ]
    
    result = llm.invoke(messages)
    state["ai_reply"] = result.content
    return state


def node_cooking_guide(state: dict, db: Session) -> dict:
    """Provide step-by-step cooking guidance"""
    reply = state.get("ai_reply", "")
    language = state.get("language", "en")
    
    match = re.search(r"[Rr]ecipe\s*ID[:\s]*(\d+)", reply)
    recipe_id = int(match.group(1)) if match else None

    recipe = None
    if recipe_id:
        recipe = db.query(Recipe).filter_by(id=recipe_id).first()

    if not recipe:
        recipe = db.query(Recipe).first()
    
    if not recipe:
        state["ai_reply"] += "\n\nNo recipes available in the database yet."
        return state

    steps = (
        db.query(CookingStep)
        .filter_by(recipe_id=recipe.id)
        .order_by(CookingStep.step_number)
        .all()
    )
    
    if steps:
        step_text = "\n".join([f"Step {s.step_number}: {s.instruction_text}" for s in steps])
    else:
        step_text = "No detailed steps available for this recipe yet."

    llm = get_llm()
    
    if language == "my":
        guide_prompt = f"""မြန်မာဘာသာဖြင့် ပြန်ကြားပါ။

အသုံးပြုသူသည် "{recipe.title}" ကို ချက်ပြုတ်နေပါသည်။

ချက်ပြုတ်နည်းများ:
{step_text}

ပထမအဆင့်များကို ရှင်းပြပါ။
"""
    else:
        guide_prompt = f"""The user is cooking "{recipe.title}".

Cooking steps:
{step_text}

Explain the first few steps in a friendly way.
"""
    
    guide = llm.invoke([HumanMessage(content=guide_prompt)])
    
    state["ai_reply"] += "\n\n" + guide.content
    state["cooking_recipe"] = recipe.title
    return state


def build_cooking_chat_graph(db: Session):
    """Build and compile the LangGraph workflow with enhanced capabilities"""
    workflow = StateGraph(dict)
    
    # Add all nodes
    workflow.add_node("user_context", lambda s: node_user_context(s, db))
    workflow.add_node("analyze_intent", node_analyze_intent)
    workflow.add_node("search_images", node_search_images)
    workflow.add_node("health_nutrition", node_health_nutrition)
    workflow.add_node("recipe_list", lambda s: node_recipe_list(s, db))
    workflow.add_node("recommend_recipe", node_recommend_recipe)
    workflow.add_node("cooking_guide", lambda s: node_cooking_guide(s, db))

    # Set up workflow
    workflow.set_entry_point("user_context")
    workflow.add_edge("user_context", "analyze_intent")
    workflow.add_edge("analyze_intent", "search_images")
    workflow.add_edge("search_images", "health_nutrition")
    workflow.add_edge("health_nutrition", "recipe_list")
    workflow.add_edge("recipe_list", "recommend_recipe")
    workflow.add_edge("recommend_recipe", "cooking_guide")
    workflow.add_edge("cooking_guide", END)
    
    return workflow.compile()


def chat_with_cooking_assistant(user_id: int, user_message: str, db: Session) -> dict:
    """
    Orchestrates LangGraph flow and stores chat message in DB.
    Enhanced with health/nutrition info and media search capabilities.
    """
    try:
        graph = build_cooking_chat_graph(db)
        result = graph.invoke({
            "user_id": user_id,
            "user_input": user_message
        })

        ai_reply = result.get("ai_reply", "I'm sorry, I couldn't process your request.")
        cooking_recipe = result.get("cooking_recipe")
        health_info = result.get("health_info")
        media_results = result.get("media_results", [])

        msg = Message(
            user_id=user_id,
            user_message=user_message,
            ai_reply=ai_reply
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)

        response = {
            "message_id": msg.id,
            "ai_reply": ai_reply,
            "cooking_recipe": cooking_recipe,
            "language": result.get("language", "en")
        }
        
        # Add health info if available
        if health_info:
            response["health_nutrition"] = health_info
        
        # Add media suggestions if available
        if media_results:
            response["media_suggestions"] = media_results
        
        return response
    
    except Exception as e:
        db.rollback()
        raise Exception(f"Chat processing failed: {str(e)}")


def get_chat_history(user_id: int, db: Session, limit: int = 20) -> list[dict]:
    """Retrieve chat history for a user"""
    messages = (
        db.query(Message)
        .filter_by(user_id=user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": msg.id,
            "user_message": msg.user_message,
            "ai_reply": msg.ai_reply,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        }
        for msg in reversed(messages)
    ]
