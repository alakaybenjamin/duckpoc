from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime

from database import get_db
from models.database_models import Collection, CollectionItem, DataProduct
from models.schemas import CollectionSchema, CollectionCreate, CollectionItemCreate
from services.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/collections", response_model=List[CollectionSchema])
async def get_user_collections(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all collections for the current user"""
    try:
        logger.debug(f"Fetching collections for user: {current_user.email}")
        collections = db.query(Collection).filter(
            Collection.user_id == current_user.id
        ).all()

        # Ensure relationships are loaded
        for collection in collections:
            # Force load items and their data products
            for item in collection.items:
                _ = item.data_product

        logger.debug(f"Found {len(collections)} collections")
        return collections
    except Exception as e:
        logger.error(f"Error fetching collections: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch collections"
        )

@router.post("/collections", response_model=CollectionSchema)
async def create_collection(
    collection: CollectionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new collection"""
    try:
        logger.debug(f"Creating collection for user {current_user.email}: {collection.dict()}")
        collection_db = Collection(
            title=collection.title,
            description=collection.description,
            user_id=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(collection_db)
        db.commit()
        db.refresh(collection_db)
        logger.debug(f"Successfully created collection with ID: {collection_db.id}")
        return collection_db
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create collection"
        )

@router.post("/collections/{collection_id}/items")
async def add_to_collection(
    collection_id: int,
    items: CollectionItemCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add data products to a collection"""
    try:
        logger.debug(f"Adding data products {items.data_product_ids} to collection {collection_id}")

        # Verify collection belongs to user
        collection = db.query(Collection).filter(
            Collection.id == collection_id,
            Collection.user_id == current_user.id
        ).first()

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )

        # Verify all data products exist
        data_products = db.query(DataProduct).filter(
            DataProduct.id.in_(items.data_product_ids)
        ).all()

        if len(data_products) != len(items.data_product_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more data products not found"
            )

        # Add items to collection
        added_count = 0
        for dp_id in items.data_product_ids:
            # Check if item already exists in collection
            existing = db.query(CollectionItem).filter(
                CollectionItem.collection_id == collection_id,
                CollectionItem.data_product_id == dp_id
            ).first()

            if not existing:
                item = CollectionItem(
                    collection_id=collection_id,
                    data_product_id=dp_id,
                    added_at=datetime.utcnow()
                )
                db.add(item)
                added_count += 1

        if added_count > 0:
            # Update collection's updated_at timestamp
            collection.updated_at = datetime.utcnow()
            db.commit()
            logger.debug(f"Successfully added {added_count} items to collection {collection_id}")
            return {"message": f"Added {added_count} items to collection"}
        else:
            return {"message": "No new items added to collection"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding items to collection: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add items to collection"
        )