from datasets import recipes
from typing import List
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.models.recipe import Recipe, CookingStep
from app.core.config import settings
from app.database import SessionLocal

session = SessionLocal()

# 🧠 Create the LLM agent
llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0.3, openai_api_key=settings.OPENAI_API_KEY)

# 🧾 Prompt to structure instructions
prompt = ChatPromptTemplate.from_template("""
You are an expert Burmese recipe writer.
Given the following raw cooking instructions, break them into clear, numbered cooking steps.
Each step should be short, actionable, and in Burmese.

Return only JSON in the format:
[
  dict("step_number": 1, "instruction_text": "..."),
  dict("step_number": 2, "instruction_text": "..."),
]

Raw Instructions:
{raw_text}
""")

def extract_cooking_steps(raw_text: str) -> List[dict]:
    """Use LLM to transform raw text into structured step JSON."""
    chain = prompt | llm
    response = chain.invoke({"raw_text": raw_text})
    try:
        steps = json.loads(response.content)
    except Exception:
        steps = [{"step_number": 1, "instruction_text": raw_text.strip()}]
    return steps

def transform_dataset_to_models(data: dict, user_id: int):
    """Transform dataset with AI-generated cooking steps."""
    recipe = Recipe(
        title=data.get("Name"),
        description=None,
        cuisine=None,
        difficulty=None,
        total_time=None,
        ingredients=data.get("Ingredients"),
        image_url=None,
        created_by=user_id
    )

    # 🧠 Generate cooking steps using the AI agent
    structured_steps = extract_cooking_steps(data.get("CookingInstructions", ""))

    steps = [
        CookingStep(
            step_number=step["step_number"],
            instruction_text=step["instruction_text"],
            media_url=None
        )
        for step in structured_steps
    ]

    recipe.steps = steps
    return recipe

for data in recipes:
    recipe_obj = transform_dataset_to_models(data, user_id=2)
    print(recipe_obj)
    session.add(recipe_obj)
    session.commit()  
session.close() 