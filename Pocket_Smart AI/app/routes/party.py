from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.party import PartyPlannerRequest
from app.services.auth_service import get_current_user
from app.services.recommendation_service import recommendation_service

router = APIRouter(tags=["Party Planner"])

@router.post("/generate-party", status_code=status.HTTP_201_CREATED)
def generate_party_plan(
    payload: PartyPlannerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate party and event budget allocation and recommendations."""
    try:
        req_dict = payload.model_dump()
        rec_model = recommendation_service.create_party_plan(db, current_user.id, req_dict)
        return {
            "id": rec_model.id,
            "request_id": rec_model.request_id,
            "planner_type": "party",
            "message": "Party planning recommendations generated successfully."
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate party recommendations: {str(e)}")
