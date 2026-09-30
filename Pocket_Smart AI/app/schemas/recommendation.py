from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class RecommendationCard(BaseModel):
    id: Optional[str] = None
    name: str
    category: str
    estimated_price: float
    platform: str
    reason: str
    style: Optional[str] = ""
    budget_status: str = "within_budget"  # within_budget, near_budget, over_budget
    search_url: Optional[str] = ""
    suggested_color: Optional[str] = None
    suggested_material: Optional[str] = None

class RecommendationPayload(BaseModel):
    budget: float
    total_estimated_cost: float
    remaining_budget: float
    budget_status: str  # within_budget, near_budget, over_budget
    allocated_budget: Dict[str, float]
    recommendations: List[RecommendationCard]
    summary: str
    tips: List[str]
    cheaper_alternatives: Optional[List[RecommendationCard]] = []
    outfit_analysis: Optional[Dict[str, Any]] = None  # For jewelry outfit image analysis results

class RecommendationResponse(BaseModel):
    id: int
    request_id: int
    planner_type: str
    budget: float
    result: RecommendationPayload
    created_at: datetime
    is_saved: bool = False

    class Config:
        from_attributes = True

class HistoryItem(BaseModel):
    id: int
    request_id: int
    planner_type: str
    budget: float
    summary: str
    total_estimated_cost: float
    created_at: datetime
    is_saved: bool = False
