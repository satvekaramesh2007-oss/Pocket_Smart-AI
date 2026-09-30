from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.recommendation_service import recommendation_service

router = APIRouter(tags=["Jewelry Planner"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

@router.post("/generate-jewelry", status_code=status.HTTP_201_CREATED)
async def generate_jewelry_plan(
    budget: float = Form(...),
    occasion: str = Form(...),
    jewelry_type: str = Form(...),
    style: str = Form(...),
    metal_preference: Optional[str] = Form("Gold / Silver"),
    color_preference: Optional[str] = Form(""),
    outfit_color: Optional[str] = Form(""),
    additional_requirements: Optional[str] = Form(""),
    outfit_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate jewelry recommendation plan with optional outfit image analysis."""
    if budget <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Budget must be greater than zero.")

    image_bytes = None
    image_mime = "image/jpeg"

    if outfit_image and outfit_image.filename:
        # Validate MIME type
        if outfit_image.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format: {outfit_image.content_type}. Please upload JPG, PNG, or WEBP."
            )
        
        # Read file bytes & check file size limit
        image_bytes = await outfit_image.read()
        max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        if len(image_bytes) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image file size exceeds maximum limit of {settings.MAX_IMAGE_SIZE_MB}MB."
            )
        image_mime = outfit_image.content_type

    req_dict = {
        "budget": budget,
        "occasion": occasion,
        "jewelry_type": jewelry_type,
        "style": style,
        "metal_preference": metal_preference,
        "color_preference": color_preference,
        "outfit_color": outfit_color,
        "additional_requirements": additional_requirements
    }

    try:
        rec_model = recommendation_service.create_jewelry_plan(
            db=db,
            user_id=current_user.id,
            request_data=req_dict,
            image_bytes=image_bytes,
            image_mime=image_mime
        )
        return {
            "id": rec_model.id,
            "request_id": rec_model.request_id,
            "planner_type": "jewelry",
            "message": "Jewelry recommendations generated successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate jewelry recommendations: {str(e)}")
