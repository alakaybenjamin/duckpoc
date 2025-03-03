import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models.database_models import User, SearchHistory
from services.auth import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/saved-searches")
async def get_saved_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all saved searches for the current user"""
    try:
        logger.debug(f"Fetching saved searches for user: {current_user.email}")
        saved_searches = db.query(SearchHistory).filter(
            SearchHistory.user_id == current_user.id,
            SearchHistory.is_saved == True
        ).order_by(SearchHistory.last_used.desc()).all()
        return saved_searches
    except Exception as e:
        logger.error(f"Failed to retrieve saved searches: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve saved searches: {str(e)}"
        )

@router.post("/saved-searches/{search_id}/execute")
async def execute_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a saved search"""
    try:
        saved_search = db.query(SearchHistory).filter(
            SearchHistory.id == search_id,
            SearchHistory.user_id == current_user.id,
            SearchHistory.is_saved == True
        ).first()

        if not saved_search:
            raise HTTPException(status_code=404, detail="Saved search not found")

        # Update last used time and count
        saved_search.last_used = datetime.utcnow()
        saved_search.use_count += 1
        db.commit()

        # Return all necessary search parameters
        return {
            "query": saved_search.query,
            "category": saved_search.category,
            "filters": saved_search.filters,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute saved search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute saved search: {str(e)}"
        )

@router.post("/search-history/{search_id}/save")
async def save_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a search from history"""
    try:
        logger.debug(f"Attempting to save search {search_id} for user: {current_user.email}")
        search = db.query(SearchHistory).filter(
            SearchHistory.id == search_id,
            SearchHistory.user_id == current_user.id
        ).first()

        if not search:
            raise HTTPException(status_code=404, detail="Search not found")

        search.is_saved = True
        search.last_used = datetime.utcnow()
        db.commit()
        logger.info(f"Successfully saved search {search_id} for user: {current_user.email}")

        return {"success": True, "message": "Search saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save search: {str(e)}"
        )

@router.delete("/saved-searches/{search_id}")
async def delete_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a saved search"""
    try:
        logger.debug(f"Attempting to delete saved search {search_id} for user: {current_user.email}")
        saved_search = db.query(SearchHistory).filter(
            SearchHistory.id == search_id,
            SearchHistory.user_id == current_user.id,
            SearchHistory.is_saved == True
        ).first()

        if not saved_search:
            raise HTTPException(status_code=404, detail="Saved search not found")

        saved_search.is_saved = False
        db.commit()
        logger.info(f"Successfully deleted saved search {search_id} for user: {current_user.email}")

        return {"success": True, "message": "Saved search deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete saved search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete saved search: {str(e)}"
        )