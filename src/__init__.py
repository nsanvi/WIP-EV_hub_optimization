"""
EV Hub Optimization Package

A Python package for optimizing electric vehicle charging hub locations
in Barcelona using weighted K-Means clustering and demand analysis.

Modules:
    config: Configuration parameters and settings
    data_loader: Data loading and export utilities
    preprocessing: Data preprocessing and demand calculation
    optimization: K-Means optimization and A/B simulation
    visualization: Mapping and plotting utilities
"""

__version__ = '0.1.0'
__author__ = 'EV Hub Optimization Team'

# Import key functions for easy access
from . import config
from .data_loader import (
    load_neighborhoods,
    load_chargers,
    load_vehicles,
    load_income,
    load_processed_barrios,
    export_geojson,
    export_csv
)
from .preprocessing import (
    standardize_barri_id,
    aggregate_income_by_barrio,
    aggregate_vehicles_by_barrio,
    calculate_ev_counts,
    spatial_join_chargers,
    create_master_dataframe,
    calculate_demand_score,
    calculate_unmet_demand,
    calculate_centroids_with_crs_transform
)
from .optimization import (
    weighted_kmeans_optimization,
    generate_smart_locations,
    generate_population_weighted_locations,
    evaluate_coverage,
    run_ab_simulation
)
from .visualization import (
    create_folium_map,
    add_choropleth_layer,
    add_points_layer,
    add_geojson_layer,
    visualize_hub_locations,
    plot_comparison_metrics,
    plot_improvement_percentage
)

__all__ = [
    # Config
    'config',
    # Data Loading
    'load_neighborhoods',
    'load_chargers',
    'load_vehicles',
    'load_income',
    'load_processed_barrios',
    'export_geojson',
    'export_csv',
    # Preprocessing
    'standardize_barri_id',
    'aggregate_income_by_barrio',
    'aggregate_vehicles_by_barrio',
    'calculate_ev_counts',
    'spatial_join_chargers',
    'create_master_dataframe',
    'calculate_demand_score',
    'calculate_unmet_demand',
    'calculate_centroids_with_crs_transform',
    # Optimization
    'weighted_kmeans_optimization',
    'generate_smart_locations',
    'generate_population_weighted_locations',
    'evaluate_coverage',
    'run_ab_simulation',
    # Visualization
    'create_folium_map',
    'add_choropleth_layer',
    'add_points_layer',
    'add_geojson_layer',
    'visualize_hub_locations',
    'plot_comparison_metrics',
    'plot_improvement_percentage'
]
