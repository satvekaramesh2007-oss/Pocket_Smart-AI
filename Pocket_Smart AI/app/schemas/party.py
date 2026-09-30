from typing import Optional
from pydantic import BaseModel, Field, field_validator

class PartyPlannerRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Total budget in INR")
    guests: int = Field(..., ge=1, description="Number of guests")
    event_type: str = Field(..., description="Birthday, Wedding, Engagement, Corporate, Anniversary, Get-together, Other")
    venue_preference: Optional[str] = Field(default="Indoor", description="Indoor, Outdoor, Banquet, Home, Restaurant")
    location: Optional[str] = Field(default="", description="City / area")
    event_date: Optional[str] = Field(default="", description="Date of event")
    food_preference: Optional[str] = Field(default="Veg & Non-Veg", description="Catering preference")
    decoration_style: Optional[str] = Field(default="Theme Decor", description="Minimal, Theme, Floral, Balloon, Luxury")
    entertainment_preference: Optional[str] = Field(default="DJ / Music", description="DJ, Live Band, Games, Magician, None")
    accommodation_required: bool = Field(default=False, description="Whether guest stay is needed")
    additional_notes: Optional[str] = ""

    @field_validator("budget")
    @classmethod
    def budget_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Budget must be greater than zero")
        return v
