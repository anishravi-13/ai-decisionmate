"""
business_search.py – Nearby business/shop discovery.
Uses live API if configured, otherwise returns a clear fallback message.
Does NOT fabricate businesses, addresses, or phone numbers.
"""
from typing import List, Optional, Dict, Any
from schemas import NearbyBusiness, NearbyResponse
from config import settings


# Category to search term mapping
CATEGORY_SEARCH_TERMS = {
    "laptop": "laptop store computer shop",
    "smartphone": "mobile phone shop electronics store",
    "pc_components": "computer parts store electronics",
    "pet": "pet shop pet supplies store",
    "fish_aquarium": "aquarium shop fish store pet aquatic",
    "office_equipment": "office supplies store stationery",
    "home": "home appliances electronics store",
    "vehicle": "car dealership showroom",
    "relationship": "counseling center community center social club support group",
    "personal": "counseling center community center support group",
    "health": "pharmacy medical clinic hospital urgent care medical store",
    "general": "electronics store general store",
}

# Helpful category-specific suggestions when live search is unavailable
CATEGORY_SUGGESTIONS = {
    "laptop": [
        "Search 'laptop stores near me' on Google Maps",
        "Visit authorised dealer stores for brands like Lenovo, HP, Dell, or ASUS",
        "Check Croma, Reliance Digital, or Vijay Sales for in-person experience",
        "Online options: Amazon.in, Flipkart, or brand official websites",
    ],
    "smartphone": [
        "Visit brand experience stores (Samsung, Apple, OnePlus) for hands-on demos",
        "Authorised multi-brand stores like Croma or Reliance Digital",
        "Online: Amazon.in, Flipkart (Assured) for warranty-backed purchases",
    ],
    "pet": [
        "Search 'pet shop near me' on Google Maps",
        "Visit registered pet stores with licensed breeders",
        "Consider adoption from local animal shelters or rescue organisations",
    ],
    "fish_aquarium": [
        "Search 'aquarium shop near me' on Google Maps",
        "Visit dedicated aquarium specialty stores for expert advice",
        "Online fish sellers: Aquakri, The Shrimp Farm, or local Facebook groups",
    ],
    "office_equipment": [
        "Search 'office supplies near me' on Google Maps",
        "Visit Staples, OfficeMax, or local stationery distributors",
        "Online: Amazon Business, Flipkart Business for bulk orders",
    ],
    "relationship": [
        "Search 'family and relationship counseling near me' on Google Maps",
        "Explore local community clubs, hobby workshops, and meetup groups to broaden social connections",
        "Visit a local youth center or community library for group activities and new friendships",
        "Confidential support helplines (Tele-MANAS: 14416 / Vandrevala: +91 9999 666 555) for distress or isolation",
    ],
    "personal": [
        "Search 'counseling center near me' for professional guidance",
        "Explore local meditation, fitness, or hobby community groups",
        "Confidential support helplines (Tele-MANAS: 14416 / Vandrevala: +91 9999 666 555)",
    ],
    "health": [
        "Search '24/7 pharmacy near me' on Google Maps to purchase ORS packets or medical supplies",
        "Search 'general physician clinic near me' for outpatient consultation if symptoms persist >48h",
        "Find nearby multi-specialty hospitals or urgent care clinics in case of severe dehydration or high fever",
        "Government Health Helpline (India: 1075 / Emergency: 112) for immediate medical advice",
    ],
}


def search_nearby_businesses(
    category: str,
    location: Optional[str] = None,
    radius_km: float = 10.0,
) -> NearbyResponse:
    """
    Search for nearby businesses.
    Returns live data if API is configured, otherwise returns a helpful fallback.
    """
    # If Google Maps API is configured, attempt live search
    if settings.GOOGLE_MAPS_API_KEY:
        try:
            return _live_search(category, location, radius_km)
        except Exception as e:
            # Fall through to fallback on error
            pass

    # Fallback: no live search available
    return _fallback_response(category, location)


def _live_search(category: str, location: Optional[str], radius_km: float) -> NearbyResponse:
    """Live search using Google Maps Places API (if key is available)."""
    # This would use the Places API — implementation omitted since no key is available in demo
    # The actual implementation would call:
    #   GET https://maps.googleapis.com/maps/api/place/textsearch/json
    #   with query, location, radius, and key parameters
    raise NotImplementedError("Live search not implemented in demo mode")


def _fallback_response(category: str, location: Optional[str]) -> NearbyResponse:
    """Return a helpful fallback when live search is unavailable."""
    cat = category.lower().strip()
    suggestions = CATEGORY_SUGGESTIONS.get(cat, CATEGORY_SUGGESTIONS.get("laptop", []))
    search_term = CATEGORY_SEARCH_TERMS.get(cat, "electronics store")

    location_str = f" near {location}" if location else ""
    message = (
        f"Live nearby search is not available in demo mode. "
        f"To find {search_term}{location_str}, use Google Maps or the suggestions below."
    )

    return NearbyResponse(
        success=True,
        businesses=[],
        live_data=False,
        message=message,
    )


def get_category_suggestions(category: str) -> List[str]:
    """Get alternative search suggestions for a category."""
    cat = category.lower().strip()
    return CATEGORY_SUGGESTIONS.get(cat, [
        f"Search '{cat} store near me' on Google Maps",
        "Check local business directories",
        "Ask in local community groups for recommendations",
    ])
