"""
Cooking Assistant Chat Service using LangGraph
"""
from typing import Optional
import re
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session

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


def node_recommend_recipe(state: dict) -> dict:
    """Use LLM to recommend a recipe based on user input"""
    recipes = state["recipes"]
    context = state["user_context"]
    user_input = state["user_input"]
    language = state.get("language", "english")
    
    llm = get_llm()
    
    if language == "burmese":
        system_msg = "သင်သည် ချက်ပြုတ်ရေးအကူအညီပေးသော AI လုပ်ဆောင်ချက်ဖြစ်သည်။"
        lang_instruction = "Please respond in Burmese (Myanmar) language."
    else:
        system_msg = "You are a friendly cooking assistant AI that can answer user questions and provide cooking guidance."
        lang_instruction = "Please respond in English."

    recipe_text = "\n".join([
        f"- Recipe ID {r['id']}: {r['title']} ({r['cuisine']}, {r['difficulty']}, {r['total_time']} mins)"
        for r in recipes
    ]) if recipes else "No recipes available."

    prompt = f"""{lang_instruction}

The user asked: "{user_input}"

User preferences:
- Diet: {context['diet']}
- Spice level: {context['spice_level']}
- Preferred cuisine: {context['cuisine']}

Available recipes:
{recipe_text}

Ask user what they want to do next.
"""
    
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
    """Build and compile the LangGraph workflow"""
    workflow = StateGraph(dict)
    
    workflow.add_node("user_context", lambda s: node_user_context(s, db))
    workflow.add_node("recipe_list", lambda s: node_recipe_list(s, db))
    workflow.add_node("recommend_recipe", node_recommend_recipe)
    workflow.add_node("cooking_guide", lambda s: node_cooking_guide(s, db))

    workflow.set_entry_point("user_context")
    workflow.add_edge("user_context", "recipe_list")
    workflow.add_edge("recipe_list", "recommend_recipe")
    workflow.add_edge("recommend_recipe", "cooking_guide")
    workflow.add_edge("cooking_guide", END)
    
    return workflow.compile()


def chat_with_cooking_assistant(user_id: int, user_message: str, db: Session) -> dict:
    """
    Orchestrates LangGraph flow and stores chat message in DB.
    """
    try:
        graph = build_cooking_chat_graph(db)
        result = graph.invoke({
            "user_id": user_id,
            "user_input": user_message
        })

        ai_reply = result.get("ai_reply", "I'm sorry, I couldn't process your request.")
        cooking_recipe = result.get("cooking_recipe")

        msg = Message(
            user_id=user_id,
            user_message=user_message,
            ai_reply=ai_reply
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)

        return {
            "message_id": msg.id,
            "ai_reply": ai_reply,
            "cooking_recipe": cooking_recipe,
            "language": result.get("language", "en")
        }
    
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
