
import pandas as pd
import geopandas as gpd
import os

FILE_CHARGERS = "data/raw/2023_2T_Punts_Recarrega_Vehicle_Electric.json"

print(f"Testing file: {FILE_CHARGERS}")
if not os.path.exists(FILE_CHARGERS):
    print("File not found via relative path, trying absolute...")
    # Try finding it relative to where script might be running
    FILE_CHARGERS = os.path.abspath(os.path.join(os.getcwd(), 'data', 'raw', '2023_2T_Punts_Recarrega_Vehicle_Electric.json'))
    print(f"Trying: {FILE_CHARGERS}")

try:
    print("Attempting gpd.read_file...")
    gdf = gpd.read_file(FILE_CHARGERS)
    print("Success with gpd.read_file!")
    print(gdf.head())
except Exception as e:
    print(f"gpd.read_file failed: {e}")
    
    try:
        print("Attempting pd.read_json...")
        df = pd.read_json(FILE_CHARGERS)
        print("Success with pd.read_json!")
        print(df.columns)
        
        if 'Station_lat' in df.columns and 'Station_lng' in df.columns:
            print("Found lat/lng columns. Converting to GeoDataFrame...")
            gdf = gpd.GeoDataFrame(
                df, 
                geometry=gpd.points_from_xy(df.Station_lng, df.Station_lat),
                crs="EPSG:4326"
            )
            print("Conversion successful!")
            print(gdf.head())
        else:
            print("Lat/Lng columns not found.")
            
    except Exception as e2:
        print(f"pd.read_json failed: {e2}")
