from langchain_core.tools import tool

from .google_api import place_recommender


@tool
def geocode_city(location: str) -> str:
    """Convert a 'City, Country' string to lat,lng coordinates.
    Returns a string like '44.8,20.4' or an error message if geocoding fails."""
    result = place_recommender.find_place(location)
    return result or "Could not geocode that location."


@tool
def find_venue(lat_lng: str, query: str) -> str:
    """Find a venue near the given lat,lng coordinates using a Google Places search query.
    The query should capture the user's preferences, e.g. 'quiet jazz bar',
    'Italian restaurant outdoor seating', 'craft beer bar live music'.
    Returns an HTML link to the venue, or an error message if nothing found."""
    result = place_recommender.get_recs(lat_lng, q=query)
    if not result:
        return "No places found."
    return f'<a href="{result["link"]}">{result["name"]}</a>'
