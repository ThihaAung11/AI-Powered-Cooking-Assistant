# Cooking Assistant Chat Setup

## Overview
The cooking assistant uses LangGraph to provide intelligent, context-aware cooking recommendations and step-by-step guidance in both English and Burmese.

## Installation

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

## API Endpoints

### 1. Send Message to Cooking Assistant
**POST** `/chat/message`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Request Body:**
```json
{
  "message": "I want to cook something spicy for dinner"
}
```

**Response:**
```json
{
  "message_id": 1,
  "ai_reply": "Based on your preferences, I recommend Recipe ID: 5...",
  "cooking_recipe": "Spicy Burmese Curry",
  "language": "en"
}
```

### 2. Get Chat History
**GET** `/chat/history?limit=20`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "messages": [
    {
      "id": 1,
      "user_message": "I want to cook something spicy",
      "ai_reply": "I recommend...",
      "created_at": "2025-10-28T10:30:00"
    }
  ],
  "total": 1
}
```

## How It Works

### LangGraph Workflow

1. **User Context Node**: Fetches user preferences (diet, spice level, cuisine, language)
2. **Recipe List Node**: Queries recipes matching user preferences
3. **Recommend Recipe Node**: Uses GPT-4o-mini to recommend the best recipe
4. **Cooking Guide Node**: Provides step-by-step cooking instructions

### Language Support

- **English** (`en`): Default language
- **Burmese** (`my`): Myanmar language support

The assistant automatically responds in the user's preferred language based on their `UserPreference.language` setting.

## Testing

### 1. Register a user:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Chat with assistant:
```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "message": "What can I cook for dinner tonight?"
  }'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | Response creativity (0-1) | `0.6` |

### User Preferences

Users can set their preferences which affect recipe recommendations:
- `language`: "en" or "my"
- `diet_type`: "vegetarian", "omnivore", etc.
- `spice_level`: "low", "medium", "high"
- `preferred_cuisine`: "Burmese", "Thai", etc.
- `cooking_skill`: Skill level

## Troubleshooting

### "OPENAI_API_KEY not configured"
- Make sure you've set `OPENAI_API_KEY` in your `.env` file
- Restart your server after updating `.env`

### "User with id X not found"
- Ensure you're authenticated with a valid JWT token
- Check that the user exists in the database

### No recipes returned
- Add recipes to the database first
- Check that recipes have the required fields (title, description, cuisine)

## Next Steps

1. Add more recipes to the database
2. Create user preferences for better recommendations
3. Add cooking steps to recipes for detailed guidance
4. Test with both English and Burmese languages
