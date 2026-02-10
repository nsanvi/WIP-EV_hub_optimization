"""
Optimization algorithms for EV Hub Optimization project.

This module provides functions for:
- Weighted K-Means clustering for hub location optimization
- Population-weighted baseline generation
- Coverage evaluation
"""

import numpy as np
import geopandas as gpd
from sklearn.cluster import KMeans
from shapely.geometry import Point
from typing import Tuple, Dict, Optional
import random
from . import config


def weighted_kmeans_optimization(
    coordinates: np.ndarray,
    weights: np.ndarray,
    n_clusters: int,
    random_state: int = config.KMEANS_RANDOM_STATE,
    n_init: int = config.KMEANS_N_INIT
) -> np.ndarray:
    """
    Perform weighted K-Means clustering to find optimal hub locations.
    
    Args:
        coordinates: Array of shape (n_samples, 2) with [lat, lng] coordinates
        weights: Array of shape (n_samples,) with weights (e.g., unmet demand)
        n_clusters: Number of clusters (hubs) to create
        random_state: Random seed for reproducibility
        n_init: Number of initializations for K-Means
        
    Returns:
        Array of shape (n_clusters, 2) with cluster centers [lat, lng]
    """
    # Ensure we don't request more clusters than data points
    n_clusters = min(n_clusters, len(coordinates))
    
    # Handle weights: ensure non-negative and not all zero
    weights = np.array(weights).flatten()
    weights = np.maximum(weights, 0)  # Ensure non-negative
    
    if weights.sum() == 0:
        weights = np.ones_like(weights)  # Fall back to uniform weights
    
    # Initialize and fit K-Means with sample weights
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=n_init
    )
    kmeans.fit(coordinates, sample_weight=weights)
    
    return kmeans.cluster_centers_


def generate_smart_locations(
    gdf: gpd.GeoDataFrame,
    n_hubs: int,
    weight_column: str = config.COL_UNMET_DEMAND,
    lat_column: str = 'lat',
    lng_column: str = 'lng'
) -> np.ndarray:
    """
    Generate smart hub locations based on unmet demand.
    
    Args:
        gdf: GeoDataFrame with neighborhood data
        n_hubs: Number of hubs to place
        weight_column: Column to use as weights (default: unmet demand)
        lat_column: Column with latitude coordinates
        lng_column: Column with longitude coordinates
        
    Returns:
        Array of shape (n_hubs, 2) with hub locations [lat, lng]
    """
    # Extract coordinates
    coordinates = gdf[[lat_column, lng_column]].values
    
    # Extract weights
    weights = gdf[weight_column].fillna(0).values
    
    # Run weighted K-Means
    centers = weighted_kmeans_optimization(
        coordinates=coordinates,
        weights=weights,
        n_clusters=n_hubs
    )
    
    return centers


def random_point_in_polygon(polygon, rng=None, py_rng=None) -> Tuple[float, float]:
    """
    Generate a random point inside a polygon.
    
    Uses rejection sampling: generate random points in bounding box
    until one falls inside the polygon.
    
    Args:
        polygon: Shapely polygon geometry
        rng: NumPy random generator (optional)
        py_rng: Python random.Random instance (optional)
        
    Returns:
        Tuple of (latitude, longitude)
    """
    if rng is None:
        rng = np.random.default_rng()
    if py_rng is None:
        py_rng = random.Random()
    
    minx, miny, maxx, maxy = polygon.bounds
    
    # Try up to 1000 times to find a point inside the polygon
    for _ in range(1000):
        # Generate random point in bounding box
        x = py_rng.uniform(minx, maxx)
        y = py_rng.uniform(miny, maxy)
        point = Point(x, y)
        
        if polygon.contains(point):
            return (y, x)  # Return as (lat, lng)
    
    # Fallback to centroid if no point found
    centroid = polygon.centroid
    return (centroid.y, centroid.x)


def generate_population_weighted_locations(
    gdf: gpd.GeoDataFrame,
    n_hubs: int,
    weight_column: str = config.COL_TOTAL_VEHICLES,
    seed: int = config.BASELINE_SEED
) -> np.ndarray:
    """
    Generate hub locations weighted by population/vehicle density (baseline).
    
    This is the "naive" approach that doesn't consider unmet demand,
    used as a baseline for comparison.
    
    Args:
        gdf: GeoDataFrame with neighborhood data
        n_hubs: Number of hubs to place
        weight_column: Column to use as weights (default: total vehicles)
        seed: Random seed for reproducibility
        
    Returns:
        Array of shape (n_hubs, 2) with hub locations [lat, lng]
    """
    # Set up random generators
    rng = np.random.default_rng(seed)
    py_rng = random.Random(seed)
    
    # Extract weights
    weights = gdf[weight_column].fillna(0).values
    
    # Normalize weights to probabilities
    weights = weights / weights.sum()
    
    # Sample neighborhoods according to weights
    sampled_indices = rng.choice(
        gdf.index.to_numpy(),
        size=n_hubs,
        replace=True,
        p=weights
    )
    
    # Generate random points within sampled neighborhoods
    locations = []
    for idx in sampled_indices:
        polygon = gdf.loc[idx, config.COL_GEOMETRY]
        point = random_point_in_polygon(polygon, rng=rng, py_rng=py_rng)
        locations.append(point)
    
    return np.array(locations)


def evaluate_coverage(
    hub_locations: np.ndarray,
    gdf_barrios: gpd.GeoDataFrame,
    radius_m: float = config.COVERAGE_RADIUS_M,
    buffer_crs: str = config.BUFFER_CRS
) -> Dict[str, float]:
    """
    Evaluate coverage metrics for hub locations.
    
    Args:
        hub_locations: Array of shape (n_hubs, 2) with [lat, lng] coordinates
        gdf_barrios: GeoDataFrame with neighborhood data
        radius_m: Coverage radius in meters
        buffer_crs: CRS for metric calculations (default: EPSG:3857)
        
    Returns:
        Dictionary with coverage metrics:
        - 'covered_neighborhoods': Number of neighborhoods with >50% coverage
        - 'avg_coverage': Average coverage percentage across all neighborhoods
        - 'demand_covered': Percentage of total demand covered
        - 'population_covered': Percentage of total population covered
    """
    # Ensure gdf_barrios has CRS
    if gdf_barrios.crs is None:
        gdf_barrios = gdf_barrios.set_crs(config.TARGET_CRS)
    
    # Convert to metric CRS for accurate distance calculations
    barrios_m = gdf_barrios.to_crs(buffer_crs)
    
    # Calculate neighborhood areas
    barrio_areas = barrios_m.geometry.area
    
    # Create GeoDataFrame for hub locations
    hub_points = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(hub_locations[:, 1], hub_locations[:, 0]),
        crs=config.TARGET_CRS
    )
    hub_points_m = hub_points.to_crs(buffer_crs)
    
    # Create buffers around hubs
    buffers = hub_points_m.geometry.buffer(radius_m)
    
    # Calculate coverage for each neighborhood
    max_coverage = np.zeros(len(barrios_m))
    
    for buffer_geom in buffers:
        # Calculate intersection area with each neighborhood
        intersection_areas = barrios_m.geometry.intersection(buffer_geom).area
        
        # Calculate coverage percentage
        coverage_pct = (intersection_areas / barrio_areas).fillna(0).clip(0, 1)
        
        # Track maximum coverage from any hub
        max_coverage = np.maximum(max_coverage, coverage_pct.values)
    
    # Calculate metrics
    covered_neighborhoods = np.sum(max_coverage > 0.5)
    avg_coverage = np.mean(max_coverage) * 100
    
    # Calculate demand coverage (if available)
    if config.COL_DEMAND_SCORE in gdf_barrios.columns:
        total_demand = gdf_barrios[config.COL_DEMAND_SCORE].sum()
        covered_demand = (gdf_barrios[config.COL_DEMAND_SCORE] * max_coverage).sum()
        demand_coverage_pct = (covered_demand / total_demand * 100) if total_demand > 0 else 0
    else:
        demand_coverage_pct = 0
    
    # Calculate population coverage (if available)
    if config.COL_TOTAL_VEHICLES in gdf_barrios.columns:
        total_population = gdf_barrios[config.COL_TOTAL_VEHICLES].sum()
        covered_population = (gdf_barrios[config.COL_TOTAL_VEHICLES] * max_coverage).sum()
        population_coverage_pct = (covered_population / total_population * 100) if total_population > 0 else 0
    else:
        population_coverage_pct = 0
    
    return {
        'covered_neighborhoods': int(covered_neighborhoods),
        'avg_coverage': float(avg_coverage),
        'demand_covered': float(demand_coverage_pct),
        'population_covered': float(population_coverage_pct)
    }


def run_ab_simulation(
    gdf: gpd.GeoDataFrame,
    n_hubs_list: list = None,
    n_iterations: int = config.BASELINE_ITERATIONS,
    seed: int = config.BASELINE_SEED
) -> Dict[int, Dict[str, float]]:
    """
    Run A/B simulation comparing smart vs. baseline placement strategies.
    
    Args:
        gdf: GeoDataFrame with neighborhood data including demand scores
        n_hubs_list: List of hub counts to simulate (default from config)
        n_iterations: Number of iterations for baseline averaging
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary mapping n_hubs to comparison metrics
    """
    if n_hubs_list is None:
        n_hubs_list = config.SCENARIOS
    
    results = {}
    
    for n_hubs in n_hubs_list:
        # Generate smart locations
        smart_locs = generate_smart_locations(gdf, n_hubs)
        smart_metrics = evaluate_coverage(smart_locs, gdf)
        
        # Generate baseline locations (average over multiple iterations)
        baseline_metrics_list = []
        for i in range(n_iterations):
            baseline_locs = generate_population_weighted_locations(
                gdf,
                n_hubs,
                seed=seed + i
            )
            baseline_metrics = evaluate_coverage(baseline_locs, gdf)
            baseline_metrics_list.append(baseline_metrics)
        
        # Average baseline metrics
        avg_baseline = {
            key: np.mean([m[key] for m in baseline_metrics_list])
            for key in baseline_metrics_list[0].keys()
        }
        
        # Calculate improvements
        results[n_hubs] = {
            'smart': smart_metrics,
            'baseline': avg_baseline,
            'improvement_pct': {
                key: ((smart_metrics[key] - avg_baseline[key]) / avg_baseline[key] * 100)
                if avg_baseline[key] > 0 else 0
                for key in smart_metrics.keys()
            }
        }
    
    return results
