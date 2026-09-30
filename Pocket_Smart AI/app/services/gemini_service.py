import json
import logging
import re
from typing import Dict, Any, Optional
from PIL import Image
import io

from app.config import settings
from app.services.budget_service import (
    calculate_home_budget_breakdown,
    calculate_party_budget_breakdown,
    calculate_jewelry_budget_breakdown,
    get_demo_catalog_items,
    generate_search_url,
    evaluate_budget_status
)

logger = logging.getLogger("pocketsmart.gemini")

class GeminiService:
    """Service to handle AI generation using Google Gemini API or fallbacks."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else None
        self.model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini client initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI SDK: {e}. Falling back to DEMO_MODE.")
                self.client = None

    def _is_api_available(self) -> bool:
        return self.client is not None and not settings.DEMO_MODE

    def _clean_json_response(self, text: str) -> str:
        """Extract valid JSON payload from markdown block or raw text."""
        cleaned = text.strip()
        # Remove ```json ... ``` codeblock backticks if present
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()
        return cleaned

    def generate_home_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate home interior recommendations via Gemini AI or Fallback engine."""
        if not self._is_api_available():
            return self._fallback_home_recommendations(request_data)

        prompt = f"""
You are an expert interior designer and budget optimization AI assistant.
Analyze the user's budget and room requirements, then return a valid JSON object.

User Request:
- Total Budget: ₹{request_data.get('budget')} INR
- Home Type: {request_data.get('home_type')}
- Room Type: {request_data.get('room_type')}
- Style Preference: {request_data.get('style')}
- Items Required: {', '.join(request_data.get('items_required', []))}
- Item Quantities: {json.dumps(request_data.get('item_quantities', {}))}
- Color Preference: {request_data.get('color_preference', 'N/A')}
- Material Preference: {request_data.get('material_preference', 'N/A')}
- Brand Preference: {request_data.get('brand_preference', 'N/A')}
- Must-have Items: {request_data.get('must_have_items', 'N/A')}
- Avoid Items: {request_data.get('avoid_items', 'N/A')}

STRICT RULES:
1. The total estimated cost of all recommended items MUST NOT exceed ₹{request_data.get('budget')} INR.
2. Return ONLY valid JSON matching this exact structure:

{{
  "budget": {request_data.get('budget')},
  "total_estimated_cost": 48500,
  "remaining_budget": 1500,
  "budget_status": "within_budget",
  "allocated_budget": {{
    "furniture": 20000,
    "lighting": 7000,
    "decor": 8000,
    "storage": 10000,
    "miscellaneous": 3500
  }},
  "recommendations": [
    {{
      "name": "3-Seater Minimalist Fabric Sofa",
      "category": "Furniture",
      "estimated_price": 18500,
      "platform": "Pepperfry / Amazon",
      "reason": "Matches modern style and fits allocated furniture budget.",
      "style": "Modern",
      "budget_status": "within_budget",
      "search_url": "https://www.amazon.in/s?k=3+seater+minimalist+sofa"
    }}
  ],
  "summary": "Tailored modern living room recommendation staying strictly within your ₹{request_data.get('budget')} budget.",
  "tips": [
    "Prioritize key seating furniture before adding decorative lamps.",
    "Look out for seasonal sales on e-commerce platforms to save up to 15%."
  ],
  "cheaper_alternatives": []
}}
"""
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            raw_text = response.text
            cleaned_json = self._clean_json_response(raw_text)
            parsed = json.loads(cleaned_json)
            return parsed
        except Exception as e:
            logger.error(f"Gemini API error during home recommendation: {e}")
            return self._fallback_home_recommendations(request_data, error_msg=str(e))

    def generate_party_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate party event planning recommendations."""
        if not self._is_api_available():
            return self._fallback_party_recommendations(request_data)

        prompt = f"""
You are an expert party planner and event cost optimizer AI assistant.
Analyze the user's event details and generate personalized recommendations staying within the budget limit.

User Request:
- Total Budget: ₹{request_data.get('budget')} INR
- Number of Guests: {request_data.get('guests')}
- Event Type: {request_data.get('event_type')}
- Venue Preference: {request_data.get('venue_preference')}
- Location: {request_data.get('location')}
- Food Preference: {request_data.get('food_preference')}
- Decoration Style: {request_data.get('decoration_style')}
- Entertainment Preference: {request_data.get('entertainment_preference')}
- Accommodation Required: {request_data.get('accommodation_required')}

STRICT RULES:
1. Total estimated cost MUST NOT exceed ₹{request_data.get('budget')} INR.
2. Return ONLY valid JSON matching this structure:

{{
  "budget": {request_data.get('budget')},
  "total_estimated_cost": 95000,
  "remaining_budget": 5000,
  "budget_status": "within_budget",
  "allocated_budget": {{
    "venue": 30000,
    "food": 35000,
    "decoration": 15000,
    "entertainment": 10000,
    "miscellaneous": 5000
  }},
  "recommendations": [
    {{
      "name": "Multi-Cuisine Buffet Catering",
      "category": "Food",
      "estimated_price": 35000,
      "platform": "Swiggy Gourmet / Zomato Catering",
      "reason": "Includes starter, main course & desserts for {request_data.get('guests')} guests.",
      "style": "{request_data.get('food_preference')}",
      "budget_status": "within_budget",
      "search_url": "https://www.google.com/search?q=event+buffet+catering"
    }}
  ],
  "summary": "Complete event breakdown for your {request_data.get('event_type')} for {request_data.get('guests')} guests within ₹{request_data.get('budget')}.",
  "tips": ["Book catering at least 2 weeks in advance for volume discounts."],
  "cheaper_alternatives": []
}}
"""
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            parsed = json.loads(self._clean_json_response(response.text))
            return parsed
        except Exception as e:
            logger.error(f"Gemini API error during party recommendation: {e}")
            return self._fallback_party_recommendations(request_data, error_msg=str(e))

    def generate_jewelry_recommendations(
        self, request_data: Dict[str, Any], image_bytes: Optional[bytes] = None, image_mime: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Generate jewelry recommendations, optionally analyzing outfit image multimodally."""
        if not self._is_api_available():
            return self._fallback_jewelry_recommendations(request_data, image_bytes is not None)

        prompt = f"""
You are a high-end fashion stylist and jewelry recommendation expert.
Analyze the user's specifications and optional outfit image to provide matched jewelry recommendations.

User Request:
- Total Budget: ₹{request_data.get('budget')} INR
- Occasion: {request_data.get('occasion')}
- Jewelry Type: {request_data.get('jewelry_type')}
- Style Preference: {request_data.get('style')}
- Metal Preference: {request_data.get('metal_preference')}
- Color Preference: {request_data.get('color_preference', 'N/A')}
- Outfit Color: {request_data.get('outfit_color', 'N/A')}
- Additional Notes: {request_data.get('additional_requirements', 'N/A')}

CRITICAL MULTIMODAL INSTRUCTION:
If an outfit image is attached, analyze the visual dress color, fabric pattern, neckline/collar, and elegance level.
DO NOT detect, mention, or classify sensitive personal characteristics of any human in the image. Focus purely on garment colors, textures, and neckline style.

STRICT RULES:
1. Total estimated cost MUST NOT exceed ₹{request_data.get('budget')} INR.
2. Return ONLY valid JSON matching this structure:

{{
  "budget": {request_data.get('budget')},
  "total_estimated_cost": 4500,
  "remaining_budget": 500,
  "budget_status": "within_budget",
  "allocated_budget": {{
    "main_piece": 3000,
    "accessories": 1500
  }},
  "outfit_analysis": {{
    "analyzed_outfit_color": "{request_data.get('outfit_color') or 'Analyzed from image'}",
    "neckline_compatibility": "V-neck / Deep round compatible",
    "suggested_jewelry_tones": ["Gold", "Pearl"],
    "style_match": "High harmony with outfit tone"
  }},
  "recommendations": [
    {{
      "name": "22K Gold Plated Kundan Choker Necklace Set",
      "category": "Necklace",
      "estimated_price": 3800,
      "platform": "Myntra / CaratLane",
      "reason": "Complements the outfit color tone and fits the occasion.",
      "suggested_color": "Gold & Pearl",
      "suggested_material": "Gold Plated Brass / Kundan",
      "style": "{request_data.get('style')}",
      "budget_status": "within_budget",
      "search_url": "https://www.myntra.com/kundan-choker-set"
    }}
  ],
  "summary": "Stunning jewelry styling recommendations tailored to your outfit and ₹{request_data.get('budget')} budget.",
  "tips": ["Pair warm metal tones like gold with vibrant warm-colored outfits."],
  "cheaper_alternatives": []
}}
"""
        try:
            from google.genai import types
            contents = [prompt]
            if image_bytes:
                part = types.Part.from_bytes(data=image_bytes, mime_type=image_mime)
                contents.append(part)

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            parsed = json.loads(self._clean_json_response(response.text))
            return parsed
        except Exception as e:
            logger.error(f"Gemini API error during jewelry recommendation: {e}")
            return self._fallback_jewelry_recommendations(request_data, image_bytes is not None, error_msg=str(e))

    # --- FALLBACK / DEMO MODE ENGINES ---

    def _fallback_home_recommendations(self, request_data: Dict[str, Any], error_msg: Optional[str] = None) -> Dict[str, Any]:
        """Fallback recommendation generator for Home Interior when AI API is unavailable."""
        budget = float(request_data.get("budget", 50000))
        room_type = request_data.get("room_type", "Living Room")
        style = request_data.get("style", "Modern")
        
        catalog = get_demo_catalog_items("home")
        allocated = calculate_home_budget_breakdown(budget, request_data.get("items_required", []))
        
        selected_recs = []
        total_cost = 0.0
        
        # Pick relevant catalog items dynamically based on requested items or room
        for item in catalog:
            if total_cost + item["estimated_price"] <= budget:
                item_rec = item.copy()
                item_rec["reason"] = f"Fits well in a {style} {room_type} setup within your allocated category budget."
                item_rec["budget_status"] = "within_budget"
                selected_recs.append(item_rec)
                total_cost += item["estimated_price"]

        status, remaining = evaluate_budget_status(budget, total_cost)
        
        summary_prefix = f"[DEMO MODE] " if settings.DEMO_MODE or not self.api_key else ""
        return {
            "budget": budget,
            "total_estimated_cost": total_cost,
            "remaining_budget": remaining,
            "budget_status": status,
            "allocated_budget": allocated,
            "recommendations": selected_recs,
            "summary": f"{summary_prefix}PocketSmart AI calculated optimal recommendations for your {style} {room_type} totaling ₹{total_cost:,.2f}.",
            "tips": [
                "Mix ambient lighting with direct task lights for better room warmth.",
                "Choose modular furniture to easily reconfigure smaller spaces.",
                "Compare seller prices on Amazon and Pepperfry for discount coupons."
            ],
            "cheaper_alternatives": [],
            "demo_mode": True,
            "api_error": error_msg
        }

    def _fallback_party_recommendations(self, request_data: Dict[str, Any], error_msg: Optional[str] = None) -> Dict[str, Any]:
        """Fallback recommendation generator for Party Planning."""
        budget = float(request_data.get("budget", 100000))
        guests = int(request_data.get("guests", 50))
        event_type = request_data.get("event_type", "Birthday")
        accom = bool(request_data.get("accommodation_required", False))
        
        catalog = get_demo_catalog_items("party")
        allocated = calculate_party_budget_breakdown(budget, guests, accom)
        
        selected_recs = []
        total_cost = 0.0
        
        for item in catalog:
            if not accom and item["category"] == "Accommodation":
                continue
            if total_cost + item["estimated_price"] <= budget:
                item_rec = item.copy()
                item_rec["reason"] = f"Ideal service option for {guests} guests at a {event_type} event."
                item_rec["budget_status"] = "within_budget"
                selected_recs.append(item_rec)
                total_cost += item["estimated_price"]

        status, remaining = evaluate_budget_status(budget, total_cost)
        summary_prefix = "[DEMO MODE] " if settings.DEMO_MODE or not self.api_key else ""
        
        return {
            "budget": budget,
            "total_estimated_cost": total_cost,
            "remaining_budget": remaining,
            "budget_status": status,
            "allocated_budget": allocated,
            "recommendations": selected_recs,
            "summary": f"{summary_prefix}Curated package for your {event_type} for {guests} guests totaling ₹{total_cost:,.2f}.",
            "tips": [
                "Confirm guest RSVPs 5 days early to finalize exact food catering count.",
                "Utilize local playlist sound setups if venue includes built-in speakers."
            ],
            "cheaper_alternatives": [],
            "demo_mode": True,
            "api_error": error_msg
        }

    def _fallback_jewelry_recommendations(self, request_data: Dict[str, Any], has_image: bool = False, error_msg: Optional[str] = None) -> Dict[str, Any]:
        """Fallback recommendation generator for Jewelry styling."""
        budget = float(request_data.get("budget", 5000))
        occasion = request_data.get("occasion", "Wedding")
        jewelry_type = request_data.get("jewelry_type", "Necklace")
        outfit_color = request_data.get("outfit_color", "Royal Blue / Crimson")
        style = request_data.get("style", "Traditional")
        
        catalog = get_demo_catalog_items("jewelry")
        allocated = calculate_jewelry_budget_breakdown(budget, jewelry_type)
        
        selected_recs = []
        total_cost = 0.0
        
        for item in catalog:
            if total_cost + item["estimated_price"] <= budget:
                item_rec = item.copy()
                item_rec["reason"] = f"Complements your {outfit_color} outfit for a {occasion}."
                item_rec["suggested_color"] = "Antique Gold / Kundan"
                item_rec["suggested_material"] = "Brass Gold Plated"
                item_rec["budget_status"] = "within_budget"
                selected_recs.append(item_rec)
                total_cost += item["estimated_price"]

        status, remaining = evaluate_budget_status(budget, total_cost)
        summary_prefix = "[DEMO MODE] " if settings.DEMO_MODE or not self.api_key else ""
        
        outfit_analysis = {
            "analyzed_outfit_color": outfit_color if outfit_color else "Vibrant Tone (from Image)",
            "neckline_compatibility": "Open Neck / Deep Collar Compatible",
            "suggested_jewelry_tones": ["Antique Gold", "Pearl White"],
            "style_match": "Harmonious Contrast with Outfit" if has_image else "Selected for Occasion Elegance"
        }

        return {
            "budget": budget,
            "total_estimated_cost": total_cost,
            "remaining_budget": remaining,
            "budget_status": status,
            "allocated_budget": allocated,
            "outfit_analysis": outfit_analysis,
            "recommendations": selected_recs,
            "summary": f"{summary_prefix}Jewelry ensemble for {occasion} tailored to your {outfit_color} outfit totaling ₹{total_cost:,.2f}.",
            "tips": [
                "Store Kundan & Pearl pieces in airtight fabric pouches to prevent tarnish.",
                "Apply perfume and cosmetics BEFORE putting on gold plated jewelry."
            ],
            "cheaper_alternatives": [],
            "demo_mode": True,
            "api_error": error_msg
        }

gemini_service = GeminiService()
