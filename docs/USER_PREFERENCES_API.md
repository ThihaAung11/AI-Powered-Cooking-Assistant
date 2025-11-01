# User Preferences API Documentation

Manage user cooking preferences for personalized recommendations and experience.

## Overview

User preferences control:
- Recipe recommendations
- Language for AI responses
- Dietary restrictions
- Cooking skill-based filtering
- Spice level preferences

## Endpoints

### 1. Get My Preferences
**GET** `/preferences/me`

Get current user's preferences. Automatically creates default preferences if they don't exist.

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "language": "en",
  "spice_level": "medium",
  "diet_type": "vegetarian",
  "allergies": "peanuts, shellfish",
  "preferred_cuisine": "Burmese",
  "cooking_skill": "intermediate",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Note:** This endpoint will create preferences with defaults if none exist, so it never returns 404.

---

### 2. Create Preferences
**POST** `/preferences/`

Create user preferences. Each user can only have one set of preferences.

**Request Body:**
```json
{
  "language": "en",
  "spice_level": "medium",
  "diet_type": "vegetarian",
  "allergies": "peanuts, tree nuts",
  "preferred_cuisine": "Burmese",
  "cooking_skill": "intermediate"
}
```

**All fields are optional. Defaults:**
- `language`: "en" (English)
- `spice_level`: null
- `diet_type`: null
- `allergies`: null
- `preferred_cuisine`: null
- `cooking_skill`: null

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "language": "en",
  "spice_level": "medium",
  "diet_type": "vegetarian",
  "allergies": "peanuts, tree nuts",
  "preferred_cuisine": "Burmese",
  "cooking_skill": "intermediate",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Errors:**
- `400` - Preferences already exist (use PUT to update)
- `401` - Unauthorized

---

### 3. Update Preferences
**PUT** `/preferences/`

Update user preferences. Only provided fields will be updated.

**Request Body:**
```json
{
  "spice_level": "high",
  "preferred_cuisine": "Thai"
}
```

**Note:** All fields are optional. Omitted fields remain unchanged.

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "language": "en",
  "spice_level": "high",
  "diet_type": "vegetarian",
  "allergies": "peanuts, tree nuts",
  "preferred_cuisine": "Thai",
  "cooking_skill": "intermediate",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Errors:**
- `404` - Preferences not found (create first)
- `401` - Unauthorized

---

### 4. Delete Preferences
**DELETE** `/preferences/`

Delete user preferences and reset to defaults.

**Response:** `204 No Content`

**Note:** This removes all custom preferences. The system will use default values.

**Errors:**
- `404` - Preferences not found
- `401` - Unauthorized

---

### 5. Get Preference Options
**GET** `/preferences/options`

Get available options and valid values for all preference fields.

**Response:** `200 OK`
```json
{
  "language": {
    "type": "enum",
    "values": ["en", "my"],
    "labels": {
      "en": "English",
      "my": "Burmese (Myanmar)"
    }
  },
  "spice_level": {
    "type": "enum",
    "values": ["low", "medium", "high"],
    "labels": {
      "low": "Low (Mild)",
      "medium": "Medium",
      "high": "High (Spicy)"
    }
  },
  "diet_type": {
    "type": "string",
    "examples": [
      "omnivore",
      "vegetarian",
      "vegan",
      "pescatarian",
      "halal",
      "kosher"
    ]
  },
  "cooking_skill": {
    "type": "string",
    "examples": [
      "beginner",
      "intermediate",
      "advanced",
      "expert"
    ]
  },
  "preferred_cuisine": {
    "type": "string",
    "examples": [
      "Burmese",
      "Thai",
      "Chinese",
      "Indian",
      "Italian",
      "Japanese",
      "Korean",
      "Vietnamese",
      "Mexican",
      "Mediterranean"
    ]
  },
  "allergies": {
    "type": "string",
    "description": "Comma-separated list of allergies",
    "examples": [
      "peanuts, tree nuts",
      "shellfish",
      "dairy",
      "gluten",
      "soy"
    ]
  }
}
```

**Note:** This endpoint doesn't require authentication and is useful for building UI forms.

---

## Field Descriptions

### language
**Type:** Enum  
**Values:** `en` (English), `my` (Burmese)  
**Default:** `en`  
**Purpose:** Controls language for AI chat responses

### spice_level
**Type:** Enum  
**Values:** `low`, `medium`, `high`  
**Default:** `null`  
**Purpose:** Filters recipes by spice level in recommendations

### diet_type
**Type:** String (max 50 chars)  
**Examples:** `vegetarian`, `vegan`, `pescatarian`, `halal`, `kosher`  
**Default:** `null`  
**Purpose:** Filters recipes matching dietary restrictions

### allergies
**Type:** String (max 500 chars)  
**Format:** Comma-separated list  
**Examples:** `peanuts, tree nuts`, `shellfish`, `dairy, gluten`  
**Default:** `null`  
**Purpose:** Helps avoid recipes with allergens (future feature)

### preferred_cuisine
**Type:** String (max 100 chars)  
**Examples:** `Burmese`, `Thai`, `Italian`, `Japanese`  
**Default:** `null`  
**Purpose:** Prioritizes recipes from preferred cuisine in recommendations

### cooking_skill
**Type:** String (max 50 chars)  
**Values:** `beginner`, `intermediate`, `advanced`, `expert`  
**Default:** `null`  
**Purpose:** Matches recipe difficulty to skill level

---

## How Preferences Affect Recommendations

### Recipe Recommendations
Preferences directly influence the recommendation scoring:
- **Cuisine match**: +20 points
- **Skill level match**: +15 points
- **Diet type match**: +15 points

See [Recommendations API](./RECOMMENDATIONS_API.md) for details.

### Chat Responses
- **Language**: Determines response language (English or Burmese)
- **Diet**: Influences recipe suggestions in chat
- **Cuisine**: Prioritizes cuisine-specific recommendations

### Recipe Filtering
Preferences can be used to filter:
- Recipes by cuisine type
- Recipes by difficulty (based on skill)
- Recipes by spice level

---

## Example Usage

### First Time Setup
```bash
# Create preferences
curl -X POST "http://localhost:8000/preferences/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "spice_level": "medium",
    "diet_type": "vegetarian",
    "preferred_cuisine": "Burmese",
    "cooking_skill": "intermediate",
    "allergies": "peanuts"
  }'
```

### Get Current Preferences
```bash
curl -X GET "http://localhost:8000/preferences/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Specific Fields
```bash
# Change only cuisine preference
curl -X PUT "http://localhost:8000/preferences/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_cuisine": "Thai"
  }'
```

### Update Multiple Fields
```bash
curl -X PUT "http://localhost:8000/preferences/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "spice_level": "high",
    "cooking_skill": "advanced",
    "diet_type": "vegan"
  }'
```

### Reset to Defaults
```bash
curl -X DELETE "http://localhost:8000/preferences/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Available Options (for UI)
```bash
curl -X GET "http://localhost:8000/preferences/options"
```

---

## Best Practices

### 1. Initialize on Registration
Create default preferences when users register:
```javascript
// After successful registration
await fetch('/preferences/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    language: userLanguage,
    cooking_skill: 'beginner'
  })
});
```

### 2. Use GET /me for Auto-Creation
The `/preferences/me` endpoint automatically creates preferences if they don't exist:
```javascript
// Always works, never 404
const prefs = await fetch('/preferences/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### 3. Partial Updates
Only send fields you want to change:
```javascript
// Update just the cuisine
await fetch('/preferences/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    preferred_cuisine: 'Italian'
  })
});
```

### 4. Build Dynamic Forms
Use the `/preferences/options` endpoint to build forms:
```javascript
const options = await fetch('/preferences/options');
const data = await options.json();

// Build select dropdown for spice level
data.spice_level.values.forEach(value => {
  const label = data.spice_level.labels[value];
  // Create option element
});
```

---

## Validation Rules

### Field Constraints
- `language`: Must be valid enum value (`en` or `my`)
- `spice_level`: Must be valid enum value (`low`, `medium`, `high`) or null
- `diet_type`: Max 50 characters
- `allergies`: Max 500 characters
- `preferred_cuisine`: Max 100 characters
- `cooking_skill`: Max 50 characters

### Business Rules
- Each user can have only one set of preferences
- Preferences are automatically created with defaults if accessed via `/me`
- Deleting preferences removes all custom settings
- Updating preferences only changes provided fields

---

## Integration with Other Features

### Recommendations
Preferences are automatically used by the recommendation system:
```bash
# Recommendations will use your preferences
GET /recommendations/for-me
```

### Chat
Language preference controls chat responses:
```bash
# Chat will respond in your preferred language
POST /chat/
```

### Recipe Discovery
Use preferences to filter recipes:
```bash
# Get recipes matching your cuisine preference
GET /recipes/?cuisine=Burmese
```

---

## Common Workflows

### Onboarding Flow
1. User registers → `POST /auth/register`
2. User logs in → `POST /auth/login`
3. User sets preferences → `POST /preferences/`
4. User gets recommendations → `GET /recommendations/for-me`

### Settings Update Flow
1. User views current preferences → `GET /preferences/me`
2. User modifies preferences → `PUT /preferences/`
3. User sees updated recommendations → `GET /recommendations/for-me`

### Profile Management
1. Get available options → `GET /preferences/options`
2. Display current preferences → `GET /preferences/me`
3. Allow editing → `PUT /preferences/`
4. Option to reset → `DELETE /preferences/`

---

## Error Handling

### 400 Bad Request
```json
{
  "status_code": 400,
  "detail": "User preferences already exist. Use update instead.",
  "timestamp": "2024-01-01T12:00:00Z",
  "path": "/preferences/"
}
```

### 404 Not Found
```json
{
  "status_code": 404,
  "detail": "User preferences not found. Create preferences first.",
  "timestamp": "2024-01-01T12:00:00Z",
  "path": "/preferences/"
}
```

### 422 Validation Error
```json
{
  "status_code": 422,
  "detail": "('language',): Invalid enum value",
  "timestamp": "2024-01-01T12:00:00Z",
  "path": "/preferences/"
}
```
