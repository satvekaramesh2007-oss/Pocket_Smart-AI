from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("planner_requests.id", ondelete="CASCADE"), nullable=False)
    result_json = Column(Text, nullable=False)  # JSON string of structured AI recommendations
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    planner_request = relationship("PlannerRequest", back_populates="recommendations")
    saved_by_users = relationship("SavedItem", back_populates="recommendation", cascade="all, delete-orphan")

class SavedItem(Base):
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_items")
    recommendation = relationship("Recommendation", back_populates="saved_by_users")
