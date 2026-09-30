from typing import Optional
from pydantic import BaseModel, Field, field_validator

class JewelryPlannerRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Total budget in INR")
    occasion: str = Field(..., description="Wedding, Party, College event, Traditional event, Casual, Engagement, Other")
    jewelry_type: str = Field(..., description="Necklace, Earrings, Bracelet, Ring, Bangles, Full set")
    style: str = Field(..., description="Traditional, Modern, Minimal, Elegant, Statement")
    metal_preference: Optional[str] = Field(default="Gold / Silver", description="Gold, Silver, Platinum, Diamond, Artificial, Mixed")
    color_preference: Optional[str] = ""
    outfit_color: Optional[str] = ""
    additional_requirements: Optional[str] = ""
    outfit_image_url: Optional[str] = None

    @field_validator("budget")
    @classmethod
    def budget_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Budget must be greater than zero")
        return v
