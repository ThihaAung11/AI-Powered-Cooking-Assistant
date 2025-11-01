# Recipe Recommendations API Documentation

Intelligent recipe recommendation system based on user preferences, cooking history, and behavior.

## Overview

The recommendation system uses multiple factors to suggest recipes:
- **User Preferences**: Cuisine, diet type, cooking skill, spice level
- **Cooking History**: Previously cooked recipes
- **Saved Recipes**: User's saved collection
- **User Ratings**: Recipes the user has rated highly
- **Recipe Popularity**: Globally highly-rated recipes
- **Novelty**: New recipes the user hasn't tried

## Endpoints

### 1. Get Personalized Recommendations
**GET** `/recommendations/for-me`

Get personalized recipe recommendations based on your preferences and history.

**Query Parameters:**
- `limit` (optional): Number of recommendations (default: 10, min: 1, max: 50)
- `cuisine` (optional): Filter by specific cuisine
- `difficulty` (optional): Filter by difficulty (Easy, Medium, Hard)
- `max_time` (optional): Maximum cooking time in minutes

**Response:** `200 OK`
```json
{
  "recommendations": [
    {
      "recipe": {
        "id": 1,
        "title": "Burmese Chicken Curry",
        "description": "Traditional curry",
        "cuisine": "Burmese",
        "difficulty": "Medium",
        "total_time": 60,
        "ingredients": "...",
        "image_url": "https://...",
        "created_by": 2,
        "steps": [...],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
      },
      "score": 85.0,
      "reasons": [
        "Matches your preferred cuisine: Burmese",
        "Matches your skill level: Medium",
        "Highly rated by other users",
        "Quick to make (60 mins)"
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

**Scoring System:**
- Base score: 50 points
- Cuisine match: +20 points
- Skill level match: +15 points
- Diet type match: +15 points
- Highly rated: +10 points
- New recipe: +5 points
- Quick recipe (≤60 mins): +5 points
- Already saved: -5 points
- Already cooked: -3 points per time

---

### 2. Get Trending Recipes
**GET** `/recommendations/trending?limit=10&days=7`

Get trending recipes based on recent community activity.

**Query Parameters:**
- `limit` (optional): Number of recipes (default: 10, min: 1, max: 50)
- `days` (optional): Number of days to look back (default: 7, min: 1, max: 30)

**Response:** `200 OK`
```json
{
  "recipes": [
    {
      "id": 5,
      "title": "Mohinga",
      "description": "Traditional Burmese fish noodle soup",
      "cuisine": "Burmese",
      "difficulty": "Medium",
      "total_time": 90,
      "ingredients": "...",
      "image_url": "https://...",
      "created_by": 1,
      "steps": [...],
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total_count": 10,
  "period_days": 7
}
```

**Trending Calculation:**
- Based on recent saves + recent cooking sessions
- Activity within the specified time period
- Sorted by total activity count

---

### 3. Get Similar Recipes
**GET** `/recommendations/similar/{recipe_id}?limit=5`

Get recipes similar to a specific recipe.

**Path Parameters:**
- `recipe_id`: Recipe ID to find similar recipes for

**Query Parameters:**
- `limit` (optional): Number of similar recipes (default: 5, min: 1, max: 20)

**Response:** `200 OK`
```json
{
  "recipes": [
    {
      "id": 3,
      "title": "Thai Green Curry",
      "description": "Spicy Thai curry",
      "cuisine": "Thai",
      "difficulty": "Medium",
      "total_time": 55,
      "ingredients": "...",
      "image_url": "https://...",
      "created_by": 2,
      "steps": [...],
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total_count": 5,
  "reference_recipe_id": 1
}
```

**Similarity Factors:**
- Same cuisine
- Same difficulty level
- Similar cooking time (±15 minutes)

**Errors:**
- `404` - Recipe not found

---

### 4. Get Recommendation Summary
**GET** `/recommendations/summary`

Get a summary of recommendation factors for the current user.

**Response:** `200 OK`
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

**Fields:**
- `total_recipes`: Total recipes in the database
- `saved_recipes`: Number of recipes saved by user
- `cooked_recipes`: Number of unique recipes cooked by user
- `highly_rated_recipes`: Number of recipes user rated 4+ stars
- `preferred_cuisine`: User's preferred cuisine
- `matching_cuisine_count`: Recipes matching user's cuisine preference
- `cooking_skill`: User's cooking skill level
- `diet_type`: User's dietary preference

---

## Recommendation Algorithm

### Factors Considered

1. **User Preferences (from UserPreference model)**
   - Preferred cuisine
   - Cooking skill level
   - Diet type (vegetarian, vegan, etc.)
   - Spice level preference

2. **User Activity**
   - Saved recipes (indicates interest)
   - Cooking history (recipes already tried)
   - Ratings (recipes liked/disliked)

3. **Recipe Attributes**
   - Cuisine type
   - Difficulty level
   - Cooking time
   - Ingredients

4. **Social Signals**
   - Global ratings (popular recipes)
   - Recent activity (trending recipes)
   - Save count (popularity)

### Score Calculation Example

For a Burmese Medium difficulty recipe (60 mins):

**User Profile:**
- Preferred cuisine: Burmese
- Skill level: Intermediate
- Diet: Vegetarian

**Score Breakdown:**
```
Base score:              50
+ Cuisine match:         20  (Burmese = Burmese)
+ Skill match:           15  (Medium = Intermediate)
+ Diet match:            15  (Recipe is vegetarian)
+ Highly rated:          10  (Avg rating 4.5)
+ Quick recipe:           5  (60 mins ≤ 60)
+ New recipe:             5  (Not saved/cooked before)
─────────────────────────────
Total score:            120 → capped at 100
```

---

## Example Usage

### Get Personalized Recommendations
```bash
curl -X GET "http://localhost:8000/recommendations/for-me?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Quick Recipes (Under 30 Minutes)
```bash
curl -X GET "http://localhost:8000/recommendations/for-me?max_time=30&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Easy Recipes for Beginners
```bash
curl -X GET "http://localhost:8000/recommendations/for-me?difficulty=Easy&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Trending Recipes (Last 7 Days)
```bash
curl -X GET "http://localhost:8000/recommendations/trending?days=7&limit=10"
```

### Get Similar Recipes
```bash
curl -X GET "http://localhost:8000/recommendations/similar/1?limit=5"
```

### Get Recommendation Summary
```bash
curl -X GET "http://localhost:8000/recommendations/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Best Practices

1. **Set User Preferences**: Ensure users complete their preferences for better recommendations
2. **Regular Updates**: Recommendations improve as users save, cook, and rate recipes
3. **Filter Wisely**: Use filters to narrow down recommendations for specific needs
4. **Check Summary**: Use the summary endpoint to understand recommendation factors
5. **Explore Trending**: Discover what the community is cooking

---

## Integration Tips

### Frontend Display
```javascript
// Fetch personalized recommendations
const response = await fetch('/recommendations/for-me?limit=10', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Display with scores and reasons
data.recommendations.forEach(rec => {
  console.log(`${rec.recipe.title} - Score: ${rec.score}`);
  console.log('Reasons:', rec.reasons.join(', '));
});
```

### Recommendation Sections
Create different sections in your UI:
- "For You" - `/recommendations/for-me`
- "Trending Now" - `/recommendations/trending`
- "Similar Recipes" - `/recommendations/similar/{id}` (on recipe detail page)
- "Quick Meals" - `/recommendations/for-me?max_time=30`
- "Easy Recipes" - `/recommendations/for-me?difficulty=Easy`

---

## Future Enhancements

Potential improvements to the recommendation system:
- Machine learning-based collaborative filtering
- Ingredient-based similarity
- Seasonal recommendations
- Time-of-day recommendations (breakfast, lunch, dinner)
- Weather-based suggestions
- Nutritional preferences
- Advanced dietary restrictions (allergies, intolerances)

---

## Performance Notes

- Recommendations are calculated in real-time
- Scoring algorithm is optimized for speed
- Consider caching recommendations for high-traffic scenarios
- Trending recipes query is optimized with database indexes
