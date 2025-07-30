import geopandas as gpd

# Read the shapefile folder path
gdf = gpd.read_file("data/hotosm_sdn_health_facilities_points_shp/hotosm_sdn_health_facilities_points_shp.shp")

# Convert to GeoJSON or plain JSON
gdf.to_file("sudan_hospitals.geojson", driver="GeoJSON")

# OR to plain JSON
gdf.drop(columns='geometry').to_json("sudan_hospitals_data.json", orient="records")
