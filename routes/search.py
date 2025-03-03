from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
import logging
from database import get_db
from models.schemas import SearchQuery, SearchResponse, SearchResult
from models.database_models import ClinicalStudy, DataProduct

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query string"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    phase: Optional[str] = Query(None, description="Filter by phase"),
    start_date: Optional[str] = Query(None, description="Filter by start date"),
    end_date: Optional[str] = Query(None, description="Filter by end date"),
    indication_category: Optional[str] = Query(None, description="Filter by indication category"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    procedure_category: Optional[str] = Query(None, description="Filter by procedure category"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    min_duration: Optional[int] = Query(None, description="Filter by minimum duration"),
    max_duration: Optional[int] = Query(None, description="Filter by maximum duration"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Search across medical studies with filters
    """
    try:
        logger.debug(f"Search request received - query: {q}, status: {status}, phase: {phase}")
        logger.debug(f"Additional filters - category: {category}, indication: {indication_category}, procedure: {procedure_category}")

        # Build base query for studies
        studies_query = db.query(ClinicalStudy).outerjoin(DataProduct)
        logger.debug("Base query created")

        # Split the query string by 'OR' and create search conditions
        search_terms = [term.strip() for term in q.split(' OR ')]
        logger.debug(f"Search terms: {search_terms}")

        # Create search conditions for each term
        search_conditions = []
        for term in search_terms:
            term_conditions = [
                ClinicalStudy.title.ilike(f"%{term}%"),
                ClinicalStudy.description.ilike(f"%{term}%"),
                # Add more searchable fields as needed
            ]
            search_conditions.extend(term_conditions)

        # Combine all conditions with OR
        studies_query = studies_query.filter(or_(*search_conditions))
        logger.debug("Search conditions added")

        # Apply filters if provided
        if status:
            studies_query = studies_query.filter(ClinicalStudy.status == status)
            logger.debug(f"Status filter applied: {status}")

        if phase:
            studies_query = studies_query.filter(ClinicalStudy.phase == phase)
            logger.debug(f"Phase filter applied: {phase}")

        if indication_category:
            studies_query = studies_query.filter(ClinicalStudy.indication_category == indication_category)
            logger.debug(f"Indication category filter applied: {indication_category}")

        if procedure_category:
            studies_query = studies_query.filter(ClinicalStudy.procedure_category == procedure_category)
            logger.debug(f"Procedure category filter applied: {procedure_category}")

        if severity:
            studies_query = studies_query.filter(ClinicalStudy.severity == severity)
            logger.debug(f"Severity filter applied: {severity}")

        if risk_level:
            studies_query = studies_query.filter(ClinicalStudy.risk_level == risk_level)
            logger.debug(f"Risk level filter applied: {risk_level}")

        if start_date:
            studies_query = studies_query.filter(ClinicalStudy.start_date >= start_date)
            logger.debug(f"Start date filter applied: {start_date}")

        if end_date:
            studies_query = studies_query.filter(ClinicalStudy.end_date <= end_date)
            logger.debug(f"End date filter applied: {end_date}")

        if min_duration:
            studies_query = studies_query.filter(ClinicalStudy.duration >= min_duration)
            logger.debug(f"Min duration filter applied: {min_duration}")

        if max_duration:
            studies_query = studies_query.filter(ClinicalStudy.duration <= max_duration)
            logger.debug(f"Max duration filter applied: {max_duration}")

        # Calculate pagination
        try:
            total = studies_query.count()
            logger.debug(f"Total results: {total}")
            studies = studies_query.offset((page - 1) * per_page).limit(per_page).all()
            logger.debug(f"Retrieved {len(studies)} studies for current page")
        except Exception as e:
            logger.error(f"Database query error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error executing database query"
            )

        # Process results
        results = []
        for study in studies:
            try:
                data_products = []
                if hasattr(study, 'data_products') and study.data_products:
                    for dp in study.data_products:
                        data_products.append({
                            'id': dp.id,
                            'title': dp.title,
                            'description': dp.description,
                            'type': dp.type,
                            'format': dp.format,
                            'study_id': dp.study_id,
                            'created_at': dp.created_at
                        })

                result = {
                    'id': study.id,
                    'title': study.title,
                    'type': "study",
                    'description': study.description,
                    'status': study.status,
                    'phase': study.phase,
                    'indication_category': getattr(study, 'indication_category', None),
                    'procedure_category': getattr(study, 'procedure_category', None),
                    'severity': getattr(study, 'severity', None),
                    'risk_level': getattr(study, 'risk_level', None),
                    'start_date': getattr(study, 'start_date', None),
                    'end_date': getattr(study, 'end_date', None),
                    'duration': getattr(study, 'duration', None),
                    'data_products': data_products
                }
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing study {study.id}: {str(e)}", exc_info=True)
                continue

        logger.debug(f"Successfully processed {len(results)} results")
        return {
            'results': results,
            'total': total,
            'page': page,
            'per_page': per_page
        }

    except Exception as e:
        logger.error(f"Search operation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search operation failed: {str(e)}"
        )

@router.get("/suggest")
async def get_suggestions(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial input
    """
    try:
        logger.debug(f"Suggestion request received for query: {q}")
        search_term = f"%{q}%"

        # Get suggestions from studies
        studies = db.query(ClinicalStudy.title).filter(
            ClinicalStudy.title.ilike(search_term)
        ).distinct().limit(5).all()

        suggestions = [{"text": study.title, "type": "study"} for study in studies]
        logger.debug(f"Returning {len(suggestions)} suggestions")

        return {"suggestions": suggestions}

    except Exception as e:
        logger.error(f"Failed to get suggestions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )