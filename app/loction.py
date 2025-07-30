import json
from geopy.distance import geodesic
import json
from geopy.distance import geodesic

def get_top_7_hospitals(user_coords, json_path="data.json"):
    """
    Returns the 7 closest hospitals to the user's location with full info.
    
    Parameters:
    - user_coords: tuple of (lat, lon)
    - json_path: path to the hospital JSON file
    
    Returns:
    - List of 7 hospital dicts sorted by proximity
    """
    # Load hospitals
    with open(json_path, "r", encoding="utf-8") as f:
        hospital_list = json.load(f)

    # Add distance to each hospital
    for hospital in hospital_list:
        hospital_coords = (hospital["latitude"], hospital["longitude"])
        hospital["distance_km"] = geodesic(user_coords, hospital_coords).km

    # Sort and get top 7
    top_7 = sorted(hospital_list, key=lambda h: h["distance_km"])[:7]
    
    return top_7
