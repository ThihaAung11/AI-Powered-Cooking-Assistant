from typing import Generic, TypeVar, List
from pydantic import BaseModel
from sqlalchemy.orm import Query
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = 1
    page_size: int = 10
    
    def get_offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.page_size
    
    def get_limit(self) -> int:
        """Get limit for database query"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    class Config:
        from_attributes = True


def paginate(query: Query, params: PaginationParams, model_class: type[T]) -> PaginatedResponse[T]:
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        params: Pagination parameters
        model_class: Pydantic model class for response items
    
    Returns:
        PaginatedResponse with paginated items and metadata
    """
    # Get total count
    total = query.count()
    
    # Calculate total pages
    total_pages = ceil(total / params.page_size) if total > 0 else 0
    
    # Get paginated items
    items = query.offset(params.get_offset()).limit(params.get_limit()).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
        has_next=params.page < total_pages,
        has_prev=params.page > 1
    )
