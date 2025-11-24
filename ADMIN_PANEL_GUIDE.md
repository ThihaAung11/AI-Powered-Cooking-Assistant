# Admin Panel API Documentation

Complete guide for the Admin Panel features in the AI-Powered Cooking Assistant.

## 🚀 Quick Start

### 1. Setup Admin Role and User

First, run the seed script to create roles and an admin user:

```bash
python seed_admin.py
```

This will:
- Create `user`, `admin`, and `moderator` roles
- Prompt you to create an admin user account
- Display available admin endpoints

### 2. Login as Admin

Use the admin credentials to login at:
- **API Docs**: http://localhost:8000/docs
- **Endpoint**: `POST /auth/login`

```json
{
  "username": "admin",
  "password": "your_admin_password"
}
```

You'll receive a JWT token. Use this token for all admin requests by clicking "Authorize" in Swagger UI.

---

## 🔐 Authorization

All admin endpoints require:
1. Valid JWT token (from login)
2. User with `admin` role

If you don't have admin role, you'll receive:
```json
{
  "detail": "Not enough permissions. Admin access required."
}
```

---

## 📚 API Endpoints

### 1. Recipe Management

#### Get All Recipes (Admin View)
```http
GET /admin/recipes
```

**Query Parameters:**
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 100, max: 1000) - Number of results
- `include_private` (bool, default: true) - Include private recipes
- `created_by` (int, optional) - Filter by creator user ID
- `cuisine` (string, optional) - Filter by cuisine

**Response:**
```json
[
  {
    "id": 1,
    "title": "Pad Thai",
    "description": "Traditional Thai noodle dish",
    "cuisine": "Thai",
    "difficulty": "Medium",
    "total_time": 30,
    "ingredients": "Rice noodles, shrimp, eggs...",
    "image_url": "https://...",
    "is_public": true,
    "created_by": 5,
    "creator_name": "John Doe",
    "created_at": "2024-01-15T10:30:00",
    "feedbacks_count": 15,
    "average_rating": 4.5
  }
]
```

#### Create Recipe (Admin)
```http
POST /admin/recipes
```

**Request Body:**
```json
{
  "title": "New Recipe",
  "description": "Description here",
  "cuisine": "Italian",
  "difficulty": "Easy",
  "total_time": 45,
  "ingredients": "Tomatoes, pasta, garlic...",
  "is_public": true
}
```

**Optional:** Include cooking steps
```json
{
  "title": "New Recipe",
  "ingredients": "...",
  "steps": [
    {
      "step_number": 1,
      "instruction_text": "Boil water",
      "media_url": null
    }
  ]
}
```

#### Update Recipe (Admin)
```http
PUT /admin/recipes/{recipe_id}
```

**Request Body:** (all fields optional)
```json
{
  "title": "Updated Title",
  "is_public": false,
  "difficulty": "Hard"
}
```

#### Delete Recipe (Admin)
```http
DELETE /admin/recipes/{recipe_id}
```

**Response:** `204 No Content`

---

### 2. AI Knowledge Management

#### Refresh Recipe Embeddings
```http
POST /admin/ai/refresh-embeddings
```

Regenerates embeddings for RAG (Retrieval-Augmented Generation) system.

**Request Body:**
```json
{
  "recipe_ids": [1, 2, 3],  // Optional: specific recipes, null for all
  "force_refresh": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 3 recipes for AI knowledge base",
  "recipes_processed": 3,
  "embeddings_created": 3
}
```

#### Update AI Recipe Data
```http
POST /admin/ai/update-recipe-data
```

Forces complete refresh of recipe information for AI assistant.

**Request Body:**
```json
{
  "recipe_ids": null,  // null = all recipes
  "force_refresh": true
}
```

---

### 3. User Management

#### Get All Users
```http
GET /admin/users
```

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100, max: 1000)
- `is_active` (bool, optional) - Filter by active status
- `role_id` (int, optional) - Filter by role
- `search` (string, optional) - Search username/email/name

**Response:**
```json
{
  "total": 50,
  "users": [
    {
      "id": 1,
      "username": "johndoe",
      "name": "John Doe",
      "email": "john@example.com",
      "profile_url": "https://...",
      "is_active": true,
      "role_id": 1,
      "role_name": "user",
      "created_at": "2024-01-01T00:00:00",
      "total_recipes": 10,
      "total_cooking_sessions": 25,
      "total_feedbacks": 15
    }
  ]
}
```

#### Get Single User Details
```http
GET /admin/users/{user_id}
```

**Response:** Same as user object above with complete statistics.

#### Deactivate User
```http
POST /admin/users/{user_id}/deactivate
```

**Request Body:**
```json
{
  "reason": "Violation of terms of service"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User johndoe has been deactivated",
  "reason": "Violation of terms of service"
}
```

**Note:** You cannot deactivate your own admin account.

#### Activate User
```http
POST /admin/users/{user_id}/activate
```

**Response:**
```json
{
  "success": true,
  "message": "User johndoe has been activated"
}
```

---

### 4. Comments & Ratings Management

#### Get All Feedbacks
```http
GET /admin/feedbacks
```

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100, max: 1000)
- `recipe_id` (int, optional) - Filter by recipe
- `user_id` (int, optional) - Filter by user
- `min_rating` (int, optional, 1-5) - Minimum rating
- `max_rating` (int, optional, 1-5) - Maximum rating

**Response:**
```json
{
  "total": 200,
  "feedbacks": [
    {
      "id": 1,
      "user_id": 5,
      "username": "johndoe",
      "recipe_id": 10,
      "recipe_title": "Pad Thai",
      "rating": 5,
      "comment": "Excellent recipe! Very easy to follow.",
      "created_at": "2024-01-15T14:30:00"
    }
  ]
}
```

#### Remove Inappropriate Feedback
```http
DELETE /admin/feedbacks/{feedback_id}
```

**Request Body:**
```json
{
  "reason": "Spam content / inappropriate language / off-topic"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback removed successfully",
  "removed_feedback": {
    "feedback_id": 1,
    "user_id": 5,
    "recipe_id": 10,
    "rating": 1,
    "comment": "spam content..."
  },
  "reason": "Spam content",
  "removed_by": "admin",
  "removed_at": "2024-01-15T15:00:00"
}
```

---

### 5. Cooking History & Analytics

#### Get Cooking Sessions History
```http
GET /admin/cooking-sessions
```

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100, max: 1000)
- `user_id` (int, optional) - Filter by user
- `recipe_id` (int, optional) - Filter by recipe
- `completed_only` (bool, default: false) - Only completed sessions

**Response:**
```json
{
  "total": 150,
  "sessions": [
    {
      "session_id": 1,
      "user_id": 5,
      "username": "johndoe",
      "recipe_id": 10,
      "recipe_title": "Pad Thai",
      "started_at": "2024-01-15T18:00:00",
      "ended_at": "2024-01-15T18:45:00",
      "duration_minutes": 45
    }
  ]
}
```

#### Get Cooking Analytics
```http
GET /admin/analytics/cooking?days=30
```

**Query Parameters:**
- `days` (int, default: 30, min: 1, max: 365) - Time range

**Response:**
```json
{
  "total_sessions": 500,
  "completed_sessions": 450,
  "total_cooking_time_minutes": 15000,
  "average_session_duration_minutes": 33.33,
  "most_cooked_recipes": [
    {
      "recipe_id": 10,
      "recipe_title": "Pad Thai",
      "count": 50
    },
    {
      "recipe_id": 15,
      "recipe_title": "Spaghetti Carbonara",
      "count": 45
    }
  ],
  "top_active_users": [
    {
      "user_id": 5,
      "username": "johndoe",
      "session_count": 100
    },
    {
      "user_id": 8,
      "username": "janedoe",
      "session_count": 85
    }
  ]
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Moderate Inappropriate Comments

1. **Find offensive comments:**
```bash
GET /admin/feedbacks?min_rating=1&max_rating=2
```

2. **Review the comment**

3. **Remove if necessary:**
```bash
DELETE /admin/feedbacks/{feedback_id}
{
  "reason": "Inappropriate language"
}
```

### Use Case 2: Manage Problematic Users

1. **Search for user:**
```bash
GET /admin/users?search=username
```

2. **Review user activity:**
```bash
GET /admin/users/{user_id}
```

3. **Check their cooking history:**
```bash
GET /admin/cooking-sessions?user_id={user_id}
```

4. **Deactivate if needed:**
```bash
POST /admin/users/{user_id}/deactivate
{
  "reason": "Multiple policy violations"
}
```

### Use Case 3: Content Management

1. **Find all private recipes:**
```bash
GET /admin/recipes?include_private=true
```

2. **Make a recipe public:**
```bash
PUT /admin/recipes/{recipe_id}
{
  "is_public": true
}
```

3. **Delete inappropriate recipe:**
```bash
DELETE /admin/recipes/{recipe_id}
```

### Use Case 4: Update AI Knowledge Base

1. **After adding new recipes:**
```bash
POST /admin/ai/refresh-embeddings
{
  "recipe_ids": [101, 102, 103]
}
```

2. **Full system refresh (monthly maintenance):**
```bash
POST /admin/ai/update-recipe-data
{
  "recipe_ids": null,
  "force_refresh": true
}
```

### Use Case 5: Platform Analytics

1. **Check monthly statistics:**
```bash
GET /admin/analytics/cooking?days=30
```

2. **Identify popular recipes:**
   - Review `most_cooked_recipes`
   - Feature these recipes on homepage

3. **Identify active users:**
   - Review `top_active_users`
   - Consider rewards/badges

---

## 🔒 Security Best Practices

1. **Never share admin credentials**
2. **Use strong passwords** (minimum 12 characters)
3. **Regularly rotate admin passwords**
4. **Log all admin actions** (implement audit log)
5. **Limit admin access** (only give to trusted users)
6. **Monitor admin activities** (unusual patterns)

---

## 🛠️ Development & Testing

### Testing Admin Endpoints

1. **Start the server:**
```bash
uvicorn app.main:app --reload
```

2. **Access API documentation:**
```
http://localhost:8000/docs
```

3. **Login as admin**

4. **Test each endpoint** using Swagger UI

### Creating Additional Admins

```bash
python seed_admin.py
# Follow prompts to create another admin user
```

### Checking Admin Role

```python
from app.database import SessionLocal
from app.models import User, Role

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()
print(f"User: {user.username}, Role: {user.role.name}")
```

---

## 📊 Admin Dashboard Frontend (Coming Soon)

The frontend admin dashboard is under development. It will include:

- **Dashboard Overview**
  - Total users, recipes, sessions
  - Recent activity feed
  - Quick actions

- **Recipe Management UI**
  - Visual recipe editor
  - Bulk actions
  - Image uploads

- **User Management UI**
  - User search and filters
  - Detailed user profiles
  - Ban/unban controls

- **Content Moderation**
  - Comment review queue
  - Flag system
  - Bulk moderation

- **Analytics Dashboard**
  - Charts and graphs
  - Export capabilities
  - Custom date ranges

---

## 🐛 Troubleshooting

### Issue: "Not enough permissions"
**Solution:** Verify you're logged in as an admin user:
```bash
# Check your user role in database
SELECT u.username, r.name as role 
FROM users u 
JOIN roles r ON u.role_id = r.id 
WHERE u.username = 'your_username';
```

### Issue: "Admin role not found"
**Solution:** Run the seed script:
```bash
python seed_admin.py
```

### Issue: Can't deactivate user
**Solution:** Ensure you're not trying to deactivate your own account.

### Issue: Empty analytics
**Solution:** Check if there's data in the specified time range. Try increasing `days` parameter.

---

## 📝 Future Enhancements

Planned features:
- [ ] Audit log for all admin actions
- [ ] Bulk operations (delete multiple, activate multiple)
- [ ] Email notifications for deactivated users
- [ ] Advanced filtering and sorting
- [ ] Export data to CSV/Excel
- [ ] Role-based permissions (moderator vs admin)
- [ ] Scheduled AI knowledge refresh
- [ ] Real-time analytics dashboard
- [ ] User warning system before deactivation
- [ ] Recipe approval workflow

---

## 📞 Support

For issues or questions:
1. Check the API documentation: `/docs`
2. Review this guide
3. Check application logs
4. Contact development team

---

**Admin Panel Version:** 1.0.0  
**Last Updated:** November 2024  
**Status:** Production Ready ✅
