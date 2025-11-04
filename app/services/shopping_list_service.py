"""
Shopping List Service
Handles shopping list creation and smart generation from recipes
"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict
from fastapi import HTTPException, status
import re

from ..models import ShoppingList, ShoppingListItem, Recipe, RecipeCollection, CollectionItem
from ..schemas.shopping_list import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListItemCreate,
    GenerateShoppingListRequest
)


def categorize_ingredient(ingredient: str) -> str:
    """Auto-categorize ingredient based on keywords"""
    ingredient_lower = ingredient.lower()
    
    categories = {
        "Produce": ["lettuce", "tomato", "onion", "garlic", "potato", "carrot", "celery", 
                   "pepper", "cucumber", "spinach", "kale", "broccoli", "cauliflower", 
                   "apple", "banana", "orange", "lemon", "lime", "strawberry", "mushroom",
                   "cabbage", "zucchini", "eggplant", "squash", "pumpkin", "ginger", "avocado"],
        "Meat": ["chicken", "beef", "pork", "lamb", "turkey", "bacon", "sausage", 
                "ground meat", "steak", "ribs", "ham"],
        "Seafood": ["fish", "salmon", "tuna", "shrimp", "crab", "lobster", "oyster", 
                   "clam", "squid", "prawn", "cod", "tilapia"],
        "Dairy": ["milk", "cheese", "butter", "cream", "yogurt", "sour cream", "ice cream",
                 "cottage cheese", "cheddar", "mozzarella", "parmesan"],
        "Pantry": ["flour", "sugar", "salt", "pepper", "oil", "vinegar", "sauce", "pasta",
                  "rice", "beans", "lentils", "quinoa", "oats", "cereal", "noodles"],
        "Bakery": ["bread", "baguette", "roll", "bagel", "tortilla", "pita", "croissant"],
        "Frozen": ["frozen", "ice"],
        "Beverages": ["juice", "soda", "water", "wine", "beer", "coffee", "tea"],
        "Condiments": ["ketchup", "mustard", "mayonnaise", "hot sauce", "soy sauce", 
                      "worcestershire", "pickle", "relish"],
        "Spices": ["cinnamon", "cumin", "paprika", "oregano", "basil", "thyme", 
                  "rosemary", "chili", "curry", "turmeric"],
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in ingredient_lower:
                return category
    
    return "Other"


def parse_ingredient_quantity(ingredient_text: str) -> tuple[str, Optional[str]]:
    """
    Parse ingredient text to extract quantity and name
    Example: "2 cups rice" -> ("rice", "2 cups")
    """
    # Pattern: number + unit + ingredient
    pattern = r'^([\d/.\s]+(?:cup|cups|tbsp|tsp|oz|lb|kg|g|ml|l|tablespoon|teaspoon|pound)?s?)\s+(.+)$'
    match = re.match(pattern, ingredient_text.strip(), re.IGNORECASE)
    
    if match:
        quantity = match.group(1).strip()
        ingredient = match.group(2).strip()
        return (ingredient, quantity)
    
    return (ingredient_text.strip(), None)


def merge_shopping_items(items: List[Dict]) -> List[Dict]:
    """
    Merge similar ingredients (simple version)
    In production, you'd use AI for smart merging
    """
    merged = {}
    
    for item in items:
        ingredient_lower = item['ingredient'].lower()
        
        # Simple merge: exact match or very similar
        found = False
        for key in list(merged.keys()):
            if ingredient_lower == key or \
               ingredient_lower in key or \
               key in ingredient_lower:
                # Merge - combine quantities if possible
                existing = merged[key]
                if item.get('quantity') and existing.get('quantity'):
                    existing['notes'] = f"From multiple recipes: {existing.get('quantity')}, {item.get('quantity')}"
                else:
                    existing['quantity'] = item.get('quantity') or existing.get('quantity')
                
                # Combine source recipes
                existing.setdefault('source_recipes', [])
                if item.get('source_recipe_id'):
                    existing['source_recipes'].append(item['source_recipe_id'])
                
                found = True
                break
        
        if not found:
            merged[ingredient_lower] = item.copy()
            merged[ingredient_lower].setdefault('source_recipes', [])
            if item.get('source_recipe_id'):
                merged[ingredient_lower]['source_recipes'].append(item['source_recipe_id'])
    
    return list(merged.values())


def create_shopping_list(db: Session, user_id: int, list_data: ShoppingListCreate) -> ShoppingList:
    """Create a new shopping list manually"""
    shopping_list = ShoppingList(
        user_id=user_id,
        name=list_data.name,
        description=list_data.description,
        is_completed=list_data.is_completed
    )
    db.add(shopping_list)
    db.flush()
    
    # Add items
    for item_data in list_data.items:
        item = ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient=item_data.ingredient,
            quantity=item_data.quantity,
            category=item_data.category or categorize_ingredient(item_data.ingredient),
            is_checked=item_data.is_checked,
            notes=item_data.notes,
            source_recipe_id=item_data.source_recipe_id
        )
        db.add(item)
    
    db.commit()
    db.refresh(shopping_list)
    return shopping_list


def generate_shopping_list_from_recipes(
    db: Session,
    user_id: int,
    request_data: GenerateShoppingListRequest
) -> ShoppingList:
    """
    Generate shopping list from recipes or collection
    Smart merging and categorization
    """
    items_to_add = []
    
    # Get recipes
    if request_data.recipe_ids:
        recipes = db.query(Recipe).filter(Recipe.id.in_(request_data.recipe_ids)).all()
    elif request_data.collection_id:
        collection = db.query(RecipeCollection)\
            .options(joinedload(RecipeCollection.items).joinedload(CollectionItem.recipe))\
            .filter(
                RecipeCollection.id == request_data.collection_id,
                RecipeCollection.user_id == user_id
            )\
            .first()
        
        if not collection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
        
        recipes = [item.recipe for item in collection.items]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide recipe_ids or collection_id")
    
    # Extract ingredients from recipes
    for recipe in recipes:
        # Parse ingredients (simple split by comma or newline)
        ingredient_lines = re.split(r'[,\n]', recipe.ingredients)
        
        for line in ingredient_lines:
            line = line.strip()
            if not line:
                continue
            
            ingredient_name, quantity = parse_ingredient_quantity(line)
            
            items_to_add.append({
                'ingredient': ingredient_name,
                'quantity': quantity,
                'category': categorize_ingredient(ingredient_name),
                'source_recipe_id': recipe.id,
                'is_checked': False
            })
    
    # Merge similar items
    merged_items = merge_shopping_items(items_to_add)
    
    # Create shopping list
    shopping_list = ShoppingList(
        user_id=user_id,
        name=request_data.list_name,
        description=f"Generated from {len(recipes)} recipe(s)",
        is_completed=False
    )
    db.add(shopping_list)
    db.flush()
    
    # Add merged items
    for item_data in merged_items:
        item = ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient=item_data['ingredient'],
            quantity=item_data.get('quantity'),
            category=item_data['category'],
            is_checked=item_data['is_checked'],
            notes=item_data.get('notes'),
            source_recipe_id=item_data.get('source_recipe_id')
        )
        db.add(item)
    
    db.commit()
    db.refresh(shopping_list)
    return shopping_list


def get_user_shopping_lists(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ShoppingList]:
    """Get all shopping lists for a user"""
    return db.query(ShoppingList)\
        .filter(ShoppingList.user_id == user_id)\
        .options(joinedload(ShoppingList.items))\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_shopping_list_by_id(db: Session, list_id: int, user_id: int) -> Optional[ShoppingList]:
    """Get shopping list by ID"""
    return db.query(ShoppingList)\
        .options(joinedload(ShoppingList.items))\
        .filter(ShoppingList.id == list_id, ShoppingList.user_id == user_id)\
        .first()


def update_shopping_list(
    db: Session,
    list_id: int,
    user_id: int,
    update_data: ShoppingListUpdate
) -> Optional[ShoppingList]:
    """Update shopping list"""
    shopping_list = db.query(ShoppingList)\
        .filter(ShoppingList.id == list_id, ShoppingList.user_id == user_id)\
        .first()
    
    if not shopping_list:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(shopping_list, key, value)
    
    db.commit()
    db.refresh(shopping_list)
    return shopping_list


def update_shopping_list_item(
    db: Session,
    item_id: int,
    user_id: int,
    is_checked: Optional[bool] = None
) -> Optional[ShoppingListItem]:
    """Update shopping list item (toggle checked)"""
    item = db.query(ShoppingListItem)\
        .join(ShoppingList)\
        .filter(
            ShoppingListItem.id == item_id,
            ShoppingList.user_id == user_id
        )\
        .first()
    
    if not item:
        return None
    
    if is_checked is not None:
        item.is_checked = is_checked
    
    db.commit()
    db.refresh(item)
    return item


def delete_shopping_list(db: Session, list_id: int, user_id: int) -> bool:
    """Delete shopping list"""
    shopping_list = db.query(ShoppingList)\
        .filter(ShoppingList.id == list_id, ShoppingList.user_id == user_id)\
        .first()
    
    if not shopping_list:
        return False
    
    db.delete(shopping_list)
    db.commit()
    return True
