# API Overview

Complete overview of all available API endpoints in the AI-Powered Cooking Assistant.

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require authentication using JWT Bearer tokens:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## API Modules

### 1. Authentication (`/auth`)
User registration, login, and token management.

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info

📖 [View Auth Documentation](#)

---

### 2. User Preferences (`/preferences`)
Manage user cooking preferences for personalized experience.

- `GET /preferences/me` - Get my preferences (auto-creates if not exists)
- `POST /preferences/` - Create preferences
- `PUT /preferences/` - Update preferences
- `DELETE /preferences/` - Delete preferences (reset to defaults)
- `GET /preferences/options` - Get available preference options

**Features:**
- ✅ Language preference (English/Burmese)
- ✅ Dietary restrictions
- ✅ Cooking skill level
- ✅ Cuisine preferences
- ✅ Spice level
- ✅ Allergy tracking

📖 [View User Preferences Documentation](./USER_PREFERENCES_API.md)

---

### 3. Recipes (`/recipes`)
Create, read, update, and delete recipes with cooking steps.

- `POST /recipes/` - Create recipe
- `GET /recipes/` - List recipes (paginated)
- `GET /recipes/{id}` - Get recipe details
- `PUT /recipes/{id}` - Update recipe
- `DELETE /recipes/{id}` - Delete recipe

**Features:**
- ✅ Pagination support
- ✅ Structured cooking steps
- ✅ Multiple metadata fields (cuisine, difficulty, time, image)
- ✅ User ownership validation

📖 [View Recipes Documentation](#)

---

### 4. Feedbacks (`/feedbacks`)
User ratings and reviews for recipes.

- `POST /feedbacks/` - Create feedback
- `GET /feedbacks/my-feedbacks` - List my feedbacks
- `GET /feedbacks/recipe/{recipe_id}` - List recipe feedbacks
- `GET /feedbacks/recipe/{recipe_id}/stats` - Get rating statistics
- `GET /feedbacks/recipe/{recipe_id}/my-feedback` - Get my feedback for recipe
- `GET /feedbacks/{id}` - Get feedback details
- `PUT /feedbacks/{id}` - Update feedback
- `DELETE /feedbacks/{id}` - Delete feedback

**Features:**
- ✅ Rating 1-5 with comments
- ✅ One feedback per user per recipe
- ✅ Aggregate statistics (avg, min, max)
- ✅ Pagination support

📖 [View Feedbacks Documentation](./FEEDBACK_API.md)

---

### 5. Cooking Sessions (`/cooking-sessions`)
Track cooking sessions and user activity.

- `POST /cooking-sessions/` - Start session
- `POST /cooking-sessions/{id}/end` - End session
- `GET /cooking-sessions/active` - Get active session
- `GET /cooking-sessions/my-sessions` - List my sessions
- `GET /cooking-sessions/my-stats` - Get my cooking stats
- `GET /cooking-sessions/recipe/{recipe_id}` - List recipe sessions
- `GET /cooking-sessions/{id}` - Get session details
- `DELETE /cooking-sessions/{id}` - Delete session

**Features:**
- ✅ One active session per user
- ✅ Auto duration calculation
- ✅ Comprehensive statistics
- ✅ Optional recipe association

📖 [View Cooking Sessions Documentation](./COOKING_SESSIONS_API.md)

---

### 6. Saved Recipes (`/saved-recipes`)
User's bookmarked/saved recipes collection.

- `POST /saved-recipes/` - Save recipe
- `DELETE /saved-recipes/recipe/{recipe_id}` - Unsave recipe
- `GET /saved-recipes/recipe/{recipe_id}/is-saved` - Check if saved
- `GET /saved-recipes/my-saved-recipes` - List my saved recipes
- `GET /saved-recipes/recipe/{recipe_id}/saves` - List recipe saves
- `GET /saved-recipes/recipe/{recipe_id}/save-count` - Get save count
- `GET /saved-recipes/{id}` - Get saved recipe details
- `DELETE /saved-recipes/{id}` - Delete saved recipe

**Features:**
- ✅ One save per user per recipe
- ✅ Optional full recipe details
- ✅ Popularity metrics
- ✅ Pagination support

📖 [View Saved Recipes Documentation](./SAVED_RECIPES_API.md)

---

### 7. Recommendations (`/recommendations`)
Intelligent recipe recommendations based on user preferences and behavior.

- `GET /recommendations/for-me` - Get personalized recommendations
- `GET /recommendations/trending` - Get trending recipes
- `GET /recommendations/similar/{recipe_id}` - Get similar recipes
- `GET /recommendations/summary` - Get recommendation summary

**Features:**
- ✅ Personalized scoring algorithm
- ✅ Multi-factor recommendations
- ✅ Trending recipes
- ✅ Similar recipe discovery
- ✅ Filter by cuisine, difficulty, time

📖 [View Recommendations Documentation](./RECOMMENDATIONS_API.md)

---

### 8. Chat (`/chat`)
AI-powered cooking assistant chat interface.

- `POST /chat/` - Send message to AI assistant
- `GET /chat/history` - Get chat history

📖 [View Chat Documentation](#)

---

## Common Features

### Pagination
Most list endpoints support pagination with these query parameters:
- `page` (default: 1, min: 1)
- `page_size` (default: 10, min: 1, max: 100)

**Response Format:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10,
  "has_next": true,
  "has_prev": false
}
```

### Error Responses
All errors follow a consistent format:
```json
{
  "status_code": 404,
  "detail": "Resource not found",
  "timestamp": "2024-01-01T12:00:00Z",
  "path": "/recipes/999"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## Data Relationships

```
User
├── recipes (created)
├── feedbacks
├── cooking_sessions
└── saved_recipes

Recipe
├── creator (User)
├── steps (CookingStep[])
├── feedbacks (UserFeedback[])
├── saved_by (UserSavedRecipe[])
└── sessions (UserCookingSession[])

CookingStep
└── recipe (Recipe)

UserFeedback
├── user (User)
└── recipe (Recipe)

UserCookingSession
├── user (User)
└── recipe (Recipe, optional)

UserSavedRecipe
├── user (User)
└── recipe (Recipe)
```

---

## Quick Start Examples

### 1. Register and Login
```bash
# Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "securepass123"
  }'
```

### 2. Create Recipe
```bash
curl -X POST "http://localhost:8000/recipes/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Burmese Chicken Curry",
    "description": "Traditional curry",
    "cuisine": "Burmese",
    "difficulty": "Medium",
    "total_time": 60,
    "ingredients": "Chicken, onions, garlic...",
    "steps": [
      {"step_number": 1, "instruction_text": "Prepare ingredients"},
      {"step_number": 2, "instruction_text": "Cook chicken"}
    ]
  }'
```

### 3. Start Cooking Session
```bash
curl -X POST "http://localhost:8000/cooking-sessions/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipe_id": 1}'
```

### 4. Save Recipe
```bash
curl -X POST "http://localhost:8000/saved-recipes/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipe_id": 1}'
```

### 5. Leave Feedback
```bash
curl -X POST "http://localhost:8000/feedbacks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": 1,
    "rating": 5,
    "comment": "Delicious!"
  }'
```

---

## Development Tools

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check
```bash
curl http://localhost:8000/health
```

---

## Best Practices

1. **Always use pagination** for list endpoints to avoid performance issues
2. **Check `is_saved` status** before attempting to save/unsave recipes
3. **End cooking sessions** when done to get accurate statistics
4. **Use `include_details=false`** when you don't need full recipe data
5. **Handle 401 errors** by refreshing tokens or re-authenticating
6. **Validate input** on the client side to reduce 422 errors

---

## Rate Limiting
Currently no rate limiting is implemented. Consider implementing rate limiting in production.

---

## Support
For issues or questions, please refer to the individual API documentation files or contact the development team.
