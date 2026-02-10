"""
Configuration settings for EV Hub Optimization project.

This module contains all configuration parameters including:
- Data file paths
- Model parameters
- Visualization settings
- CRS (Coordinate Reference System) settings
"""

import os

# ==============================================================================
# DATA PATHS
# ==============================================================================

# Base directories
RAW_DATA_DIR = os.path.join('data', 'raw')
PROCESSED_DATA_DIR = os.path.join('data', 'processed')

# Raw data files
FILE_GEOMETRY = '0301100100_UNITATS_ADM_POLIGONS.json'
FILE_NEIGHBORHOODS = 'neighbourhoods.geojson'
FILE_CHARGERS_JSON = '2023_2T_Punts_Recarrega_Vehicle_Electric.json'
FILE_CHARGERS_CSV = 'puntos_recarga_barcelona.csv'
FILE_VEHICLES_PROPULSION = '2024_parc_vehicles_tipus_propulsio.csv'
FILE_VEHICLES_INDEX = '2024_parc_vehicles_index_motoritzacio.csv'
FILE_INCOME = '2022_renda_disponible_llars_per_persona.csv'

# Processed data files
FILE_BARRIOS_WITH_DEMAND = 'barrios_with_demand.geojson'
FILE_TABLEAU_MASTER = 'tableau_barrios_master.csv'
FILE_TABLEAU_KPIS = 'tableau_kpis.csv'
FILE_TABLEAU_SCENARIOS = 'tableau_scenarios.csv'

# ==============================================================================
# DEMAND SCORE PARAMETERS
# ==============================================================================

# Weights for demand score calculation (must sum to 1.0)
WEIGHT_EV_COUNT = 0.5  # 50% - Primary driver
WEIGHT_INCOME = 0.3  # 30% - Purchasing power indicator
WEIGHT_TOTAL_VEHICLES = 0.2  # 20% - Vehicle density

# Demand score scaling
DEMAND_SCORE_BASE = 100  # Base scaling factor
SUPPLY_IMPACT = 80  # Impact of existing chargers on unmet demand

# ==============================================================================
# K-MEANS OPTIMIZATION PARAMETERS
# ==============================================================================

# K-Means algorithm settings
KMEANS_N_INIT = 10  # Number of initializations
KMEANS_RANDOM_STATE = 42  # For reproducibility

# Scenario hub counts
SCENARIOS = [10, 25, 50]  # Number of hubs to simulate

# ==============================================================================
# COVERAGE EVALUATION PARAMETERS
# ==============================================================================

# Coverage radius in meters
COVERAGE_RADIUS_M = 500  # Walking distance threshold

# Baseline comparison settings
BASELINE_ITERATIONS = 300  # Number of iterations for robust baseline
BASELINE_SEED = 42  # Random seed for baseline generation

# ==============================================================================
# COORDINATE REFERENCE SYSTEMS
# ==============================================================================

# Standard CRS for geographic data (latitude/longitude)
TARGET_CRS = 'EPSG:4326'

# Projected CRS for metric calculations (meters)
# EPSG:25831 - ETRS89 / UTM zone 31N (Barcelona, Spain)
PROJECTED_CRS = 'EPSG:25831'

# Alternative projected CRS for web mapping
BUFFER_CRS = 'EPSG:3857'  # Web Mercator

# ==============================================================================
# DATA FILTERING PARAMETERS
# ==============================================================================

# Geometry filtering
BARRI_TYPE = 'BARRI'  # Neighborhood type identifier

# Vehicle type classification
EV_PROPULSION_TYPES = ['Elèctrica', 'Híbrid']  # Electric vehicle types

# Missing data handling
FILL_STRATEGY = 'median'  # Strategy for filling missing values

# ==============================================================================
# VISUALIZATION PARAMETERS
# ==============================================================================

# Map center (Barcelona coordinates)
MAP_CENTER = [41.3851, 2.1734]  # [latitude, longitude]
MAP_ZOOM = 12  # Default zoom level

# Color schemes
COLOR_DEMAND = 'YlOrRd'  # Yellow-Orange-Red for demand heatmaps
COLOR_UNMET = 'RdYlGn_r'  # Red-Yellow-Green reversed for unmet demand

# ==============================================================================
# COLUMN NAMES
# ==============================================================================

# Standard column names used across the project
COL_BARRI_ID = 'Barri_ID'
COL_BARRI_NAME = 'NOM'
COL_GEOMETRY = 'geometry'
COL_AVG_INCOME = 'Avg_Income'
COL_TOTAL_VEHICLES = 'Total_Vehicles'
COL_EV_COUNT = 'EV_Count'
COL_CHARGER_COUNT = 'Charger_Count'
COL_DEMAND_SCORE = 'Demand_Score'
COL_UNMET_DEMAND = 'Unmet_Demand'
