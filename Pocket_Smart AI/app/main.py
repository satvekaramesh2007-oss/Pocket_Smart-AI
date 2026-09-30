import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import init_db
from app.routes import auth, home, party, jewelry, recommendations, history, views

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pocketsmart.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to initialize database tables on startup."""
    logger.info("Initializing SQLite database tables...")
    init_db()
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="GenAI-powered budget planning and recommendation assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files & Templates setup
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="app/templates")

# Include API Routers
app.include_router(auth.router)
app.include_router(home.router)
app.include_router(party.router)
app.include_router(jewelry.router)
app.include_router(recommendations.router)
app.include_router(history.router)

# Include HTML Page Views Router (Catch-all page views)
app.include_router(views.router)

# Global Error Handler for HTML or API Requests
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error at {request.url.path}: {exc}", exc_info=True)
    
    # If API request, return JSON error
    if request.url.path.startswith("/api") or request.url.path.startswith("/generate"):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected server error occurred. Please try again."}
        )
    
    # For web page requests, return friendly HTML response
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "page_title": "Error - PocketSmart AI",
            "error": "Something went wrong while processing your request. Please go back to the home page.",
            "demo_mode": settings.DEMO_MODE
        },
        status_code=500
    )
