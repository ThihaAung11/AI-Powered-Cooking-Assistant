# Feedback API Documentation

Complete API documentation for user feedback endpoints.

## Endpoints

### 1. Create Feedback
**POST** `/feedbacks/`

Create feedback for a recipe. Each user can only provide one feedback per recipe.

**Request Body:**
```json
{
  "recipe_id": 1,
  "rating": 5,
  "comment": "Delicious recipe! Easy to follow."
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "rating": 5,
  "comment": "Delicious recipe! Easy to follow.",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `400` - User already provided feedback for this recipe
- `404` - Recipe not found
- `401` - Unauthorized

---

### 2. Get My Feedbacks
**GET** `/feedbacks/my-feedbacks?page=1&page_size=10`

List all feedbacks created by the current user with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1, min: 1)
- `page_size` (optional): Items per page (default: 10, min: 1, max: 100)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "recipe_id": 1,
      "rating": 5,
      "comment": "Great!",
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

### 3. Get Recipe Feedbacks
**GET** `/feedbacks/recipe/{recipe_id}?page=1&page_size=10`

List all feedbacks for a specific recipe with pagination.

**Path Parameters:**
- `recipe_id`: Recipe ID

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)

**Response:** `200 OK`
```json
{
  "items": [...],
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

### 4. Get Recipe Rating Statistics
**GET** `/feedbacks/recipe/{recipe_id}/stats`

Get aggregated rating statistics for a recipe.

**Path Parameters:**
- `recipe_id`: Recipe ID

**Response:** `200 OK`
```json
{
  "recipe_id": 1,
  "total_feedbacks": 50,
  "average_rating": 4.5,
  "min_rating": 2,
  "max_rating": 5
}
```

---

### 5. Get My Feedback for Recipe
**GET** `/feedbacks/recipe/{recipe_id}/my-feedback`

Get the current user's feedback for a specific recipe.

**Path Parameters:**
- `recipe_id`: Recipe ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "rating": 5,
  "comment": "Great recipe!",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `404` - Feedback not found

---

### 6. Get Feedback by ID
**GET** `/feedbacks/{feedback_id}`

Get a specific feedback by its ID.

**Path Parameters:**
- `feedback_id`: Feedback ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "rating": 5,
  "comment": "Excellent!",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `404` - Feedback not found

---

### 7. Update Feedback
**PUT** `/feedbacks/{feedback_id}`

Update user's own feedback. Users can only update their own feedback.

**Path Parameters:**
- `feedback_id`: Feedback ID

**Request Body:**
```json
{
  "rating": 4,
  "comment": "Updated comment"
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "rating": 4,
  "comment": "Updated comment",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

**Errors:**
- `401` - Unauthorized (not the owner)
- `404` - Feedback not found

---

### 8. Delete Feedback
**DELETE** `/feedbacks/{feedback_id}`

Delete user's own feedback. Users can only delete their own feedback.

**Path Parameters:**
- `feedback_id`: Feedback ID

**Response:** `204 No Content`

**Errors:**
- `401` - Unauthorized (not the owner)
- `404` - Feedback not found

---

## Data Models

### FeedbackCreate
```json
{
  "recipe_id": "integer (required)",
  "rating": "integer (required, 1-5)",
  "comment": "string (optional, max 1000 chars)"
}
```

### FeedbackUpdate
```json
{
  "rating": "integer (optional, 1-5)",
  "comment": "string (optional, max 1000 chars)"
}
```

### FeedbackOut
```json
{
  "id": "integer",
  "user_id": "integer",
  "recipe_id": "integer",
  "rating": "integer (1-5)",
  "comment": "string | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## Business Rules

1. **One Feedback Per Recipe**: Each user can only create one feedback per recipe
2. **Rating Range**: Rating must be between 1 and 5 (inclusive)
3. **Comment Length**: Comments are limited to 1000 characters
4. **Ownership**: Users can only update/delete their own feedback
5. **Cascade Delete**: Feedbacks are automatically deleted when the associated recipe or user is deleted

---

## Example Usage

### Create Feedback
```bash
curl -X POST "http://localhost:8000/feedbacks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": 1,
    "rating": 5,
    "comment": "Amazing recipe!"
  }'
```

### Get Recipe Statistics
```bash
curl -X GET "http://localhost:8000/feedbacks/recipe/1/stats"
```

### Update Feedback
```bash
curl -X PUT "http://localhost:8000/feedbacks/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "comment": "Good, but could be better"
  }'
```

### List My Feedbacks (Paginated)
```bash
curl -X GET "http://localhost:8000/feedbacks/my-feedbacks?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
