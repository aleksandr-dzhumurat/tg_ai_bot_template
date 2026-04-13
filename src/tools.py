from langchain_core.tools import tool

from .google_api import place_recommender


@tool
def geocode_city(location: str) -> str:
    """Convert a 'City, Country' string to lat,lng coordinates.
    Returns a string like '44.8,20.4' or an error message if geocoding fails."""
    result = place_recommender.find_place(location)
    return result or "Could not geocode that location."


@tool
def find_beer_pub(lat_lng: str, craft: bool = False) -> dict:
    """Find a beer pub or craft bar near the given lat,lng coordinates.
    Set craft=True if the user prefers craft beer.
    Returns a dict with 'name' and 'link', or an error dict if nothing found."""
    q = "craft beer bar" if craft else "beer pub"
    result = place_recommender.get_recs(lat_lng, q=q)
    return result or {"error": "No places found."}
