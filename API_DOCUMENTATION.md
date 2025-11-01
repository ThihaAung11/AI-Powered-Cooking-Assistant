# AI-Powered Cooking Assistant - API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://ai-powered-cooking-assistant.onrender.com
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Table of Contents
1. [Authentication](#authentication-endpoints)
2. [User Management](#user-management)
3. [Recipes](#recipes)
4. [Cooking Sessions](#cooking-sessions)
5. [Saved Recipes](#saved-recipes)
6. [Feedback & Reviews](#feedback--reviews)
7. [User Preferences](#user-preferences)
8. [Chat Assistant](#chat-assistant)
9. [Recommendations](#recommendations)
10. [File Uploads](#file-uploads)

---

## 🔐 Authentication Endpoints

### Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}

Response: 201 Created
{
  "id": 1,
  "username": "john_doe",
  "name": "John Doe",
  "email": "john@example.com",
  "is_active": true,
  "role_id": 2
}
```

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=securepassword123

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 👤 User Management

### Get Current User Profile
```http
GET /users/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "username": "john_doe",
  "name": "John Doe",
  "email": "john@example.com",
  "profile_url": "https://supabase.co/storage/v1/object/public/general/avatars/user_1_uuid.jpg",
  "is_active": true,
  "role_id": 2,
  "total_recipes": 5,
  "total_saved_recipes": 10,
  "total_cooking_sessions": 3,
  "total_feedbacks": 2
}
```

### Update User Profile
```http
PUT /users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Updated",
  "email": "newemail@example.com",
  "username": "john_updated",
  "profile_url": "https://example.com/new-avatar.jpg"
}

Response: 200 OK (Updated UserProfile)
```

### Upload Profile Image
```http
POST /users/me/upload-profile-image
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_file>

Response: 200 OK
{
  "id": 1,
  "username": "john_doe",
  "profile_url": "https://supabase.co/.../user_1_uuid.jpg",
  ...
}
```

### Get User Statistics
```http
GET /users/me/stats
Authorization: Bearer <token>

Response: 200 OK
{
  "total_recipes_created": 5,
  "total_recipes_saved": 10,
  "total_cooking_sessions": 8,
  "completed_cooking_sessions": 6,
  "total_cooking_minutes": 240,
  "total_feedbacks_given": 3,
  "average_rating_given": 4.5,
  "recipes_received_feedbacks": 4,
  "average_rating_received": 4.7
}
```

### Change Password
```http
POST /users/me/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}

Response: 204 No Content
```

### Delete Account
```http
DELETE /users/me?password=mypassword
Authorization: Bearer <token>

Response: 204 No Content
```

---

## 🍳 Recipes

### Create Recipe
```http
POST /recipes/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Burmese Mohinga",
  "description": "Traditional Burmese fish noodle soup",
  "cuisine": "Burmese",
  "difficulty": "Medium",
  "total_time": 60,
  "ingredients": "rice noodles, fish, lemongrass, ginger, onions, fish sauce",
  "image_url": null,
  "is_public": true,
  "steps": [
    {
      "step_number": 1,
      "instruction_text": "Prepare the fish broth",
      "media_url": null
    },
    {
      "step_number": 2,
      "instruction_text": "Cook the rice noodles",
      "media_url": null
    }
  ]
}

Response: 201 Created
{
  "id": 1,
  "title": "Burmese Mohinga",
  "description": "Traditional Burmese fish noodle soup",
  "cuisine": "Burmese",
  "difficulty": "Medium",
  "total_time": 60,
  "ingredients": "rice noodles, fish, lemongrass...",
  "image_url": null,
  "is_public": true,
  "created_by": 1,
  "steps": [...],
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-01T10:00:00Z"
}
```

### List All Public Recipes (Paginated)
```http
GET /recipes/?page=1&page_size=10

Response: 200 OK
{
  "items": [
    {
      "id": 1,
      "title": "Burmese Mohinga",
      "cuisine": "Burmese",
      "difficulty": "Medium",
      "total_time": 60,
      "is_public": true,
      ...
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

### Search & Filter Recipes
```http
GET /recipes/search?search=chicken&cuisine=Italian&difficulty=Easy&min_time=15&max_time=45&ingredients=tomato&include_private=false&page=1&page_size=10
Authorization: Bearer <token> (optional, required for include_private=true)

Query Parameters:
- search: Search in title, description, ingredients
- cuisine: Filter by cuisine type
- difficulty: Filter by difficulty (Easy, Medium, Hard)
- min_time: Minimum cooking time in minutes
- max_time: Maximum cooking time in minutes
- ingredients: Search for specific ingredients
- created_by: Filter by creator user ID
- include_private: Include your private recipes (requires auth)
- page: Page number (default: 1)
- page_size: Items per page (default: 10, max: 100)

Response: 200 OK (Paginated list of recipes)
```

### Get Single Recipe
```http
GET /recipes/{recipe_id}

Response: 200 OK
{
  "id": 1,
  "title": "Burmese Mohinga",
  "description": "Traditional Burmese fish noodle soup",
  "cuisine": "Burmese",
  "difficulty": "Medium",
  "total_time": 60,
  "ingredients": "rice noodles, fish...",
  "image_url": "https://...",
  "is_public": true,
  "created_by": 1,
  "steps": [
    {
      "id": 1,
      "recipe_id": 1,
      "step_number": 1,
      "instruction_text": "Prepare the fish broth",
      "media_url": null,
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-01T10:00:00Z"
    }
  ],
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-01T10:00:00Z"
}
```

### Update Recipe
```http
PUT /recipes/{recipe_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "is_public": false,
  "steps": [...]
}

Response: 200 OK (Updated recipe)
```

### Delete Recipe
```http
DELETE /recipes/{recipe_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "detail": "Deleted"
}
```

### Upload Recipe Image
```http
POST /recipes/{recipe_id}/upload-image
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_file>

Accepts: JPEG, PNG, WebP, GIF (max 10MB)

Response: 200 OK (Updated recipe with image_url)
```

### Upload Cooking Step Media
```http
POST /recipes/{recipe_id}/steps/{step_number}/upload-media
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_or_video_file>

Accepts: 
- Images: JPEG, PNG, WebP, GIF (max 10MB)
- Videos: MP4, WebM, QuickTime (max 50MB)

Response: 200 OK (Updated recipe with step media_url)
```

---

## 🧑‍🍳 Cooking Sessions

### Start Cooking Session
```http
POST /cooking-sessions/
Authorization: Bearer <token>
Content-Type: application/json

{
  "recipe_id": 1
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "started_at": "2025-11-01T10:00:00Z",
  "ended_at": null,
  "duration_minutes": null,
  "notes": null,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-01T10:00:00Z"
}
```

### End Cooking Session
```http
PUT /cooking-sessions/{session_id}/end
Authorization: Bearer <token>
Content-Type: application/json

{
  "notes": "Turned out great! Added extra spices."
}

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "started_at": "2025-11-01T10:00:00Z",
  "ended_at": "2025-11-01T11:30:00Z",
  "duration_minutes": 90,
  "notes": "Turned out great! Added extra spices.",
  ...
}
```

### Get User's Cooking Sessions
```http
GET /cooking-sessions/?page=1&page_size=10
Authorization: Bearer <token>

Response: 200 OK (Paginated list of sessions)
```

### Get Single Cooking Session
```http
GET /cooking-sessions/{session_id}
Authorization: Bearer <token>

Response: 200 OK (Session details)
```

### Delete Cooking Session
```http
DELETE /cooking-sessions/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "detail": "Deleted"
}
```

---

## ⭐ Saved Recipes

### Save Recipe
```http
POST /saved-recipes/
Authorization: Bearer <token>
Content-Type: application/json

{
  "recipe_id": 1
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "created_at": "2025-11-01T10:00:00Z"
}
```

### Get Saved Recipes
```http
GET /saved-recipes/?page=1&page_size=10
Authorization: Bearer <token>

Response: 200 OK
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "recipe_id": 1,
      "recipe": {
        "id": 1,
        "title": "Burmese Mohinga",
        ...
      },
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### Remove Saved Recipe
```http
DELETE /saved-recipes/{recipe_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "detail": "Removed from saved recipes"
}
```

---

## 💬 Feedback & Reviews

### Submit Recipe Feedback
```http
POST /feedbacks/
Authorization: Bearer <token>
Content-Type: application/json

{
  "recipe_id": 1,
  "rating": 5,
  "comment": "Absolutely delicious! Easy to follow instructions."
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "rating": 5,
  "comment": "Absolutely delicious!...",
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-01T10:00:00Z"
}
```

### Get Recipe Feedbacks
```http
GET /feedbacks/recipe/{recipe_id}?page=1&page_size=10

Response: 200 OK (Paginated list of feedbacks)
```

### Get User's Feedbacks
```http
GET /feedbacks/my-feedbacks?page=1&page_size=10
Authorization: Bearer <token>

Response: 200 OK (Paginated list of user's feedbacks)
```

### Update Feedback
```http
PUT /feedbacks/{feedback_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "rating": 4,
  "comment": "Updated review"
}

Response: 200 OK (Updated feedback)
```

### Delete Feedback
```http
DELETE /feedbacks/{feedback_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "detail": "Deleted"
}
```

---

## ⚙️ User Preferences

### Get User Preferences
```http
GET /user-preferences/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "language": "en",
  "spice_level": "medium",
  "diet_type": "vegetarian",
  "allergies": "peanuts, shellfish",
  "preferred_cuisine": "Italian",
  "cooking_skill": "intermediate"
}
```

### Create/Update User Preferences
```http
POST /user-preferences/
Authorization: Bearer <token>
Content-Type: application/json

{
  "language": "en",
  "spice_level": "high",
  "diet_type": "vegan",
  "allergies": "nuts",
  "preferred_cuisine": "Thai",
  "cooking_skill": "advanced"
}

Response: 200 OK (Created/Updated preferences)
```

---

## 🤖 Chat Assistant

### Send Message to AI Assistant
```http
POST /chat/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Show me healthy chicken recipes under 30 minutes"
}

Response: 200 OK
{
  "message_id": 1,
  "ai_reply": "I found several healthy chicken recipes for you...",
  "cooking_recipe": null,
  "language": "en",
  "health_nutrition": "Chicken is an excellent source of protein...",
  "media_suggestions": [
    {
      "type": "image",
      "title": "Visual guide for healthy chicken recipes",
      "suggestion": "Try searching: 'healthy chicken recipes cooking tutorial' on YouTube"
    }
  ]
}
```

### Get Chat History
```http
GET /chat/history?limit=20
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "user_message": "Show me healthy chicken recipes",
    "ai_reply": "I found several healthy chicken recipes...",
    "created_at": "2025-11-01T10:00:00Z"
  }
]
```

---

## 🎯 Recommendations

### Get Recipe Recommendations
```http
GET /recommendations/?page=1&page_size=10
Authorization: Bearer <token>

Response: 200 OK
{
  "items": [
    {
      "id": 5,
      "title": "Recommended Recipe",
      "cuisine": "Italian",
      "difficulty": "Easy",
      ...
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10,
  "total_pages": 2
}
```

---

## 📤 File Uploads

### Supabase Storage Configuration
All file uploads are stored in Supabase Storage with the following structure:

```
general/ (bucket)
├── avatars/
│   └── user_{user_id}_{uuid}.{ext}
├── recipes/
│   └── recipe_{recipe_id}_{uuid}.{ext}
└── cooking-steps/
    └── recipe_{recipe_id}_step_{step_number}_{uuid}.{ext}
```

### File Upload Limits
- **Profile Images**: Max 5MB (JPEG, PNG, WebP, GIF)
- **Recipe Images**: Max 10MB (JPEG, PNG, WebP, GIF)
- **Step Media (Images)**: Max 10MB (JPEG, PNG, WebP, GIF)
- **Step Media (Videos)**: Max 50MB (MP4, WebM, QuickTime)

---

## 🔍 Search & Filter Features

### Recipe Search Capabilities
1. **Full-text search** in title, description, and ingredients
2. **Cuisine filter** (e.g., Italian, Burmese, Chinese, Thai)
3. **Difficulty filter** (Easy, Medium, Hard)
4. **Time range filter** (min_time to max_time)
5. **Ingredient search** (find recipes with specific ingredients)
6. **Creator filter** (recipes by specific user)
7. **Privacy filter** (public only or include your private recipes)

### Example Complex Search
```http
GET /recipes/search?search=pasta&cuisine=Italian&difficulty=Easy&max_time=30&ingredients=tomato&page=1&page_size=20
```

---

## 🌐 Response Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## 🎨 Frontend Features to Implement

### 1. **Authentication Pages**
- [ ] Login page
- [ ] Registration page
- [ ] Password reset flow
- [ ] Protected route wrapper

### 2. **User Dashboard**
- [ ] Profile page with stats
- [ ] Edit profile form
- [ ] Upload profile picture
- [ ] Change password form
- [ ] User preferences settings

### 3. **Recipe Management**
- [ ] Recipe list/grid view with pagination
- [ ] Recipe detail page
- [ ] Create recipe form (multi-step)
- [ ] Edit recipe form
- [ ] Delete recipe confirmation
- [ ] Upload recipe image
- [ ] Upload step media (images/videos)
- [ ] Public/Private toggle

### 4. **Recipe Discovery**
- [ ] Advanced search interface
- [ ] Filter sidebar (cuisine, difficulty, time, ingredients)
- [ ] Search results page
- [ ] Recipe cards with images
- [ ] "My Recipes" vs "Public Recipes" tabs

### 5. **Cooking Features**
- [ ] Start cooking session button
- [ ] Step-by-step cooking guide
- [ ] Timer integration
- [ ] End session with notes
- [ ] Cooking history page

### 6. **Social Features**
- [ ] Save/unsave recipe button
- [ ] Saved recipes collection
- [ ] Rating & review system
- [ ] Comment section on recipes
- [ ] User profile pages

### 7. **AI Chat Assistant**
- [ ] Chat interface (sidebar or modal)
- [ ] Message history
- [ ] Health & nutrition info display
- [ ] Media suggestions display
- [ ] Recipe recommendations from chat

### 8. **Recommendations**
- [ ] Personalized recipe feed
- [ ] "Recommended for you" section
- [ ] Based on preferences and history

### 9. **User Preferences**
- [ ] Preferences form
- [ ] Language selector
- [ ] Dietary restrictions
- [ ] Allergy management
- [ ] Spice level preference

### 10. **Additional Features**
- [ ] Responsive design (mobile-first)
- [ ] Dark mode toggle
- [ ] Loading states & skeletons
- [ ] Error handling & toast notifications
- [ ] Image lazy loading
- [ ] Infinite scroll or pagination
- [ ] Share recipe functionality
- [ ] Print recipe view

---

## 🛠️ Tech Stack Recommendations

### Frontend Framework
- **React** with TypeScript
- **Next.js** (for SSR/SSG)
- **Vite + React** (for SPA)

### State Management
- **React Query / TanStack Query** (for API state)
- **Zustand** or **Redux Toolkit** (for global state)

### UI Libraries
- **TailwindCSS** (styling)
- **shadcn/ui** (components)
- **Lucide React** (icons)
- **Framer Motion** (animations)

### Form Handling
- **React Hook Form**
- **Zod** (validation)

### HTTP Client
- **Axios** or **Fetch API**

### Additional Libraries
- **react-router-dom** (routing)
- **date-fns** (date formatting)
- **react-hot-toast** (notifications)
- **react-dropzone** (file uploads)

---

## 📝 Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## 🚀 Getting Started

1. Clone the repository
2. Install dependencies: `npm install` or `yarn install`
3. Set up environment variables
4. Run development server: `npm run dev`
5. Start building features!

---

## 📚 Additional Resources

- **API Interactive Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Backend Repository**: [Link to backend repo]

---

**Last Updated**: November 1, 2025
**API Version**: 1.0.0
