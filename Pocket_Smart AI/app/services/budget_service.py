from typing import Dict, List, Any, Tuple
import urllib.parse

# Local Demo Catalog with Realistic Prices and Safe Search Links
DEMO_CATALOG = {
    "home": [
        {"id": "h1", "name": "3-Seater Fabric Sofa Set", "category": "Furniture", "estimated_price": 18500, "platform": "Pepperfry / Amazon", "style": "Modern", "search_query": "3 seater sofa set modern"},
        {"id": "h2", "name": "Minimalist Wooden Dining Table Set (4 Chairs)", "category": "Furniture", "estimated_price": 14000, "platform": "IKEA / Flipkart", "style": "Minimalist", "search_query": "4 seater dining table set"},
        {"id": "h3", "name": "Ergonomic Mesh Study Chair & Desk", "category": "Furniture", "estimated_price": 8500, "platform": "Amazon", "style": "Modern", "search_query": "ergonomic study desk chair set"},
        {"id": "h4", "name": "Smart BLDC Energy Saving Ceiling Fan", "category": "Lighting", "estimated_price": 3200, "platform": "Flipkart", "style": "Modern", "search_query": "BLDC ceiling fan smart"},
        {"id": "h5", "name": "Warm Ambient LED Chandelier / Pendant Light", "category": "Lighting", "estimated_price": 2800, "platform": "Amazon", "style": "Luxury", "search_query": "warm LED pendant light fixture"},
        {"id": "h6", "name": "Set of 3 Minimalist Canvas Wall Art Prints", "category": "Decor", "estimated_price": 1500, "platform": "Myntra / Pepperfry", "style": "Minimalist", "search_query": "framed canvas wall art set"},
        {"id": "h7", "name": "Blackout Thermal Insulated Window Curtains (Pair)", "category": "Curtains", "estimated_price": 1800, "platform": "Amazon", "style": "Scandinavian", "search_query": "blackout window curtains pair"},
        {"id": "h8", "name": "Soft Microfiber Area Rug (5x7 ft)", "category": "Rugs", "estimated_price": 2400, "platform": "Flipkart", "style": "Scandinavian", "search_query": "microfiber area rug 5x7"},
        {"id": "h9", "name": "Modular Engineered Wood Storage Cabinet", "category": "Storage", "estimated_price": 6500, "platform": "IKEA", "style": "Modern", "search_query": "wooden modular storage cabinet"},
        {"id": "h10", "name": "Ceramic Decorative Vases & Table Accents", "category": "Decor", "estimated_price": 950, "platform": "Amazon", "style": "Modern", "search_query": "ceramic decorative vase set"}
    ],
    "party": [
        {"id": "p1", "name": "Boutique AC Party Hall / Banquet Venue", "category": "Venue", "estimated_price": 25000, "platform": "OYO / VenueBooking", "style": "Banquet", "search_query": "party banquet hall rental"},
        {"id": "p2", "name": "Multi-Cuisine Buffet Catering (Per Head Package)", "category": "Food", "estimated_price": 30000, "platform": "Zomato Catering / Swiggy Gourmet", "style": "Buffet", "search_query": "event buffet catering service"},
        {"id": "p3", "name": "Custom Birthday / Anniversary Designer Cake (2-Tier)", "category": "Food", "estimated_price": 2500, "platform": "Swiggy / Ferns N Petals", "style": "Celebration", "search_query": "designer celebration cake 2 tier"},
        {"id": "p4", "name": "Themed Balloon Arch & Backdrop Floral Decor", "category": "Decoration", "estimated_price": 8500, "platform": "Local Event Decorator", "style": "Theme Decor", "search_query": "theme balloon arch decoration"},
        {"id": "p5", "name": "Professional DJ Setup with Disco Lights & Sound System", "category": "Entertainment", "estimated_price": 12000, "platform": "BookMyShow / ArtistBooking", "style": "DJ", "search_query": "party DJ sound and lighting setup"},
        {"id": "p6", "name": "Interactive Emcee / Party Games Host", "category": "Entertainment", "estimated_price": 5000, "platform": "EventHost", "style": "Games", "search_query": "party anchor games host"},
        {"id": "p7", "name": "Budget AC Hotel Guest Rooms (Package)", "category": "Accommodation", "estimated_price": 15000, "platform": "OYO / MakeMyTrip", "style": "Hotel", "search_query": "OYO budget hotel rooms package"},
        {"id": "p8", "name": "Instant Photo Booth & Props Rental", "category": "Entertainment", "estimated_price": 4500, "platform": "Local Vendor", "style": "Fun", "search_query": "photo booth rental props party"}
    ],
    "jewelry": [
        {"id": "j1", "name": "22K Gold Plated Kundan Choker Necklace Set with Earrings", "category": "Necklace", "estimated_price": 3800, "platform": "Myntra / CaratLane", "style": "Traditional", "search_query": "kundan choker necklace set gold plated"},
        {"id": "j2", "name": "925 Sterling Silver Cubic Zirconia Drop Earrings", "category": "Earrings", "estimated_price": 1800, "platform": "GIVA / Amazon", "style": "Modern", "search_query": "925 sterling silver drop earrings"},
        {"id": "j3", "name": "Delicate Rose Gold Adjustable Charm Bracelet", "category": "Bracelet", "estimated_price": 1250, "platform": "Myntra / GIVA", "style": "Minimal", "search_query": "rose gold charm bracelet adjustable"},
        {"id": "j4", "name": "Solitaire Crystal Accent Adjustable Cocktail Ring", "category": "Ring", "estimated_price": 950, "platform": "Amazon", "style": "Statement", "search_query": "solitaire crystal cocktail ring"},
        {"id": "j5", "name": "Traditional Antique Gold Finish Velvet Bangle Set (Pack of 4)", "category": "Bangles", "estimated_price": 1400, "platform": "Flipkart", "style": "Traditional", "search_query": "antique gold finish bangles set"},
        {"id": "j6", "name": "Royalty Pearl & Emerald Polki Bridal / Party Full Jewellery Set", "category": "Full set", "estimated_price": 7500, "platform": "Myntra / Tanishq Mia", "style": "Elegant", "search_query": "polki pearl jewelry set elegant"},
        {"id": "j7", "name": "Sleek Geometric Platinum-Plated Stud Earrings", "category": "Earrings", "estimated_price": 850, "platform": "GIVA / Amazon", "style": "Minimal", "search_query": "platinum plated geometric stud earrings"}
    ]
}

def generate_search_url(query: str, platform: str) -> str:
    """Generate safe e-commerce search URL."""
    encoded_query = urllib.parse.quote(query)
    if "Amazon" in platform:
        return f"https://www.amazon.in/s?k={encoded_query}"
    elif "Flipkart" in platform:
        return f"https://www.flipkart.com/search?q={encoded_query}"
    elif "Myntra" in platform:
        return f"https://www.myntra.com/{encoded_query}"
    elif "IKEA" in platform:
        return f"https://www.ikea.com/in/en/search/?q={encoded_query}"
    elif "Zomato" in platform or "Swiggy" in platform:
        return f"https://www.google.com/search?q={encoded_query}"
    elif "OYO" in platform:
        return f"https://www.google.com/search?q={encoded_query}"
    else:
        return f"https://www.google.com/search?q={encoded_query}"

def calculate_home_budget_breakdown(total_budget: float, items_required: List[str]) -> Dict[str, float]:
    """Calculate intelligent budget allocation per category for home interior planning."""
    # Standard weighting ratios (sum = 1.0)
    weights = {
        "furniture": 0.40,
        "lighting": 0.15,
        "decor": 0.15,
        "storage": 0.15,
        "miscellaneous": 0.15
    }
    
    # Adjust weights based on requested items while ensuring total sum == 1.0
    items_lower = [i.lower() for i in items_required]
    if any(k in items_lower for k in ["sofa", "dining table", "bed"]):
        weights = {
            "furniture": 0.48,
            "lighting": 0.13,
            "decor": 0.13,
            "storage": 0.13,
            "miscellaneous": 0.13
        }
        
    allocation = {cat: round(total_budget * pct, 2) for cat, pct in weights.items()}
    return allocation

def calculate_party_budget_breakdown(total_budget: float, guests: int, accommodation_required: bool) -> Dict[str, float]:
    """Calculate budget breakdown for party planner."""
    if accommodation_required:
        weights = {
            "venue": 0.25,
            "food": 0.35,
            "decoration": 0.15,
            "entertainment": 0.10,
            "accommodation": 0.15
        }
    else:
        weights = {
            "venue": 0.30,
            "food": 0.40,
            "decoration": 0.15,
            "entertainment": 0.10,
            "miscellaneous": 0.05
        }
    return {cat: round(total_budget * pct, 2) for cat, pct in weights.items()}

def calculate_jewelry_budget_breakdown(total_budget: float, jewelry_type: str) -> Dict[str, float]:
    """Calculate budget breakdown for jewelry planner."""
    if jewelry_type.lower() in ["full set", "set"]:
        weights = {
            "main_piece": 0.50,
            "earrings": 0.25,
            "ring_bracelet": 0.15,
            "accessories": 0.10
        }
    elif jewelry_type.lower() == "necklace":
        weights = {
            "necklace": 0.70,
            "matching_earrings": 0.20,
            "accessories": 0.10
        }
    else:
        weights = {
            jewelry_type.lower(): 0.80,
            "accessories": 0.20
        }
    return {cat: round(total_budget * pct, 2) for cat, pct in weights.items()}

def evaluate_budget_status(total_budget: float, total_estimated_cost: float) -> Tuple[str, float]:
    """Evaluate budget status ('within_budget', 'near_budget', 'over_budget') and compute remaining balance."""
    remaining = total_budget - total_estimated_cost
    ratio = total_estimated_cost / total_budget if total_budget > 0 else 1.0
    
    if ratio <= 0.90:
        status = "within_budget"
    elif ratio <= 1.00:
        status = "near_budget"
    else:
        status = "over_budget"
        
    return status, round(remaining, 2)

def get_demo_catalog_items(planner_type: str) -> List[Dict[str, Any]]:
    """Retrieve demo catalog items populated with search URLs."""
    items = DEMO_CATALOG.get(planner_type, [])
    processed = []
    for item in items:
        item_copy = item.copy()
        item_copy["search_url"] = generate_search_url(item_copy["search_query"], item_copy["platform"])
        processed.append(item_copy)
    return processed
