from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.home import HomePlannerRequest
from app.services.auth_service import get_current_user
from app.services.recommendation_service import recommendation_service

router = APIRouter(tags=["Home Planner"])

@router.post("/generate-home", status_code=status.HTTP_201_CREATED)
def generate_home_plan(
    payload: HomePlannerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate home interior budget allocation and product recommendations."""
    try:
        req_dict = payload.model_dump()
        rec_model = recommendation_service.create_home_plan(db, current_user.id, req_dict)
        return {
            "id": rec_model.id,
            "request_id": rec_model.request_id,
            "planner_type": "home",
            "message": "Home interior recommendation generated successfully."
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate home recommendations: {str(e)}")
