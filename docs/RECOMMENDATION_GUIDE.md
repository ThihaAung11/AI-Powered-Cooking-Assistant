# Recipe Recommendation System - Quick Guide

## How It Works

The recommendation system automatically analyzes your preferences and behavior to suggest recipes you'll love.

## What Influences Your Recommendations?

### 1. Your Preferences (Set in Profile)
```
✓ Preferred Cuisine (e.g., Burmese, Thai, Italian)
✓ Cooking Skill Level (Beginner, Intermediate, Advanced)
✓ Diet Type (Vegetarian, Vegan, Pescatarian, etc.)
✓ Spice Level (Low, Medium, High)
```

### 2. Your Activity
```
✓ Recipes you've saved
✓ Recipes you've cooked
✓ Recipes you've rated highly (4-5 stars)
✓ Time spent cooking
```

### 3. Community Signals
```
✓ Highly-rated recipes (4+ stars average)
✓ Trending recipes (recently popular)
✓ Frequently saved recipes
```

## Recommendation Types

### 🎯 For You (Personalized)
**Endpoint:** `GET /recommendations/for-me`

Best for: Daily recipe discovery based on your unique taste

**What it considers:**
- Your cuisine preferences
- Your skill level
- Your dietary restrictions
- Recipes you haven't tried yet
- Quick recipes (if you prefer them)

**Example:**
```bash
# Get 10 personalized recommendations
GET /recommendations/for-me?limit=10

# Get easy recipes under 30 minutes
GET /recommendations/for-me?difficulty=Easy&max_time=30
```

---

### 🔥 Trending
**Endpoint:** `GET /recommendations/trending`

Best for: Discovering what's popular right now

**What it considers:**
- Recent saves (last 7 days)
- Recent cooking sessions
- Community activity

**Example:**
```bash
# Get trending recipes from last week
GET /recommendations/trending?days=7&limit=10

# Get trending recipes from last 30 days
GET /recommendations/trending?days=30&limit=20
```

---

### 🔍 Similar Recipes
**Endpoint:** `GET /recommendations/similar/{recipe_id}`

Best for: Finding alternatives to a recipe you like

**What it considers:**
- Same cuisine
- Same difficulty
- Similar cooking time

**Example:**
```bash
# Find 5 recipes similar to recipe #1
GET /recommendations/similar/1?limit=5
```

---

## Understanding Recommendation Scores

Scores range from 0-100, with higher scores meaning better matches.

### Score Breakdown

| Factor | Points | Description |
|--------|--------|-------------|
| Base Score | 50 | Starting point for all recipes |
| Cuisine Match | +20 | Recipe matches your preferred cuisine |
| Skill Match | +15 | Difficulty matches your skill level |
| Diet Match | +15 | Recipe matches your diet type |
| Highly Rated | +10 | Recipe has 4+ star average rating |
| New Recipe | +5 | You haven't saved or cooked this before |
| Quick Recipe | +5 | Recipe takes ≤60 minutes |
| Already Saved | -5 | You've already saved this recipe |
| Already Cooked | -3 per time | You've cooked this before |

### Example Score Calculation

**Your Profile:**
- Preferred Cuisine: Burmese
- Skill: Intermediate
- Diet: Vegetarian

**Recipe: Burmese Tea Leaf Salad**
- Cuisine: Burmese ✓
- Difficulty: Medium ✓
- Time: 20 minutes ✓
- Vegetarian: Yes ✓
- Average Rating: 4.5 stars ✓
- You haven't tried it ✓

**Score:**
```
50 (base) + 20 (cuisine) + 15 (skill) + 15 (diet) 
+ 10 (highly rated) + 5 (quick) + 5 (new) = 120
→ Capped at 100
```

---

## Tips for Better Recommendations

### 1. Complete Your Profile
Set your preferences in your user profile:
- Preferred cuisine
- Cooking skill level
- Diet type
- Spice level

### 2. Engage with Recipes
The more you interact, the better recommendations get:
- ⭐ Rate recipes you've tried
- 💾 Save recipes you want to try
- 👨‍🍳 Track cooking sessions
- 💬 Leave feedback

### 3. Use Filters
Narrow down recommendations for specific needs:
```bash
# Quick weeknight dinners
GET /recommendations/for-me?max_time=30

# Easy recipes for beginners
GET /recommendations/for-me?difficulty=Easy

# Specific cuisine
GET /recommendations/for-me?cuisine=Thai
```

### 4. Check Your Summary
See what factors influence your recommendations:
```bash
GET /recommendations/summary
```

---

## Common Use Cases

### Daily Meal Planning
```bash
# Morning: Get personalized recommendations
GET /recommendations/for-me?limit=5

# Filter by time available
GET /recommendations/for-me?max_time=45
```

### Discovering New Cuisines
```bash
# Try a different cuisine
GET /recommendations/for-me?cuisine=Thai&limit=10
```

### Finding Quick Meals
```bash
# Recipes under 30 minutes
GET /recommendations/for-me?max_time=30&limit=10
```

### Learning to Cook
```bash
# Start with easy recipes
GET /recommendations/for-me?difficulty=Easy&limit=10
```

### Exploring Trending Recipes
```bash
# See what's popular this week
GET /recommendations/trending?days=7
```

### Finding Recipe Variations
```bash
# After viewing a recipe you like
GET /recommendations/similar/123
```

---

## Recommendation Reasons

Each recommendation includes reasons explaining why it was suggested:

```json
{
  "recipe": {...},
  "score": 85,
  "reasons": [
    "Matches your preferred cuisine: Burmese",
    "Matches your skill level: Medium",
    "Highly rated by other users",
    "Quick to make (45 mins)",
    "New recipe to try"
  ]
}
```

Use these reasons to understand why recipes are recommended and make informed choices.

---

## Privacy & Data

### What We Track
- Your saved recipes
- Your cooking sessions
- Your ratings and feedback
- Your preferences

### What We Don't Track
- Specific ingredients you search for
- Time of day you cook
- Location data

### Data Usage
All data is used solely to improve your personal recommendations. We don't share your cooking data with third parties.

---

## Troubleshooting

### Not Getting Good Recommendations?

**Problem:** Recommendations don't match my taste
**Solution:** 
1. Update your preferences in your profile
2. Rate more recipes (helps us learn your taste)
3. Save recipes you're interested in

**Problem:** Too many recipes I've already tried
**Solution:**
- System automatically reduces scores for cooked recipes
- Try using filters to discover new cuisines
- Check trending recipes for fresh ideas

**Problem:** Recommendations are too difficult/easy
**Solution:**
- Update your cooking skill level in preferences
- Use difficulty filter: `?difficulty=Easy` or `?difficulty=Hard`

**Problem:** No vegetarian/vegan options
**Solution:**
- Set diet type in your preferences
- System will prioritize matching recipes
- Note: Requires recipes to be properly tagged

---

## API Response Examples

### Personalized Recommendations
```json
{
  "recommendations": [
    {
      "recipe": {
        "id": 1,
        "title": "Burmese Chicken Curry",
        "cuisine": "Burmese",
        "difficulty": "Medium",
        "total_time": 60
      },
      "score": 85.0,
      "reasons": [
        "Matches your preferred cuisine: Burmese",
        "Matches your skill level: Medium"
      ]
    }
  ],
  "total_count": 10,
  "filters_applied": {
    "cuisine": null,
    "difficulty": null,
    "max_time": null
  }
}
```

### Recommendation Summary
```json
{
  "total_recipes": 150,
  "saved_recipes": 12,
  "cooked_recipes": 8,
  "highly_rated_recipes": 5,
  "preferred_cuisine": "Burmese",
  "matching_cuisine_count": 45,
  "cooking_skill": "intermediate",
  "diet_type": "vegetarian"
}
```

---

## Need Help?

- Check the [full API documentation](./RECOMMENDATIONS_API.md)
- Review the [API overview](./API_OVERVIEW.md)
- Contact support for assistance
