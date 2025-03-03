import logging
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    q: str
    category: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    id: int
    title: str
    type: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    phase: Optional[str] = None
    severity: Optional[str] = None
    risk_level: Optional[str] = None
    relevance_score: float = 1.0
    data_products: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    page: int
    per_page: int

    class Config:
        from_attributes = True

class SearchHistoryEntry(BaseModel):
    id: int
    query: str
    category: Optional[str]
    filters: Optional[Dict[str, Any]]
    results_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class DataProductBase(BaseModel):
    id: int
    title: str
    description: Optional[str]
    type: str
    format: str
    study_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CollectionItemBase(BaseModel):
    id: int
    data_product: DataProductBase
    added_at: datetime

    class Config:
        from_attributes = True

class CollectionCreate(BaseModel):
    title: str
    description: Optional[str] = None

class CollectionSchema(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[CollectionItemBase] = []

    class Config:
        from_attributes = True

class CollectionItemCreate(BaseModel):
    data_product_ids: List[int]

    class Config:
        from_attributes = True