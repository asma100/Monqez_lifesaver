import geopandas as gpd
import json

# Load the shapefile
gdf = gpd.read_file("hotosm_sdn_health_facilities_polygons_shp.shp")

# Optional: view sample columns
print(gdf.columns)

hospitals = []

for _, row in gdf.iterrows():
    geometry = row["geometry"]
    
    # Compute the centroid of the polygon
    if geometry:
        centroid = geometry.centroid
        lat = centroid.y
        lon = centroid.x
    else:
        lat, lon = None, None

    hospitals.append({
        "name": row.get("name", "Unknown"),
        "type": row.get("amenity", row.get("healthcare", "Unknown")),
        "latitude": lat,
        "longitude": lon,
        "address": "Unknown",
        "contact": "Unknown",
        "working_hours": "Unknown"
    })

# Save to JSON
with open("sudan_hospitals.json", "w", encoding='utf-8') as f:
    json.dump(hospitals, f, ensure_ascii=False, indent=2)

print(f"✅ Exported {len(hospitals)} hospitals with centroid coordinates.")
