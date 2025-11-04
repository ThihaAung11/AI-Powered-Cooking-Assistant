# New Features Implementation Guide 🚀

**Features Added:**
1. ✅ Recipe Collections & Meal Planning
2. ✅ Smart Shopping List Generator
3. ✅ Enhanced Functionality

---

## 🎯 Features Overview

### 1. Recipe Collections
- Create custom recipe collections ("Quick Dinners", "Healthy Lunches")
- Organize recipes for meal planning
- Assign recipes to days/meals (Monday Breakfast, Tuesday Dinner)
- Add personal notes per recipe
- Public/private collections

### 2. Smart Shopping Lists
- **Manual Creation**: Create shopping lists from scratch
- **Auto-Generation**: Generate from recipes or collections
- **Smart Merging**: Combines similar ingredients automatically
- **Auto-Categorization**: Groups items by category (Produce, Dairy, Meat)
- **Check-off Items**: Track purchased items

---

## 📦 Database Setup

### Step 1: Stop Your Server
```bash
# Press Ctrl+C to stop if running
```

### Step 2: Backup Database (Optional but Recommended)
```bash
cp app.db app.db.backup
```

### Step 3: Run Database Migration

Since you're using `Base.metadata.create_all()`, the tables will be created automatically:

```bash
# Start the server - tables will be created
uv run uvicorn app.main:app --reload
```

**The new tables will be created:**
- `recipe_collections`
- `collection_items`
- `shopping_lists`
- `shopping_list_items`

---

## 🧪 Testing the Features

### Access API Documentation
```
Open: http://localhost:8000/docs
```

### Get Your Auth Token
1. Register or login via `/auth/login`
2. Copy the `access_token`
3. Click "Authorize" button in Swagger UI
4. Paste: `Bearer YOUR_TOKEN`

---

## 📋 Feature 1: Recipe Collections

### Create a Collection
```bash
POST /collections/

{
  "name": "Weekly Meal Plan",
  "description": "My meals for this week",
  "collection_type": "meal_plan",
  "is_public": false
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Weekly Meal Plan",
  "description": "My meals for this week",
  "collection_type": "meal_plan",
  "is_public": false,
  "items": [],
  "created_at": "2025-11-04T...",
  "updated_at": "2025-11-04T..."
}
```

### Get Your Collections
```bash
GET /collections/
```

### Add Recipe to Collection
```bash
POST /collections/1/recipes

{
  "recipe_id": 5,
  "order": 1,
  "day_of_week": "Monday",
  "meal_type": "dinner",
  "notes": "Prep night before",
  "servings": 4
}
```

### Remove Recipe from Collection
```bash
DELETE /collections/1/recipes/5
```

### Update Collection Item (Meal Planning)
```bash
PUT /collections/1/items/1

{
  "day_of_week": "Tuesday",
  "meal_type": "lunch",
  "notes": "Make extra for leftovers"
}
```

### Delete Collection
```bash
DELETE /collections/1
```

---

## 🛒 Feature 2: Shopping Lists

### Generate Shopping List from Recipes
```bash
POST /shopping-lists/generate

{
  "recipe_ids": [1, 2, 3],
  "list_name": "Weekend Grocery Run"
}
```

**What happens:**
- ✅ Extracts ingredients from all 3 recipes
- ✅ Merges similar ingredients ("2 onions" + "1 onion" = note about multiple)
- ✅ Auto-categorizes (Produce, Dairy, Meat, etc.)
- ✅ Creates organized shopping list

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Weekend Grocery Run",
  "description": "Generated from 3 recipe(s)",
  "is_completed": false,
  "items": [
    {
      "id": 1,
      "ingredient": "chicken breast",
      "quantity": "500g",
      "category": "Meat",
      "is_checked": false,
      "source_recipe_id": 1
    },
    {
      "id": 2,
      "ingredient": "onion",
      "quantity": "2 cups",
      "category": "Produce",
      "is_checked": false
    }
  ]
}
```

### Generate from Collection
```bash
POST /shopping-lists/generate

{
  "collection_id": 1,
  "list_name": "Weekly Shopping List"
}
```

### Create Manual Shopping List
```bash
POST /shopping-lists/

{
  "name": "Quick Shopping",
  "description": "Things I need",
  "is_completed": false,
  "items": [
    {
      "ingredient": "milk",
      "quantity": "1 gallon",
      "category": "Dairy"
    },
    {
      "ingredient": "bread",
      "quantity": "1 loaf",
      "category": "Bakery"
    }
  ]
}
```

### Get Your Shopping Lists
```bash
GET /shopping-lists/
```

### Get Specific Shopping List
```bash
GET /shopping-lists/1
```

### Toggle Item Checked
```bash
PATCH /shopping-lists/items/1?is_checked=true
```

### Update Shopping List
```bash
PUT /shopping-lists/1

{
  "name": "Updated Name",
  "is_completed": true
}
```

### Delete Shopping List
```bash
DELETE /shopping-lists/1
```

---

## 💡 Example Workflows

### Workflow 1: Weekly Meal Planning
```bash
# 1. Create meal plan collection
POST /collections/
{
  "name": "Week of Nov 4",
  "collection_type": "meal_plan"
}

# 2. Add recipes for each day
POST /collections/1/recipes
{
  "recipe_id": 10,
  "day_of_week": "Monday",
  "meal_type": "dinner"
}

POST /collections/1/recipes
{
  "recipe_id": 15,
  "day_of_week": "Tuesday",
  "meal_type": "dinner"
}

# 3. Generate shopping list from meal plan
POST /shopping-lists/generate
{
  "collection_id": 1,
  "list_name": "Week of Nov 4 - Groceries"
}

# 4. Check off items as you shop
PATCH /shopping-lists/items/1?is_checked=true
PATCH /shopping-lists/items/2?is_checked=true
```

### Workflow 2: Quick Dinner Ideas Collection
```bash
# 1. Create favorites collection
POST /collections/
{
  "name": "Quick Dinners (< 30 mins)",
  "collection_type": "favorites"
}

# 2. Add your go-to quick recipes
POST /collections/2/recipes
{
  "recipe_id": 5,
  "order": 1,
  "notes": "Family favorite!"
}

# 3. Later: Generate shopping list for 2-3 quick dinners
POST /shopping-lists/generate
{
  "recipe_ids": [5, 7, 12],
  "list_name": "Quick Dinners This Week"
}
```

---

## 🧩 Integration with Existing Features

### Combine with Recommendations
```bash
# 1. Get personalized recommendations
GET /recommendations/

# 2. Save good ones to collection
POST /collections/1/recipes
{
  "recipe_id": <recommended_recipe_id>
}
```

### Combine with Cooking Sessions
```bash
# 1. Start cooking from collection item
POST /cooking-sessions/
{
  "recipe_id": 5
}

# 2. Track which meals from collection you've cooked
```

---

## 🎨 Frontend Implementation Ideas

### Collections UI
```
📋 My Collections
┌─────────────────────────────────┐
│ 🗓️ Weekly Meal Plan (7 recipes) │
│ ⚡ Quick Dinners (12 recipes)   │
│ 💚 Healthy Options (8 recipes)  │
│                                  │
│ [+ New Collection]               │
└─────────────────────────────────┘

Collection Detail: "Weekly Meal Plan"
┌──────────────────────────────────────┐
│ Monday                               │
│  🍳 Breakfast: Oatmeal               │
│  🥗 Lunch: Chicken Salad             │
│  🍝 Dinner: Pasta Bolognese          │
│                                      │
│ Tuesday                              │
│  🍳 Breakfast: [Add Recipe]          │
│  🥗 Lunch: [Add Recipe]              │
│  🍝 Dinner: Thai Curry ✏️ 🗑️         │
│                                      │
│ [Generate Shopping List] 📝          │
└──────────────────────────────────────┘
```

### Shopping List UI
```
🛒 Shopping List: Weekend Groceries

Produce ✓✓✗
☑ Tomatoes (4)
☑ Onions (2)
☐ Garlic (1 bulb)

Meat ✗✗
☐ Chicken breast (500g)
☐ Ground beef (1 lb)

Dairy ✓
☑ Milk (1 gallon)

[Export] [Print] [Mark All Done]
```

---

## 📊 Database Schema

### recipe_collections
```sql
id INTEGER PRIMARY KEY
user_id INTEGER FOREIGN KEY
name VARCHAR
description VARCHAR
collection_type VARCHAR (meal_plan/favorites/custom)
is_public BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
```

### collection_items
```sql
id INTEGER PRIMARY KEY
collection_id INTEGER FOREIGN KEY
recipe_id INTEGER FOREIGN KEY
order INTEGER
day_of_week VARCHAR (Monday, Tuesday, ...)
meal_type VARCHAR (breakfast, lunch, dinner, snack)
notes VARCHAR
servings INTEGER
created_at TIMESTAMP
updated_at TIMESTAMP
```

### shopping_lists
```sql
id INTEGER PRIMARY KEY
user_id INTEGER FOREIGN KEY
name VARCHAR
description VARCHAR
is_completed BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
```

### shopping_list_items
```sql
id INTEGER PRIMARY KEY
shopping_list_id INTEGER FOREIGN KEY
ingredient VARCHAR
quantity VARCHAR
category VARCHAR (Produce, Dairy, Meat, ...)
is_checked BOOLEAN
notes VARCHAR
source_recipe_id INTEGER FOREIGN KEY (nullable)
created_at TIMESTAMP
updated_at TIMESTAMP
```

---

## 🐛 Troubleshooting

### Error: "Collection not found"
- Check that you own the collection
- Verify collection_id is correct
- Ensure you're authenticated

### Error: "Recipe already in collection"
- Recipe can only be added once to each collection
- Remove it first, then re-add with different metadata

### Shopping list missing ingredients
- Check recipe `ingredients` field format
- Ingredients should be comma or newline separated
- Example: "2 cups flour, 1 egg, 500g chicken"

### Tables not created
```bash
# Stop server, delete database, restart
rm app.db
uv run uvicorn app.main:app --reload
```

---

## ✅ Testing Checklist

### Collections
- [ ] Create collection
- [ ] Get all collections
- [ ] Get single collection
- [ ] Update collection
- [ ] Delete collection
- [ ] Add recipe to collection
- [ ] Remove recipe from collection
- [ ] Update collection item (meal planning)

### Shopping Lists
- [ ] Create manual shopping list
- [ ] Generate from recipes
- [ ] Generate from collection
- [ ] Get all shopping lists
- [ ] Get single shopping list
- [ ] Toggle item checked
- [ ] Update shopping list
- [ ] Delete shopping list

---

## 🚀 Next Steps

### For Academic Project:
1. **Test all endpoints** in Swagger UI
2. **Document with screenshots** for dissertation
3. **Create sample data** (5-10 recipes, 2-3 collections)
4. **User testing**: Ask participants to create meal plan
5. **Measure metrics**:
   - Time to create meal plan
   - Accuracy of shopping list generation
   - User satisfaction with categorization

### For Frontend:
1. **Collections page** with drag-drop interface
2. **Calendar view** for meal plans
3. **Shopping list** with checkboxes
4. **Print/export** shopping list feature
5. **Mobile-friendly** checklist

---

## 📝 API Documentation Updates

The new endpoints are automatically documented at:
- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Look for the new tags:
- `collections`
- `shopping-lists`

---

## 🎓 For Your Dissertation

### Key Points to Highlight:

**1. Algorithm Complexity**
- Smart ingredient merging
- Auto-categorization logic
- Meal planning organization

**2. User Benefits**
- Saves time (generate shopping list vs manual)
- Reduces waste (organized planning)
- Improves cooking workflow

**3. Technical Innovation**
- RESTful API design
- Database normalization
- Smart text parsing (ingredient extraction)

**4. User Testing Metrics to Collect**
- Time to create meal plan: Target < 5 mins
- Shopping list accuracy: Target 90%+
- Category correctness: Target 85%+
- User would use feature: Target 80%+

---

## 🎉 Success!

You've now implemented:
- ✅ Recipe Collections with meal planning
- ✅ Smart Shopping List Generator
- ✅ 11 new API endpoints
- ✅ 4 new database tables
- ✅ Smart ingredient categorization
- ✅ Ingredient merging algorithm

**Your app now has significantly more value for users!**

---

**Need help? Check:**
1. Swagger UI documentation
2. Error messages in terminal
3. Database integrity
4. Authentication token validity

**Happy coding! 🚀**
