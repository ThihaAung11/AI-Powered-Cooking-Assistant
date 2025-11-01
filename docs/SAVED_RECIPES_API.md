# Saved Recipes API Documentation

Manage user's saved/bookmarked recipes collection.

## Endpoints

### 1. Save Recipe
**POST** `/saved-recipes/`

Save a recipe to user's collection. Each user can only save a recipe once.

**Request Body:**
```json
{
  "recipe_id": 1
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `400` - Recipe is already saved
- `404` - Recipe not found
- `401` - Unauthorized

---

### 2. Unsave Recipe
**DELETE** `/saved-recipes/recipe/{recipe_id}`

Remove a recipe from user's saved collection.

**Path Parameters:**
- `recipe_id`: Recipe ID

**Response:** `204 No Content`

**Errors:**
- `404` - Saved recipe not found
- `401` - Unauthorized

---

### 3. Check if Recipe is Saved
**GET** `/saved-recipes/recipe/{recipe_id}/is-saved`

Check if a recipe is saved by the current user.

**Path Parameters:**
- `recipe_id`: Recipe ID

**Response:** `200 OK`
```json
{
  "is_saved": true
}
```

---

### 4. List My Saved Recipes
**GET** `/saved-recipes/my-saved-recipes?page=1&page_size=10&include_details=true`

List current user's saved recipes with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)
- `include_details` (optional): Include full recipe details (default: true)

**Response with details:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "recipe_id": 1,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "recipe": {
        "id": 1,
        "title": "Burmese Chicken Curry",
        "description": "Traditional Burmese curry",
        "cuisine": "Burmese",
        "difficulty": "Medium",
        "total_time": 60,
        "ingredients": "...",
        "image_url": "https://...",
        "created_by": 2,
        "steps": [...],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
      }
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10,
  "total_pages": 2,
  "has_next": true,
  "has_prev": false
}
```

**Response without details (include_details=false):**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "recipe_id": 1,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10,
  "total_pages": 2,
  "has_next": true,
  "has_prev": false
}
```

---

### 5. List Recipe Saves
**GET** `/saved-recipes/recipe/{recipe_id}/saves?page=1&page_size=10`

List all users who saved a specific recipe (useful for analytics).

**Path Parameters:**
- `recipe_id`: Recipe ID

**Query Parameters:**
- `page` (optional): Page number
- `page_size` (optional): Items per page

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "recipe_id": 1,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

**Errors:**
- `404` - Recipe not found

---

### 6. Get Recipe Save Count
**GET** `/saved-recipes/recipe/{recipe_id}/save-count`

Get the total number of times a recipe has been saved.

**Path Parameters:**
- `recipe_id`: Recipe ID

**Response:** `200 OK`
```json
{
  "recipe_id": 1,
  "save_count": 50
}
```

---

### 7. Get Saved Recipe by ID
**GET** `/saved-recipes/{saved_recipe_id}`

Get a specific saved recipe entry by its ID.

**Path Parameters:**
- `saved_recipe_id`: Saved recipe ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `404` - Saved recipe not found

---

### 8. Delete Saved Recipe
**DELETE** `/saved-recipes/{saved_recipe_id}`

Delete a saved recipe entry. Users can only delete their own saved recipes.

**Path Parameters:**
- `saved_recipe_id`: Saved recipe ID

**Response:** `204 No Content`

**Errors:**
- `401` - Unauthorized (not the owner)
- `404` - Saved recipe not found

---

## Data Models

### SavedRecipeCreate
```json
{
  "recipe_id": "integer (required)"
}
```

### SavedRecipeOut
```json
{
  "id": "integer",
  "user_id": "integer",
  "recipe_id": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### SavedRecipeWithDetails
```json
{
  "id": "integer",
  "user_id": "integer",
  "recipe_id": "integer",
  "created_at": "datetime",
  "updated_at": "datetime",
  "recipe": {
    // Full RecipeOut object
  }
}
```

---

## Business Rules

1. **Unique Saves**: Each user can only save a recipe once
2. **Ownership**: Users can only delete their own saved recipes
3. **Cascade Delete**: Saved recipes are deleted when the user or recipe is deleted
4. **Public Stats**: Anyone can view save counts and lists (useful for popularity metrics)
5. **Efficient Loading**: Use `include_details=false` for faster loading when full recipe data isn't needed

---

## Example Usage

### Save a Recipe
```bash
curl -X POST "http://localhost:8000/saved-recipes/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipe_id": 1}'
```

### Unsave a Recipe
```bash
curl -X DELETE "http://localhost:8000/saved-recipes/recipe/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check if Saved
```bash
curl -X GET "http://localhost:8000/saved-recipes/recipe/1/is-saved" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List My Saved Recipes with Full Details
```bash
curl -X GET "http://localhost:8000/saved-recipes/my-saved-recipes?include_details=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Recipe Popularity
```bash
curl -X GET "http://localhost:8000/saved-recipes/recipe/1/save-count"
```

---

## Use Cases

### 1. User's Recipe Collection
Users can build their personal cookbook by saving favorite recipes.

### 2. Recipe Popularity Metrics
Track which recipes are most popular by save count.

### 3. Quick Access
Saved recipes provide quick access to frequently used recipes.

### 4. Personalized Recommendations
Use saved recipes to understand user preferences for recommendations.

### 5. Social Features
See how many users saved a recipe (social proof).
