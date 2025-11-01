# Pagination Utility

Common pagination utilities for the API.

## Usage

### In Services

```python
from ..utils.pagination import PaginationParams, PaginatedResponse, paginate
from ..schemas.your_schema import YourModelOut

def list_items(db: Session, params: Optional[PaginationParams] = None) -> PaginatedResponse[YourModelOut]:
    """List items with pagination"""
    query = db.query(YourModel).order_by(YourModel.created_at.desc())
    
    if params is None:
        params = PaginationParams()
    
    return paginate(query, params, YourModelOut)
```

### In Routers

```python
from fastapi import Query
from ..utils.pagination import PaginationParams, PaginatedResponse

@router.get("/", response_model=PaginatedResponse[YourModelOut])
def list_all(
    db: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    params = PaginationParams(page=page, page_size=page_size)
    return list_items(db, params)
```

## Response Format

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

## Parameters

- `page`: Current page number (default: 1, min: 1)
- `page_size`: Number of items per page (default: 10, min: 1, max: 100)

## Features

- ✅ Generic type support for type safety
- ✅ Automatic total count calculation
- ✅ Total pages calculation
- ✅ Next/previous page indicators
- ✅ Configurable page size limits
- ✅ Works with any SQLAlchemy query
