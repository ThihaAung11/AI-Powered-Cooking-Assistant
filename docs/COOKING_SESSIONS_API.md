# Cooking Sessions API Documentation

Track and manage user cooking sessions with recipes.

## Endpoints

### 1. Start Cooking Session
**POST** `/cooking-sessions/`

Start a new cooking session. Users can only have one active session at a time.

**Request Body:**
```json
{
  "recipe_id": 1  // optional, can be null for general cooking
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "started_at": "2024-01-01T12:00:00Z",
  "ended_at": null,
  "duration_minutes": null,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `400` - User already has an active session
- `404` - Recipe not found (if recipe_id provided)
- `401` - Unauthorized

---

### 2. End Cooking Session
**POST** `/cooking-sessions/{session_id}/end`

End an active cooking session and calculate duration.

**Path Parameters:**
- `session_id`: Session ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "started_at": "2024-01-01T12:00:00Z",
  "ended_at": "2024-01-01T13:30:00Z",
  "duration_minutes": 90,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T13:30:00Z"
}
```

**Errors:**
- `400` - Session already ended
- `401` - Unauthorized (not the owner)
- `404` - Session not found

---

### 3. Get Active Session
**GET** `/cooking-sessions/active`

Get the current user's active cooking session.

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "started_at": "2024-01-01T12:00:00Z",
  "ended_at": null,
  "duration_minutes": null,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `404` - No active session found
- `401` - Unauthorized

---

### 4. List My Sessions
**GET** `/cooking-sessions/my-sessions?page=1&page_size=10&active_only=false`

List current user's cooking sessions with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)
- `active_only` (optional): Show only active sessions (default: false)

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false
}
```

---

### 5. Get My Cooking Stats
**GET** `/cooking-sessions/my-stats`

Get comprehensive cooking statistics for the current user.

**Response:** `200 OK`
```json
{
  "total_sessions": 50,
  "completed_sessions": 45,
  "active_sessions": 5,
  "total_cooking_minutes": 2700,
  "average_session_minutes": 60.0,
  "most_cooked_recipe_id": 5,
  "most_cooked_recipe_title": "Burmese Chicken Curry"
}
```

---

### 6. List Recipe Sessions
**GET** `/cooking-sessions/recipe/{recipe_id}?page=1&page_size=10`

List all cooking sessions for a specific recipe.

**Path Parameters:**
- `recipe_id`: Recipe ID

**Query Parameters:**
- `page` (optional): Page number
- `page_size` (optional): Items per page

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 15,
  "page": 1,
  "page_size": 10,
  "total_pages": 2,
  "has_next": true,
  "has_prev": false
}
```

**Errors:**
- `404` - Recipe not found

---

### 7. Get Session by ID
**GET** `/cooking-sessions/{session_id}`

Get a specific cooking session by its ID.

**Path Parameters:**
- `session_id`: Session ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "recipe_id": 1,
  "started_at": "2024-01-01T12:00:00Z",
  "ended_at": "2024-01-01T13:30:00Z",
  "duration_minutes": 90,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T13:30:00Z"
}
```

**Errors:**
- `404` - Session not found

---

### 8. Delete Session
**DELETE** `/cooking-sessions/{session_id}`

Delete a cooking session. Users can only delete their own sessions.

**Path Parameters:**
- `session_id`: Session ID

**Response:** `204 No Content`

**Errors:**
- `401` - Unauthorized (not the owner)
- `404` - Session not found

---

## Business Rules

1. **One Active Session**: Users can only have one active session at a time
2. **Auto Duration**: Duration is automatically calculated when ending a session
3. **Optional Recipe**: Sessions can be started without a recipe (general cooking)
4. **Ownership**: Users can only end/delete their own sessions
5. **Cascade Delete**: Sessions are deleted when the user is deleted
6. **Soft Recipe Delete**: If a recipe is deleted, `recipe_id` is set to NULL

---

## Example Usage

### Start a Session
```bash
curl -X POST "http://localhost:8000/cooking-sessions/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipe_id": 1}'
```

### End a Session
```bash
curl -X POST "http://localhost:8000/cooking-sessions/1/end" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get My Stats
```bash
curl -X GET "http://localhost:8000/cooking-sessions/my-stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Active Sessions Only
```bash
curl -X GET "http://localhost:8000/cooking-sessions/my-sessions?active_only=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
