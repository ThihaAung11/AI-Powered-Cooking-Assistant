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
    
    # Detect greetings
    is_greeting = any(word in user_input for word in [
        "hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"
    ]) and len(user_input.split()) <= 5
    
    # Detect specific intents
    needs_image_search = any(word in user_input for word in [
        "show", "image", "picture", "photo", "video", "how does", "what does", "look like"
    ])
    
    needs_health_info = any(word in user_input for word in [
        "health", "nutrition", "calorie", "vitamin", "protein", "carb", "fat",
        "benefit", "nutrient", "healthy", "diet plan", "meal plan"
    ])
    
    needs_recipe = any(word in user_input for word in [
        "recipe", "recommend", "suggest", "what should i cook", "what can i make"
    ])
    
    needs_cooking_guide = any(word in user_input for word in [
        "how to cook", "guide me", "step", "cooking guide", "start cooking", "help me cook"
    ])
    
    state["is_greeting"] = is_greeting
    state["needs_image_search"] = needs_image_search
    state["needs_health_info"] = needs_health_info
    state["needs_recipe"] = needs_recipe
    state["needs_cooking_guide"] = needs_cooking_guide
    
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


def node_greeting_response(state: dict) -> dict:
    """Handle greetings with a brief, helpful response"""
    context = state["user_context"]
    language = state.get("language", "en")
    
    if language == "my":
        greeting = f"""မင်္ဂလာပါ {context['name']}! 

ကျွန်ုပ်သည် ချက်ပြုတ်ရေးအကူအညီပေးသော AI ဖြစ်ပါသည်။ အောက်ပါအရာများကို ကူညီပေးနိုင်ပါတယ်:

• **ကျန်းမာရေးနှင့် အာဟာရ** - အာဟာရဆိုင်ရာ အကြံဉာဏ်များ
• **စားသောက်ကုန်အစီအစဉ်** - နေ့စဉ်/အပတ်စဉ် အစီအစဉ်များ
• **ချက်နည်းများ အကြံပြုချက်** - သင့်အတွက် သင့်လျော်သော ချက်နည်းများ
• **ချက်ပြုတ်ခြင်း အကူအညီ** - အဆင့်ဆင့် လမ်းညွှန်ချက်များ

ဘာကူညီပေးရမလဲ ပြောပြပါ! 😊"""
    else:
        greeting = f"""Hello {context['name']}! 👋

I'm your cooking assistant. I can help you with:

• **Health & Nutrition** - Nutritional advice and dietary guidance
• **Meal Planning** - Daily or weekly meal plans
• **Recipe Recommendations** - Personalized recipe suggestions
• **Cooking Guidance** - Step-by-step cooking instructions

What would you like to do today?"""
    
    state["ai_reply"] = greeting
    return state


def node_simple_response(state: dict) -> dict:
    """Provide a simple conversational response for general queries"""
    user_input = state["user_input"]
    context = state["user_context"]
    language = state.get("language", "en")
    
    llm = get_llm()
    
    if language == "my":
        system_msg = """သင်သည် ချက်ပြုတ်ရေးအကူအညီပေးသော AI ဖြစ်သည်။ 
တိုတောင်းပြီး အသုံးဝင်သော အဖြေများပေးပါ။ အသုံးပြုသူက တိတိကျကျ မတောင်းဆိုပါက အလိုအလျောက် လုပ်ဆောင်မပေးပါနဲ့။"""
        prompt = f"""အသုံးပြုသူက: "{user_input}"

တိုတောင်းစွာ ဖြေကြားပြီး ဆက်လုပ်ဆောင်ရန် မေးမြန်းပါ။ (၂-၃ စာကြောင်း)"""
    else:
        system_msg = """You are a friendly cooking assistant. Keep responses brief (2-3 sentences) unless user asks for details. 
Never perform actions automatically - always ask first. Focus on being helpful and conversational."""
        prompt = f"""User said: "{user_input}"

User preferences: {context['diet']} diet, {context['spice_level']} spice, likes {context['cuisine']} cuisine.

Provide a brief, helpful response (2-3 sentences max). Ask what they'd like to do next."""
    
    messages = [
        SystemMessage(content=system_msg),
        HumanMessage(content=prompt)
    ]
    
    result = llm.invoke(messages)
    state["ai_reply"] = result.content
    return state


def node_recommend_recipe(state: dict) -> dict:
    """Use LLM to recommend a recipe based on user input"""
    recipes = state.get("recipes", [])
    context = state["user_context"]
    user_input = state["user_input"]
    language = state.get("language", "english")
    health_info = state.get("health_info")
    
    llm = get_llm()
    
    if language == "burmese":
        system_msg = """သင်သည် ချက်ပြုတ်ရေးအကူအညီပေးသော AI ဖြစ်သည်။ တိုတောင်းပြီး အသုံးဝင်သော ချက်နည်းများကို အကြံပြုပါ။"""
        lang_instruction = "မြန်မာဘာသာဖြင့် ဖြေကြားပါ။"
    else:
        system_msg = """You are a friendly cooking assistant. Recommend 2-3 recipes briefly. Keep it concise."""
        lang_instruction = "Respond in English."

    recipe_text = "\n".join([
        f"- Recipe ID {r['id']}: {r['title']} ({r['cuisine']}, {r['difficulty']}, {r['total_time']} mins)"
        for r in recipes[:5]  # Limit to 5 recipes
    ]) if recipes else "No recipes available matching your preferences."
    
    prompt = f"""{lang_instruction}

User asked: "{user_input}"

User preferences: {context['diet']} diet, {context['spice_level']} spice, likes {context['cuisine']} cuisine.

Available recipes:
{recipe_text}

Recommend 2-3 recipes briefly. Ask if they want cooking guidance for any recipe."""
    
    if health_info:
        prompt += f"\n\nHealth info:\n{health_info}"
    
    messages = [
        SystemMessage(content=system_msg),
        HumanMessage(content=prompt)
    ]
    
    result = llm.invoke(messages)
    state["ai_reply"] = result.content
    return state


def node_cooking_guide(state: dict, db: Session) -> dict:
    """Provide step-by-step cooking guidance only when explicitly requested"""
    user_input = state["user_input"].lower()
    language = state.get("language", "en")
    
    # Extract recipe ID from user input if mentioned
    match = re.search(r"[Rr]ecipe\s*ID[:\s]*(\d+)", user_input)
    recipe_id = int(match.group(1)) if match else None

    recipe = None
    if recipe_id:
        recipe = db.query(Recipe).filter_by(id=recipe_id).first()
    
    if not recipe:
        if language == "my":
            state["ai_reply"] = "ချက်နည်း ID ကို ပြောပြပေးပါ။ ဥပမာ: 'Recipe ID 5 ကို ချက်ပြုတ်ပေးပါ'"
        else:
            state["ai_reply"] = "Please specify which recipe you'd like to cook. Say 'Recipe ID [number]' or ask me to recommend recipes first."
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
        guide_prompt = f"""မြန်မာဘာသာဖြင့် တိုတောင်းစွာ ပြန်ကြားပါ။

"{recipe.title}" ချက်ပြုတ်နည်း:
{step_text}

စတင်ရန် ပထမ ၂-၃ အဆင့်ကို ရှင်းပြပြီး 'ဆက်လုပ်မလား' ဟု မေးပါ။"""
    else:
        guide_prompt = f"""Recipe: "{recipe.title}"

Steps:
{step_text}

Briefly explain the first 2-3 steps to get started. Then ask if they're ready to continue. Keep it short."""
    
    guide = llm.invoke([HumanMessage(content=guide_prompt)])
    
    state["ai_reply"] = guide.content
    state["cooking_recipe"] = recipe.title
    return state


def route_after_intent(state: dict) -> str:
    """Route to appropriate node based on detected intent"""
    if state.get("is_greeting"):
        return "greeting_response"
    elif state.get("needs_cooking_guide"):
        return "cooking_guide"
    elif state.get("needs_recipe"):
        return "recipe_list"
    elif state.get("needs_health_info"):
        return "health_nutrition"
    else:
        return "simple_response"


def build_cooking_chat_graph(db: Session):
    """Build and compile the LangGraph workflow with conditional routing"""
    workflow = StateGraph(dict)
    
    # Add all nodes
    workflow.add_node("user_context", lambda s: node_user_context(s, db))
    workflow.add_node("analyze_intent", node_analyze_intent)
    workflow.add_node("greeting_response", node_greeting_response)
    workflow.add_node("simple_response", node_simple_response)
    workflow.add_node("health_nutrition", node_health_nutrition)
    workflow.add_node("recipe_list", lambda s: node_recipe_list(s, db))
    workflow.add_node("recommend_recipe", node_recommend_recipe)
    workflow.add_node("cooking_guide", lambda s: node_cooking_guide(s, db))

    # Set up workflow with conditional routing
    workflow.set_entry_point("user_context")
    workflow.add_edge("user_context", "analyze_intent")
    
    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "analyze_intent",
        route_after_intent,
        {
            "greeting_response": "greeting_response",
            "simple_response": "simple_response",
            "health_nutrition": "health_nutrition",
            "recipe_list": "recipe_list",
            "cooking_guide": "cooking_guide"
        }
    )
    
    # End paths
    workflow.add_edge("greeting_response", END)
    workflow.add_edge("simple_response", END)
    workflow.add_edge("cooking_guide", END)
    
    # Health info flows to simple response
    workflow.add_edge("health_nutrition", "simple_response")
    
    # Recipe flow: list -> recommend -> end
    workflow.add_edge("recipe_list", "recommend_recipe")
    workflow.add_edge("recommend_recipe", END)
    
    return workflow.compile()


def chat_with_cooking_assistant(user_id: int, user_message: str, db: Session) -> dict:
    """
    Orchestrates LangGraph flow and stores chat message in DB.
    Uses conditional routing to provide brief, targeted responses.
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
            "language": result.get("language", "en")
        }
        
        # Add optional fields
        if cooking_recipe:
            response["cooking_recipe"] = cooking_recipe
        if health_info:
            response["health_nutrition"] = health_info
        
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
