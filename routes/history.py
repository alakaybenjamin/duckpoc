import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.schemas import SearchHistoryEntry
from models.database_models import SearchHistory, User
from services.auth import get_current_user
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/search-history", response_model=List[SearchHistoryEntry])
async def get_search_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the search history for the current user
    """
    try:
        logger.debug(f"Fetching search history for user: {current_user.email}")
        history = db.query(SearchHistory).filter(
            SearchHistory.user_id == current_user.id
        ).order_by(SearchHistory.created_at.desc()).all()
        return history
    except Exception as e:
        logger.error(f"Failed to retrieve search history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve search history: {str(e)}"
        )

@router.post("/search-history")
async def save_search(
    search_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a search to history
    """
    try:
        logger.debug(f"Saving search for user: {current_user.email}")
        logger.debug(f"Search data: {search_data}")

        history_entry = SearchHistory(
            user_id=current_user.id,
            query=search_data.get("query"),
            category=search_data.get("category"),
            filters=search_data.get("filters"),
            results_count=search_data.get("results_count", 0),
            is_saved=search_data.get("is_saved", False),
            last_used=datetime.utcnow(),
            use_count=1
        )
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        logger.info(f"Successfully saved search history for user: {current_user.email}")
        return {"success": True, "message": "Search saved successfully"}
    except Exception as e:
        logger.error(f"Failed to save search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save search: {str(e)}"
        )