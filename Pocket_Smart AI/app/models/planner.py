from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class PlannerRequest(Base):
    __tablename__ = "planner_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    planner_type = Column(String(50), nullable=False)  # 'home', 'party', 'jewelry'
    budget = Column(Float, nullable=False)
    input_data = Column(Text, nullable=False)  # JSON string of input parameters
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="planner_requests")
    recommendations = relationship("Recommendation", back_populates="planner_request", cascade="all, delete-orphan")
