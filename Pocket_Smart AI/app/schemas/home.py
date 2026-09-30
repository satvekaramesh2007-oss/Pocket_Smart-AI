from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator

class HomeItemQuantity(BaseModel):
    item_name: str
    quantity: int = Field(default=1, ge=1)

class HomePlannerRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Total budget in INR")
    home_type: str = Field(default="Apartment", description="e.g. Apartment, Villa, Independent House")
    room_type: str = Field(..., description="Living Room, Bedroom, Kitchen, Dining Room, Study Room, Other")
    style: str = Field(..., description="Modern, Minimalist, Traditional, Luxury, Scandinavian, Industrial, User-defined")
    items_required: List[str] = Field(default_factory=list, description="List of items e.g. Sofa, Lights, Fan")
    item_quantities: Optional[Dict[str, int]] = Field(default_factory=dict, description="Item quantities map")
    color_preference: Optional[str] = ""
    material_preference: Optional[str] = ""
    brand_preference: Optional[str] = ""
    must_have_items: Optional[str] = ""
    avoid_items: Optional[str] = ""

    @field_validator("budget")
    @classmethod
    def budget_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Budget must be greater than zero")
        return v
