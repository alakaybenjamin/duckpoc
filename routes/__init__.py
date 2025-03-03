from .auth import router as auth_router
from .search import router as search_router
from .history import router as history_router
from .collections import router as collections_router
from .saved_searches import router as saved_searches_router

__all__ = ['auth_router', 'search_router', 'history_router', 'collections_router', 'saved_searches_router']