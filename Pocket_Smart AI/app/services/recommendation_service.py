import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.planner import PlannerRequest
from app.models.recommendation import Recommendation, SavedItem
from app.models.user import User
from app.services.gemini_service import gemini_service
from app.services.budget_service import evaluate_budget_status, get_demo_catalog_items

class RecommendationService:
    """Service handling orchestration between AI, database persistence, and budget checks."""

    @staticmethod
    def post_process_budget(result_json: Dict[str, Any], total_user_budget: float) -> Dict[str, Any]:
        """Verify strict budget constraint and generate cheaper alternatives if over budget."""
        recs = result_json.get("recommendations", [])
        total_cost = sum(float(r.get("estimated_price", 0)) for r in recs)
        
        status, remaining = evaluate_budget_status(total_user_budget, total_cost)
        
        result_json["budget"] = total_user_budget
        result_json["total_estimated_cost"] = round(total_cost, 2)
        result_json["remaining_budget"] = round(remaining, 2)
        result_json["budget_status"] = status
        
        # If recommendations exceed user budget, automatically populate cheaper alternatives
        if status == "over_budget":
            cheaper_alts = []
            for item in recs:
                discounted_price = round(float(item.get("estimated_price", 0)) * 0.70, 2)
                alt_item = item.copy()
                alt_item["name"] = f"Budget Alternative: {item.get('name')}"
                alt_item["estimated_price"] = discounted_price
                alt_item["reason"] = "Economical alternative suggested to fit within your total budget."
                alt_item["budget_status"] = "within_budget"
                cheaper_alts.append(alt_item)
            result_json["cheaper_alternatives"] = cheaper_alts
            result_json["summary"] += f" Note: Original total (₹{total_cost:,.2f}) exceeded budget. Cheaper alternatives have been provided below."
            
        return result_json

    @classmethod
    def create_home_plan(cls, db: Session, user_id: int, request_data: Dict[str, Any]) -> Recommendation:
        """Process Home Interior Planner request."""
        # 1. Create PlannerRequest database record
        budget = float(request_data.get("budget", 0))
        planner_req = PlannerRequest(
            user_id=user_id,
            planner_type="home",
            budget=budget,
            input_data=json.dumps(request_data),
            created_at=datetime.utcnow()
        )
        db.add(planner_req)
        db.flush()

        # 2. Call Gemini AI / Fallback Service
        raw_result = gemini_service.generate_home_recommendations(request_data)
        
        # 3. Post-process and strictly validate budget
        validated_result = cls.post_process_budget(raw_result, budget)

        # 4. Save Recommendation to DB
        rec_model = Recommendation(
            request_id=planner_req.id,
            result_json=json.dumps(validated_result),
            created_at=datetime.utcnow()
        )
        db.add(rec_model)
        db.commit()
        db.refresh(rec_model)
        return rec_model

    @classmethod
    def create_party_plan(cls, db: Session, user_id: int, request_data: Dict[str, Any]) -> Recommendation:
        """Process Party Planner request."""
        budget = float(request_data.get("budget", 0))
        planner_req = PlannerRequest(
            user_id=user_id,
            planner_type="party",
            budget=budget,
            input_data=json.dumps(request_data),
            created_at=datetime.utcnow()
        )
        db.add(planner_req)
        db.flush()

        raw_result = gemini_service.generate_party_recommendations(request_data)
        validated_result = cls.post_process_budget(raw_result, budget)

        rec_model = Recommendation(
            request_id=planner_req.id,
            result_json=json.dumps(validated_result),
            created_at=datetime.utcnow()
        )
        db.add(rec_model)
        db.commit()
        db.refresh(rec_model)
        return rec_model

    @classmethod
    def create_jewelry_plan(
        cls, db: Session, user_id: int, request_data: Dict[str, Any], image_bytes: Optional[bytes] = None, image_mime: str = "image/jpeg"
    ) -> Recommendation:
        """Process Jewelry Planner request with optional multimodal outfit image."""
        budget = float(request_data.get("budget", 0))
        planner_req = PlannerRequest(
            user_id=user_id,
            planner_type="jewelry",
            budget=budget,
            input_data=json.dumps(request_data),
            created_at=datetime.utcnow()
        )
        db.add(planner_req)
        db.flush()

        raw_result = gemini_service.generate_jewelry_recommendations(request_data, image_bytes, image_mime)
        validated_result = cls.post_process_budget(raw_result, budget)

        rec_model = Recommendation(
            request_id=planner_req.id,
            result_json=json.dumps(validated_result),
            created_at=datetime.utcnow()
        )
        db.add(rec_model)
        db.commit()
        db.refresh(rec_model)
        return rec_model

    @staticmethod
    def get_user_history(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Fetch all historical recommendations for the user."""
        records = (
            db.query(Recommendation)
            .join(PlannerRequest, Recommendation.request_id == PlannerRequest.id)
            .filter(PlannerRequest.user_id == user_id)
            .order_by(Recommendation.created_at.desc())
            .all()
        )

        saved_rec_ids = set(
            s.recommendation_id for s in db.query(SavedItem.recommendation_id).filter(SavedItem.user_id == user_id).all()
        )

        history = []
        for r in records:
            p_req = r.planner_request
            try:
                res_data = json.loads(r.result_json)
            except Exception:
                res_data = {}
            
            history.append({
                "id": r.id,
                "request_id": r.request_id,
                "planner_type": p_req.planner_type,
                "budget": p_req.budget,
                "summary": res_data.get("summary", "Personalized recommendations plan"),
                "total_estimated_cost": res_data.get("total_estimated_cost", p_req.budget),
                "created_at": r.created_at,
                "is_saved": r.id in saved_rec_ids
            })
        return history

    @staticmethod
    def get_recommendation_by_id(db: Session, rec_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve single recommendation detail ensuring user ownership."""
        rec = (
            db.query(Recommendation)
            .join(PlannerRequest, Recommendation.request_id == PlannerRequest.id)
            .filter(Recommendation.id == rec_id, PlannerRequest.user_id == user_id)
            .first()
        )
        if not rec:
            return None

        saved = (
            db.query(SavedItem)
            .filter(SavedItem.recommendation_id == rec_id, SavedItem.user_id == user_id)
            .first()
        ) is not None

        try:
            res_dict = json.loads(rec.result_json)
        except Exception:
            res_dict = {}

        return {
            "id": rec.id,
            "request_id": rec.request_id,
            "planner_type": rec.planner_request.planner_type,
            "budget": rec.planner_request.budget,
            "result": res_dict,
            "created_at": rec.created_at,
            "is_saved": saved
        }

    @staticmethod
    def toggle_save_item(db: Session, rec_id: int, user_id: int) -> bool:
        """Save or unsave recommendation for user. Returns True if saved, False if unsaved."""
        existing = db.query(SavedItem).filter(SavedItem.recommendation_id == rec_id, SavedItem.user_id == user_id).first()
        if existing:
            db.delete(existing)
            db.commit()
            return False
        else:
            new_save = SavedItem(user_id=user_id, recommendation_id=rec_id, created_at=datetime.utcnow())
            db.add(new_save)
            db.commit()
            return True

    @staticmethod
    def delete_recommendation(db: Session, rec_id: int, user_id: int) -> bool:
        """Delete recommendation and associated planner request."""
        rec = (
            db.query(Recommendation)
            .join(PlannerRequest, Recommendation.request_id == PlannerRequest.id)
            .filter(Recommendation.id == rec_id, PlannerRequest.user_id == user_id)
            .first()
        )
        if not rec:
            return False

        planner_req = rec.planner_request
        db.delete(rec)
        db.delete(planner_req)
        db.commit()
        return True

recommendation_service = RecommendationService()
