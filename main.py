from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
import logging
import os
from starlette.middleware.sessions import SessionMiddleware

from database import get_db, init_db
from models.database_models import User, ClinicalStudy, DataProduct, Collection, CollectionItem
from models.schemas import SearchQuery, SearchResponse, CollectionSchema
from routes import auth, search, collections, saved_searches, history

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BioMed Search API",
    description="""
    A comprehensive biomedical search service API providing advanced multi-index search capabilities 
    with robust collection management and data product selection.

    ## Features
    * Advanced search across medical studies, indications, and procedures
    * Dynamic data product selection and filtering
    * User-driven collection management
    * Secure authentication system

    ## Authentication
    Most endpoints require authentication using JWT tokens. To authenticate:
    1. Register a new account using `/api/auth/register`
    2. Login using `/api/auth/login` to get your access token
    3. Include the token in your requests using the Authorization header:
       `Authorization: Bearer your_token_here`
    """,
    version="1.0.0"
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "your-secret-key"),
    max_age=3600,
    same_site="lax",
    https_only=True
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Include routers with API prefix
app.include_router(
    auth.router,
    prefix="/api",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}}
)

app.include_router(
    search.router,
    prefix="/api",
    tags=["Search"],
    responses={401: {"description": "Unauthorized"}}
)

app.include_router(
    collections.router,
    prefix="/api",
    tags=["Collections"],
    responses={401: {"description": "Unauthorized"}}
)

app.include_router(
    saved_searches.router,
    prefix="/api",
    tags=["Saved Searches"],
    responses={401: {"description": "Unauthorized"}}
)

app.include_router(
    history.router,
    prefix="/api",
    tags=["Search History"],
    responses={401: {"description": "Unauthorized"}}
)

# HTML page routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main search page"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    try:
        return templates.TemplateResponse("auth/login.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration page"""
    try:
        return templates.TemplateResponse("auth/register.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering register page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/collections", response_class=HTMLResponse)
async def collections_page(request: Request):
    """Serve the collections page"""
    try:
        return templates.TemplateResponse("collections.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering collections page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/saved-searches", response_class=HTMLResponse)
async def saved_searches_page(request: Request):
    """Serve the saved searches page"""
    try:
        return templates.TemplateResponse("saved_searches.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering saved searches page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/search-history", response_class=HTMLResponse)
async def search_history_page(request: Request):
    """Serve the search history page"""
    try:
        return templates.TemplateResponse("search_history.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering search history page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {"status": "healthy", "message": "BioMed Search API is running"}

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)