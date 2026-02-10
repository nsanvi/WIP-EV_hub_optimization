# EV Hub Optimization for Barcelona

A Python-based optimization system for identifying optimal locations for Electric Vehicle (EV) charging hubs in Barcelona using weighted K-Means clustering and demand analysis.

## 📋 Project Overview

This project analyzes Barcelona's EV charging infrastructure needs by:
- Calculating demand scores based on vehicle ownership, income levels, and existing EV adoption
- Identifying underserved neighborhoods using unmet demand analysis
- Using weighted K-Means clustering to find optimal hub locations
- Comparing smart (demand-driven) vs. baseline (population-weighted) placement strategies through A/B testing

## 🏗️ Project Structure

```
WIP-EV_hub_optimization/
├── data/
│   ├── raw/                                    # Raw input data
│   │   ├── 0301100100_UNITATS_ADM_POLIGONS.json  # Neighborhood boundaries
│   │   ├── neighbourhoods.geojson              # Simplified neighborhood geometries
│   │   ├── 2023_2T_Punts_Recarrega_Vehicle_Electric.json  # Charging stations
│   │   ├── puntos_recarga_barcelona.csv        # Charging stations (CSV)
│   │   ├── 2024_parc_vehicles_tipus_propulsio.csv  # Vehicle census by type
│   │   ├── 2024_parc_vehicles_index_motoritzacio.csv  # Vehicle motorization index
│   │   ├── 2022_renda_disponible_llars_per_persona.csv  # Household income
│   │   └── converter.py                        # JSON to CSV converter utility
│   └── processed/                              # Generated output data
│       ├── barrios_with_demand.geojson         # Neighborhoods with demand metrics
│       ├── tableau_barrios_master.csv          # Master data for visualization
│       ├── tableau_kpis.csv                    # Key performance indicators
│       └── tableau_scenarios.csv               # Scenario comparisons
│
├── notebooks/                                  # Jupyter notebooks (analysis pipeline)
│   ├── 01_setup.ipynb                         # Initial data exploration
│   ├── 02_data_loading.ipynb                  # Load and inspect datasets
│   ├── 03_data_processing.ipynb               # Calculate demand metrics
│   ├── 04_optimization.ipynb                  # Run K-Means optimization
│   └── 05_ab_simulation.ipynb                 # A/B testing simulation
│
├── src/                                        # Reusable Python package
│   ├── __init__.py                            # Package initialization
│   ├── config.py                              # Configuration parameters
│   ├── data_loader.py                         # Data loading utilities
│   ├── preprocessing.py                       # Data processing functions
│   ├── optimization.py                        # K-Means and simulation algorithms
│   └── visualization.py                       # Mapping and plotting functions
│
├── debug_chargers.py                          # Utility script for testing charger data
├── requirements.txt                           # Python dependencies
├── .gitignore                                 # Git ignore rules
└── README.md                                  # This file
```

## 📊 Datasets Used

### Geographic Data
- **Neighborhood Boundaries** (`0301100100_UNITATS_ADM_POLIGONS.json`): Polygon geometries for Barcelona's 73 neighborhoods
- **Simplified Neighborhoods** (`neighbourhoods.geojson`): Lightweight version for visualization

### Infrastructure Data
- **Charging Stations** (`2023_2T_Punts_Recarrega_Vehicle_Electric.json`): Existing EV charging point locations (Q2 2023)

### Demographic Data
- **Vehicle Census** (`2024_parc_vehicles_tipus_propulsio.csv`): Vehicle counts by neighborhood and propulsion type (2024)
  - Electric, Hybrid, Gasoline, Diesel classifications
- **Household Income** (`2022_renda_disponible_llars_per_persona.csv`): Average disposable income per capita by neighborhood (2022)

### Data Sources
All datasets are sourced from Barcelona's Open Data Service (https://opendata-ajuntament.barcelona.cat/).

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/nsanvi/WIP-EV_hub_optimization.git
   cd WIP-EV_hub_optimization
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import geopandas; import sklearn; print('✓ All packages installed successfully')"
   ```

## 📖 Usage Guide

### Running the Analysis Pipeline

The analysis is organized into 5 sequential Jupyter notebooks:

1. **Setup and Exploration** (`01_setup.ipynb`)
   ```bash
   jupyter notebook notebooks/01_setup.ipynb
   ```
   - Load neighborhood geometries and existing charging stations
   - Visualize current infrastructure distribution
   - Explore geographic data structure

2. **Data Loading** (`02_data_loading.ipynb`)
   ```bash
   jupyter notebook notebooks/02_data_loading.ipynb
   ```
   - Load all raw datasets (vehicles, income, chargers)
   - Validate data formats and CRS compatibility
   - Perform initial data quality checks

3. **Data Processing** (`03_data_processing.ipynb`)
   ```bash
   jupyter notebook notebooks/03_data_processing.ipynb
   ```
   - Calculate EV counts per neighborhood
   - Aggregate income and vehicle statistics
   - Compute normalized demand scores
   - Export processed data to `barrios_with_demand.geojson`

4. **Optimization** (`04_optimization.ipynb`)
   ```bash
   jupyter notebook notebooks/04_optimization.ipynb
   ```
   - Calculate unmet demand (demand - supply)
   - Run weighted K-Means clustering for optimal hub placement
   - Generate scenarios: 10, 30, and 50 hubs
   - Visualize results on interactive maps

5. **A/B Simulation** (`05_ab_simulation.ipynb`)
   ```bash
   jupyter notebook notebooks/05_ab_simulation.ipynb
   ```
   - Compare smart (demand-driven) vs. baseline (population-weighted) strategies
   - Run 300 iterations for robust baseline comparison
   - Calculate efficiency gains and coverage improvements
   - Export KPIs for Tableau visualization

### Using the Python Package

The `src/` package provides reusable functions for custom analyses:

```python
from src import (
    load_neighborhoods,
    load_chargers,
    calculate_demand_score,
    generate_smart_locations,
    evaluate_coverage,
    visualize_hub_locations
)

# Load data
gdf_barrios = load_neighborhoods()
gdf_chargers = load_chargers()

# Calculate demand
gdf_with_demand = calculate_demand_score(gdf_barrios)

# Find optimal locations for 25 hubs
hub_locations = generate_smart_locations(gdf_with_demand, n_hubs=25)

# Evaluate coverage
metrics = evaluate_coverage(hub_locations, gdf_with_demand)
print(f"Coverage: {metrics['avg_coverage']:.1f}%")

# Visualize on map
m = visualize_hub_locations(gdf_with_demand, hub_locations)
m.save('hub_map.html')
```

### Key Functions

**Data Loading** (`data_loader.py`):
- `load_neighborhoods()`: Load Barcelona neighborhood geometries
- `load_chargers()`: Load existing charging station locations
- `load_vehicles()`: Load vehicle census data
- `load_income()`: Load household income data

**Preprocessing** (`preprocessing.py`):
- `calculate_demand_score()`: Compute weighted demand scores
- `calculate_unmet_demand()`: Calculate demand minus supply
- `calculate_centroids_with_crs_transform()`: CRS-aware centroid calculation

**Optimization** (`optimization.py`):
- `generate_smart_locations()`: Weighted K-Means for hub placement
- `generate_population_weighted_locations()`: Baseline strategy
- `evaluate_coverage()`: Calculate coverage metrics
- `run_ab_simulation()`: Full A/B comparison

**Visualization** (`visualization.py`):
- `create_folium_map()`: Create interactive web maps
- `visualize_hub_locations()`: Plot hubs on demand heatmap
- `plot_comparison_metrics()`: Compare strategies with matplotlib

## 🛠️ Technologies

### Core Libraries
- **pandas** (>=2.0.0): Data manipulation and analysis
- **numpy** (>=1.24.0): Numerical computing
- **geopandas** (>=0.14.0): Geospatial data handling
- **shapely** (>=2.0.0): Geometric operations

### Machine Learning
- **scikit-learn** (>=1.3.0): K-Means clustering and preprocessing
  - `KMeans`: Weighted clustering algorithm
  - `MinMaxScaler`: Feature normalization

### Visualization
- **matplotlib** (>=3.7.0): Static plotting
- **folium** (>=0.15.0): Interactive web maps
- **Jupyter** (>=1.0.0): Notebook environment

### Geospatial
- **pyproj** (>=3.6.0): Coordinate reference system transformations
- CRS used:
  - **EPSG:4326**: Geographic coordinates (WGS84, latitude/longitude)
  - **EPSG:25831**: Projected coordinates (ETRS89/UTM Zone 31N, meters) - used for accurate distance/area calculations in Barcelona
  - **EPSG:3857**: Web Mercator (alternative for web mapping)

## 🔬 Methodology

### Demand Score Calculation
Weighted composite score based on:
- **EV Count** (50%): Number of electric and hybrid vehicles
- **Income** (30%): Household disposable income (purchasing power)
- **Total Vehicles** (20%): Overall vehicle density

Formula:
```
Demand_Score = (Norm_EVs × 0.5 + Norm_Income × 0.3 + Norm_Vehicles × 0.2) × 100
```

### Unmet Demand
Accounts for existing charging infrastructure:
```
Unmet_Demand = max(0, Demand_Score - Norm_Supply × 80)
```
Where `Norm_Supply` is the normalized count of existing chargers.

### Optimization Algorithm
**Weighted K-Means Clustering:**
- Input: Neighborhood centroids (lat/lng)
- Weights: Unmet demand scores
- Output: N cluster centers representing optimal hub locations
- Parameters: `n_init=10`, `random_state=42`

### A/B Testing
- **Strategy A (Smart)**: Weighted K-Means with unmet demand
- **Strategy B (Baseline)**: Population-weighted random sampling
- **Metrics**: Coverage %, neighborhoods served, demand satisfied
- **Iterations**: 300 runs for baseline to ensure robust comparison

## 📈 Key Results

Typical improvements of smart strategy over baseline:
- **10 hubs**: +15-25% demand coverage
- **25 hubs**: +20-30% efficiency gain
- **50 hubs**: +25-35% neighborhood coverage

## 🤝 Contributing

This is a work-in-progress project. Contributions are welcome!

### Development Setup
```bash
# Install dev dependencies
pip install -e .

# Run tests (if available)
pytest tests/

# Format code
black src/ notebooks/
```

## 📝 License

This project uses open data from Barcelona's Open Data Service. Please refer to their licensing terms when using or redistributing the datasets.

## 👥 Authors

**EV Hub Optimization Team**
- Repository: https://github.com/nsanvi/WIP-EV_hub_optimization

## 🙏 Acknowledgments

- Barcelona City Council for providing open data
- scikit-learn community for excellent ML tools
- GeoPandas and Shapely teams for geospatial libraries

## 📧 Contact

For questions or collaboration opportunities, please open an issue on GitHub.

---

**Last Updated**: February 2026
**Version**: 0.1.0
