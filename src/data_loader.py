"""
Data loading utilities for EV Hub Optimization project.

This module provides functions for loading various data sources including:
- Geographic data (GeoJSON, JSON)
- CSV files (vehicles, income, chargers)
- Automatic path resolution and error handling
"""

import os
import pandas as pd
import geopandas as gpd
from typing import Optional, Tuple
from . import config


def get_data_dir(data_type: str = 'raw') -> str:
    """
    Get the appropriate data directory path with automatic resolution.
    
    Tries multiple possible paths relative to current working directory
    to handle different execution contexts (notebooks, scripts, tests).
    
    Args:
        data_type: Type of data directory ('raw' or 'processed')
        
    Returns:
        Path to the data directory
        
    Raises:
        FileNotFoundError: If no valid data directory is found
    """
    if data_type == 'raw':
        possible_paths = [
            config.RAW_DATA_DIR,
            os.path.join('..', 'data', 'raw'),
            os.path.join('..', '..', 'data', 'raw'),
            os.path.join(os.getcwd(), 'data', 'raw')
        ]
    elif data_type == 'processed':
        possible_paths = [
            config.PROCESSED_DATA_DIR,
            os.path.join('..', 'data', 'processed'),
            os.path.join('..', '..', 'data', 'processed'),
            os.path.join(os.getcwd(), 'data', 'processed')
        ]
    else:
        raise ValueError(f"Invalid data_type: {data_type}. Must be 'raw' or 'processed'.")
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError(
        f"Could not find {data_type} data directory. "
        f"Tried paths: {possible_paths}"
    )


def load_neighborhoods(
    file_name: Optional[str] = None,
    target_crs: str = config.TARGET_CRS
) -> gpd.GeoDataFrame:
    """
    Load neighborhood boundary data.
    
    Args:
        file_name: Name of the file to load. If None, uses default from config.
        target_crs: Target coordinate reference system. Default is EPSG:4326.
        
    Returns:
        GeoDataFrame containing neighborhood geometries
        
    Raises:
        FileNotFoundError: If the file cannot be found
        ValueError: If the file cannot be loaded as geographic data
    """
    if file_name is None:
        file_name = config.FILE_GEOMETRY
    
    data_dir = get_data_dir('raw')
    file_path = os.path.join(data_dir, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Neighborhood file not found: {file_path}")
    
    try:
        gdf = gpd.read_file(file_path)
        
        # Standardize CRS if needed
        if gdf.crs is not None and gdf.crs != target_crs:
            gdf = gdf.to_crs(target_crs)
        elif gdf.crs is None:
            gdf.set_crs(target_crs, inplace=True)
            
        return gdf
    except Exception as e:
        raise ValueError(f"Error loading neighborhood data from {file_path}: {str(e)}")


def load_chargers(
    file_name: Optional[str] = None,
    target_crs: str = config.TARGET_CRS
) -> gpd.GeoDataFrame:
    """
    Load EV charging station data.
    
    Handles both GeoJSON and JSON formats. For JSON format, creates point
    geometries from Station_lat and Station_lng columns.
    
    Args:
        file_name: Name of the file to load. If None, uses default from config.
        target_crs: Target coordinate reference system. Default is EPSG:4326.
        
    Returns:
        GeoDataFrame containing charging station locations
        
    Raises:
        FileNotFoundError: If the file cannot be found
        ValueError: If the file format is invalid
    """
    if file_name is None:
        file_name = config.FILE_CHARGERS_JSON
    
    data_dir = get_data_dir('raw')
    file_path = os.path.join(data_dir, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Chargers file not found: {file_path}")
    
    try:
        # Try loading as GeoDataFrame first
        gdf = gpd.read_file(file_path)
        
        # Standardize CRS
        if gdf.crs is not None and gdf.crs != target_crs:
            gdf = gdf.to_crs(target_crs)
        elif gdf.crs is None:
            gdf.set_crs(target_crs, inplace=True)
            
        return gdf
    except Exception:
        # If that fails, try as regular JSON with lat/lng columns
        try:
            df = pd.read_json(file_path)
            
            # Check for required columns
            if 'Station_lat' not in df.columns or 'Station_lng' not in df.columns:
                raise ValueError(
                    "JSON file must contain 'Station_lat' and 'Station_lng' columns"
                )
            
            # Create GeoDataFrame from coordinates
            gdf = gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df.Station_lng, df.Station_lat),
                crs=target_crs
            )
            
            return gdf
        except Exception as e:
            raise ValueError(f"Error loading chargers data from {file_path}: {str(e)}")


def load_vehicles(
    file_name: Optional[str] = None,
    filter_ev_types: bool = False
) -> pd.DataFrame:
    """
    Load vehicle census data.
    
    Args:
        file_name: Name of the file to load. If None, uses default from config.
        filter_ev_types: If True, filter to only EV propulsion types
        
    Returns:
        DataFrame containing vehicle counts by neighborhood and propulsion type
        
    Raises:
        FileNotFoundError: If the file cannot be found
    """
    if file_name is None:
        file_name = config.FILE_VEHICLES_PROPULSION
    
    data_dir = get_data_dir('raw')
    file_path = os.path.join(data_dir, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Vehicles file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    
    if filter_ev_types and 'Propulsio' in df.columns:
        df = df[df['Propulsio'].isin(config.EV_PROPULSION_TYPES)]
    
    return df


def load_income(file_name: Optional[str] = None) -> pd.DataFrame:
    """
    Load household income data.
    
    Args:
        file_name: Name of the file to load. If None, uses default from config.
        
    Returns:
        DataFrame containing income data by neighborhood
        
    Raises:
        FileNotFoundError: If the file cannot be found
    """
    if file_name is None:
        file_name = config.FILE_INCOME
    
    data_dir = get_data_dir('raw')
    file_path = os.path.join(data_dir, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Income file not found: {file_path}")
    
    return pd.read_csv(file_path)


def load_processed_barrios(
    file_name: Optional[str] = None
) -> gpd.GeoDataFrame:
    """
    Load processed neighborhood data with demand scores.
    
    Args:
        file_name: Name of the file to load. If None, uses default from config.
        
    Returns:
        GeoDataFrame containing neighborhoods with demand metrics
        
    Raises:
        FileNotFoundError: If the file cannot be found
    """
    if file_name is None:
        file_name = config.FILE_BARRIOS_WITH_DEMAND
    
    data_dir = get_data_dir('processed')
    file_path = os.path.join(data_dir, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Processed barrios file not found: {file_path}")
    
    return gpd.read_file(file_path)


def export_geojson(
    gdf: gpd.GeoDataFrame,
    file_name: str,
    data_type: str = 'processed'
) -> str:
    """
    Export GeoDataFrame to GeoJSON format.
    
    Args:
        gdf: GeoDataFrame to export
        file_name: Name of the output file
        data_type: Type of data directory ('raw' or 'processed')
        
    Returns:
        Path to the exported file
        
    Raises:
        OSError: If the file cannot be written
    """
    data_dir = get_data_dir(data_type)
    file_path = os.path.join(data_dir, file_name)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    gdf.to_file(file_path, driver='GeoJSON')
    return file_path


def export_csv(
    df: pd.DataFrame,
    file_name: str,
    data_type: str = 'processed',
    index: bool = False
) -> str:
    """
    Export DataFrame to CSV format.
    
    Args:
        df: DataFrame to export
        file_name: Name of the output file
        data_type: Type of data directory ('raw' or 'processed')
        index: Whether to include the index in the output
        
    Returns:
        Path to the exported file
        
    Raises:
        OSError: If the file cannot be written
    """
    data_dir = get_data_dir(data_type)
    file_path = os.path.join(data_dir, file_name)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    df.to_csv(file_path, index=index)
    return file_path
