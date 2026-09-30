from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.recommendation_service import recommendation_service

router = APIRouter(tags=["Recommendations"])

@router.get("/recommendations/{rec_id}")
def get_recommendation_detail(
    rec_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve detailed recommendation JSON payload by ID."""
    rec = recommendation_service.get_recommendation_by_id(db, rec_id, current_user.id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation plan not found or access denied."
        )
    return rec

@router.post("/recommendations/{rec_id}/save")
def toggle_save_recommendation(
    rec_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle bookmark / saved state of a recommendation plan."""
    rec = recommendation_service.get_recommendation_by_id(db, rec_id, current_user.id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation plan not found or access denied."
        )
    
    is_saved = recommendation_service.toggle_save_item(db, rec_id, current_user.id)
    return {
        "id": rec_id,
        "is_saved": is_saved,
        "message": "Plan saved to your collection." if is_saved else "Plan removed from saved collection."
    }

@router.delete("/recommendations/{rec_id}")
def delete_recommendation(
    rec_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete recommendation plan and associated request record."""
    deleted = recommendation_service.delete_recommendation(db, rec_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation plan not found or access denied."
        )
    return {"message": "Recommendation plan deleted successfully."}
