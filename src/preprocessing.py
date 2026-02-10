"""
Data preprocessing utilities for EV Hub Optimization project.

This module provides functions for:
- Standardizing data formats
- Aggregating data by neighborhood
- Calculating demand scores
- Spatial joins and merges
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Optional, List
from . import config


def standardize_barri_id(
    df: pd.DataFrame,
    source_column: str
) -> pd.DataFrame:
    """
    Standardize Barri_ID column across different data sources.
    
    Args:
        df: DataFrame to process
        source_column: Name of the source column containing neighborhood IDs
        
    Returns:
        DataFrame with standardized Barri_ID column
    """
    df = df.copy()
    
    # Convert to numeric, handling different formats
    if source_column in df.columns:
        # Try direct conversion first
        df[config.COL_BARRI_ID] = pd.to_numeric(
            df[source_column].astype(str).str.strip(),
            errors='coerce'
        ).astype('Int64')
    
    return df


def aggregate_income_by_barrio(df_income: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate income data by neighborhood.
    
    Args:
        df_income: Raw income DataFrame
        
    Returns:
        DataFrame with average income per neighborhood
    """
    df = standardize_barri_id(df_income, 'Codi_Barri')
    
    # Group by Barri_ID and calculate mean income
    df_agg = df.groupby(config.COL_BARRI_ID)['Import_Euros'].mean().reset_index()
    df_agg.rename(columns={'Import_Euros': config.COL_AVG_INCOME}, inplace=True)
    
    return df_agg


def aggregate_vehicles_by_barrio(
    df_vehicles: pd.DataFrame,
    propulsion_types: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Aggregate vehicle data by neighborhood.
    
    Args:
        df_vehicles: Raw vehicle DataFrame
        propulsion_types: List of propulsion types to filter. If None, includes all.
        
    Returns:
        DataFrame with vehicle counts per neighborhood
    """
    df = standardize_barri_id(df_vehicles, 'Codi_Barri')
    
    # Filter by propulsion type if specified
    if propulsion_types and 'Propulsio' in df.columns:
        df = df[df['Propulsio'].isin(propulsion_types)]
    
    # Group by Barri_ID and sum vehicle counts
    df_agg = df.groupby(config.COL_BARRI_ID)['Nombre'].sum().reset_index()
    df_agg.rename(columns={'Nombre': config.COL_TOTAL_VEHICLES}, inplace=True)
    
    return df_agg


def calculate_ev_counts(df_vehicles: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate electric vehicle counts by neighborhood.
    
    Args:
        df_vehicles: Raw vehicle DataFrame
        
    Returns:
        DataFrame with EV counts per neighborhood
    """
    df = standardize_barri_id(df_vehicles, 'Codi_Barri')
    
    # Filter to EV propulsion types
    if 'Propulsio' in df.columns:
        df_ev = df[df['Propulsio'].isin(config.EV_PROPULSION_TYPES)]
        
        # Group and sum
        df_agg = df_ev.groupby(config.COL_BARRI_ID)['Nombre'].sum().reset_index()
        df_agg.rename(columns={'Nombre': config.COL_EV_COUNT}, inplace=True)
        
        return df_agg
    else:
        # Return empty DataFrame with correct structure
        return pd.DataFrame({
            config.COL_BARRI_ID: [],
            config.COL_EV_COUNT: []
        })


def spatial_join_chargers(
    gdf_chargers: gpd.GeoDataFrame,
    gdf_barrios: gpd.GeoDataFrame
) -> pd.DataFrame:
    """
    Perform spatial join to count chargers per neighborhood.
    
    Args:
        gdf_chargers: GeoDataFrame of charging stations
        gdf_barrios: GeoDataFrame of neighborhoods
        
    Returns:
        DataFrame with charger counts per neighborhood
    """
    # Ensure both use same CRS
    if gdf_chargers.crs != gdf_barrios.crs:
        gdf_chargers = gdf_chargers.to_crs(gdf_barrios.crs)
    
    # Spatial join
    gdf_joined = gpd.sjoin(
        gdf_chargers,
        gdf_barrios[[config.COL_BARRI_ID, config.COL_GEOMETRY]],
        how='left',
        predicate='within'
    )
    
    # Count chargers per neighborhood
    chargers_count = gdf_joined.groupby(config.COL_BARRI_ID).size().reset_index(
        name=config.COL_CHARGER_COUNT
    )
    
    return chargers_count


def create_master_dataframe(
    gdf_barrios: gpd.GeoDataFrame,
    df_income: Optional[pd.DataFrame] = None,
    df_vehicles: Optional[pd.DataFrame] = None,
    df_ev_counts: Optional[pd.DataFrame] = None,
    df_chargers: Optional[pd.DataFrame] = None
) -> gpd.GeoDataFrame:
    """
    Create master GeoDataFrame by merging all data sources.
    
    Args:
        gdf_barrios: Base GeoDataFrame with neighborhood geometries
        df_income: Income data (optional)
        df_vehicles: Vehicle counts data (optional)
        df_ev_counts: EV counts data (optional)
        df_chargers: Charger counts data (optional)
        
    Returns:
        Merged GeoDataFrame with all metrics
    """
    # Start with base barrios
    master = gdf_barrios[[config.COL_BARRI_ID, config.COL_BARRI_NAME, config.COL_GEOMETRY]].copy()
    
    # Merge income data
    if df_income is not None:
        master = master.merge(df_income, on=config.COL_BARRI_ID, how='left')
    
    # Merge vehicle data
    if df_vehicles is not None:
        master = master.merge(df_vehicles, on=config.COL_BARRI_ID, how='left')
    
    # Merge EV counts
    if df_ev_counts is not None:
        master = master.merge(df_ev_counts, on=config.COL_BARRI_ID, how='left')
    
    # Merge charger counts
    if df_chargers is not None:
        master = master.merge(df_chargers, on=config.COL_BARRI_ID, how='left')
    
    return master


def normalize_column(
    df: pd.DataFrame,
    column: str,
    output_column: Optional[str] = None
) -> pd.DataFrame:
    """
    Normalize a column using MinMaxScaler.
    
    Args:
        df: DataFrame to process
        column: Name of column to normalize
        output_column: Name for normalized column. If None, uses 'Norm_{column}'
        
    Returns:
        DataFrame with normalized column added
    """
    df = df.copy()
    
    if output_column is None:
        output_column = f'Norm_{column}'
    
    # Fill NaN values with 0 before scaling
    values = df[[column]].fillna(0)
    
    # Scale to [0, 1]
    scaler = MinMaxScaler()
    df[output_column] = scaler.fit_transform(values)
    
    return df


def calculate_demand_score(
    gdf: gpd.GeoDataFrame,
    weight_ev: float = config.WEIGHT_EV_COUNT,
    weight_income: float = config.WEIGHT_INCOME,
    weight_vehicles: float = config.WEIGHT_TOTAL_VEHICLES,
    base: float = config.DEMAND_SCORE_BASE
) -> gpd.GeoDataFrame:
    """
    Calculate demand score for each neighborhood.
    
    Args:
        gdf: GeoDataFrame with income, vehicle, and EV data
        weight_ev: Weight for EV count (default from config)
        weight_income: Weight for income (default from config)
        weight_vehicles: Weight for total vehicles (default from config)
        base: Base scaling factor (default from config)
        
    Returns:
        GeoDataFrame with demand score added
    """
    gdf = gdf.copy()
    
    # Normalize each metric
    gdf = normalize_column(gdf, config.COL_AVG_INCOME, 'Norm_Income')
    gdf = normalize_column(gdf, config.COL_TOTAL_VEHICLES, 'Norm_Vehicles')
    gdf = normalize_column(gdf, config.COL_EV_COUNT, 'Norm_EVs')
    
    # Calculate weighted demand score
    gdf[config.COL_DEMAND_SCORE] = (
        gdf['Norm_EVs'] * weight_ev +
        gdf['Norm_Income'] * weight_income +
        gdf['Norm_Vehicles'] * weight_vehicles
    ) * base
    
    return gdf


def calculate_unmet_demand(
    gdf: gpd.GeoDataFrame,
    supply_impact: float = config.SUPPLY_IMPACT
) -> gpd.GeoDataFrame:
    """
    Calculate unmet demand considering existing charger supply.
    
    Args:
        gdf: GeoDataFrame with demand scores and charger counts
        supply_impact: Impact factor for existing supply (default from config)
        
    Returns:
        GeoDataFrame with unmet demand added
    """
    gdf = gdf.copy()
    
    # Normalize supply (charger count)
    gdf = normalize_column(gdf, config.COL_CHARGER_COUNT, 'Norm_Supply')
    
    # Calculate unmet demand (demand minus supply impact, clipped at 0)
    gdf[config.COL_UNMET_DEMAND] = (
        gdf[config.COL_DEMAND_SCORE] - gdf['Norm_Supply'] * supply_impact
    ).clip(lower=0)
    
    return gdf


def calculate_centroids_with_crs_transform(
    gdf: gpd.GeoDataFrame,
    projected_crs: str = config.PROJECTED_CRS,
    target_crs: str = config.TARGET_CRS
) -> gpd.GeoDataFrame:
    """
    Calculate centroids with proper CRS transformation to avoid warnings.
    
    This function:
    1. Converts to a projected CRS (EPSG:25831 for Barcelona)
    2. Calculates centroids in the projected CRS
    3. Converts back to geographic CRS (EPSG:4326)
    4. Extracts latitude and longitude
    
    Args:
        gdf: GeoDataFrame with polygon geometries
        projected_crs: Projected CRS for accurate centroid calculation
        target_crs: Target geographic CRS for output coordinates
        
    Returns:
        GeoDataFrame with 'lat' and 'lng' columns added
    """
    gdf = gdf.copy()
    
    # Store original CRS
    original_crs = gdf.crs
    
    # Convert to projected CRS for accurate centroid calculation
    gdf_projected = gdf.to_crs(projected_crs)
    
    # Calculate centroids in projected CRS
    centroids_projected = gdf_projected.geometry.centroid
    
    # Create GeoDataFrame with centroids
    centroids_gdf = gpd.GeoDataFrame(
        geometry=centroids_projected,
        crs=projected_crs
    )
    
    # Convert centroids back to target CRS
    centroids_target = centroids_gdf.to_crs(target_crs)
    
    # Extract latitude and longitude
    gdf['lat'] = centroids_target.geometry.y
    gdf['lng'] = centroids_target.geometry.x
    
    # Restore original CRS if needed
    if original_crs != target_crs:
        gdf = gdf.to_crs(original_crs)
    
    return gdf
