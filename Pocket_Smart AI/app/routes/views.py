from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.recommendation import SavedItem
from app.services.auth_service import get_current_user_optional
from app.services.recommendation_service import recommendation_service

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(include_in_schema=False)

def _common_context(request: Request, user: Optional[User] = None, title: str = "PocketSmart AI") -> dict:
    """Helper to return default context variables for templates."""
    return {
        "request": request,
        "user": user,
        "page_title": title,
        "demo_mode": settings.DEMO_MODE or not settings.GEMINI_API_KEY,
        "project_name": settings.PROJECT_NAME
    }

@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request, user: Optional[User] = Depends(get_current_user_optional)):
    """Render modern landing page."""
    context = _common_context(request, user, "PocketSmart AI - Smart Budget & Recommendation Assistant")
    return templates.TemplateResponse("index.html", context)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: Optional[User] = Depends(get_current_user_optional)):
    """Render user login page."""
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    context = _common_context(request, user, "Login - PocketSmart AI")
    return templates.TemplateResponse("login.html", context)

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, user: Optional[User] = Depends(get_current_user_optional)):
    """Render user registration page."""
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    context = _common_context(request, user, "Register - PocketSmart AI")
    return templates.TemplateResponse("register.html", context)

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_user_optional)):
    """Render protected dashboard page."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    history = recommendation_service.get_user_history(db, user.id)
    saved_count = db.query(SavedItem).filter(SavedItem.user_id == user.id).count()

    context = _common_context(request, user, "User Dashboard - PocketSmart AI")
    context.update({
        "recent_plans": history[:5],
        "total_plans_count": len(history),
        "saved_plans_count": saved_count
    })
    return templates.TemplateResponse("dashboard.html", context)

@router.get("/home-planner", response_class=HTMLResponse)
def home_planner_page(request: Request, user: Optional[User] = Depends(get_current_user_optional)):
    """Render Home Interior Planner page."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    context = _common_context(request, user, "Home Interior Planner - PocketSmart AI")
    return templates.TemplateResponse("home_planner.html", context)

@router.get("/party-planner", response_class=HTMLResponse)
def party_planner_page(request: Request, user: Optional[User] = Depends(get_current_user_optional)):
    """Render Party & Event Planner page."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    context = _common_context(request, user, "Party & Event Planner - PocketSmart AI")
    return templates.TemplateResponse("party_planner.html", context)

@router.get("/jewelry-planner", response_class=HTMLResponse)
def jewelry_planner_page(request: Request, user: Optional[User] = Depends(get_current_user_optional)):
    """Render Jewelry Recommendation Planner page."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    context = _common_context(request, user, "Jewelry Recommendation Planner - PocketSmart AI")
    return templates.TemplateResponse("jewelry_planner.html", context)

@router.get("/results/{rec_id}", response_class=HTMLResponse)
def recommendation_results_page(
    rec_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """Render Recommendation Results Page."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    rec_data = recommendation_service.get_recommendation_by_id(db, rec_id, user.id)
    if not rec_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation plan not found.")

    context = _common_context(request, user, f"Plan Results #{rec_id} - PocketSmart AI")
    context.update({
        "plan": rec_data,
        "result": rec_data["result"]
    })
    return templates.TemplateResponse("results.html", context)

@router.get("/history", response_class=HTMLResponse)
def history_page(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """Render Plan History Page."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    history = recommendation_service.get_user_history(db, user.id)
    context = _common_context(request, user, "Plan History - PocketSmart AI")
    context.update({
        "history_list": history
    })
    return templates.TemplateResponse("history.html", context)

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "demo_mode": settings.DEMO_MODE or not settings.GEMINI_API_KEY,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY)
    }
