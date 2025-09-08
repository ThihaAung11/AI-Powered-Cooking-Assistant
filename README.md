# AI-Powered Cooking Assistant API

A complete FastAPI backend with JWT authentication, recipe management, and comprehensive error handling.

## Features

- **User Authentication**: JWT-based registration and login
- **Recipe Management**: Full CRUD operations with ownership validation
- **Database**: SQLAlchemy with SQLite (default) or PostgreSQL
- **Security**: Password hashing with bcrypt, JWT tokens
- **Middleware**: Request logging, CORS, global error handling
- **Exception Handling**: Standardized JSON error responses
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### 1. Install Dependencies
```bash
# Dependencies are already installed via uv
uv sync
```

### 2. Configure Environment (Optional)
```bash
cp .env.example .env
# Edit .env to set SECRET_KEY and DATABASE_URL if needed
```

### 3. Start the Server
```bash
uv run uvicorn app.main:app --reload
```

### 4. Access the API
- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Recipes
- `GET /recipes/` - List all recipes (public)
- `GET /recipes/{id}` - Get specific recipe (public)
- `POST /recipes/` - Create recipe (requires auth)
- `PUT /recipes/{id}` - Update recipe (requires auth + ownership)
- `DELETE /recipes/{id}` - Delete recipe (requires auth + ownership)

## Example Usage

### Register a User
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "password": "yourpassword"
  }'
```

### Login
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "yourpassword"
  }'
```

### Create a Recipe (with JWT token)
```bash
curl -X POST "http://127.0.0.1:8000/recipes/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Chocolate Chip Cookies",
    "description": "Classic homemade cookies",
    "ingredients": "flour, butter, sugar, chocolate chips, eggs",
    "steps": "1. Mix dry ingredients 2. Cream butter and sugar 3. Combine and bake"
  }'
```

## Configuration

Environment variables (see `.env.example`):

- `SECRET_KEY`: JWT signing key (change in production!)
- `DATABASE_URL`: Database connection string
  - SQLite: `sqlite:///./app.db` (default)
  - PostgreSQL: `postgresql+psycopg2://user:password@localhost:5432/dbname`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration (default: 60)
- `CORS_ALLOW_ORIGINS`: Comma-separated allowed origins (default: *)

## Database

The app uses SQLAlchemy with automatic table creation on startup (for demo purposes). In production, use Alembic migrations:

```bash
# Initialize Alembic (if not already done)
uv run alembic init alembic

# Create migration
uv run alembic revision --autogenerate -m "Initial migration"

# Apply migration
uv run alembic upgrade head
```

## Error Handling

All errors return standardized JSON:

```json
{
  "status_code": 404,
  "detail": "Recipe not found",
  "timestamp": "2025-09-08T12:34:56Z",
  "path": "/recipes/123"
}
```

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── database.py          # SQLAlchemy setup
├── middleware.py        # Custom middleware
├── exceptions.py        # Custom exceptions & handlers
├── core/
│   ├── config.py        # Settings from environment
│   └── security.py      # JWT & password utilities
├── models/
│   ├── user.py          # User SQLAlchemy model
│   └── recipe.py        # Recipe SQLAlchemy model
├── schemas/
│   ├── auth.py          # Auth Pydantic schemas
│   ├── user.py          # User Pydantic schemas
│   └── recipe.py        # Recipe Pydantic schemas
├── services/
│   ├── auth_service.py  # Authentication business logic
│   ├── user_service.py  # User business logic
│   └── recipe_service.py # Recipe business logic
└── routers/
    ├── auth.py          # Auth endpoints
    └── recipes.py       # Recipe endpoints
```

## Development

The server runs with auto-reload enabled. Make changes to any Python file and the server will automatically restart.

For additional uv commands:
- `uv add <package>` - Add new dependency
- `uv remove <package>` - Remove dependency
- `uv tree` - Show dependency tree
- `uv run <command>` - Run command in project environment