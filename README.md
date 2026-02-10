#  EV Hub Optimization for Barcelona

> ** Work in Progress**: This project is currently under active development. The final KPI dashboards and visualization layer are in progress and will be the key deliverables for stakeholder presentation.

A data-driven optimization system that identifies optimal locations for Electric Vehicle charging hubs in Barcelona using machine learning, geospatial analysis, and demand modeling.

---

##  Project Goal

Help Barcelona's city planners make **smarter infrastructure decisions** by analyzing where to place EV charging hubs to maximize coverage, minimize underserved areas, and respond to real demand patterns — not just population density.

**Key Question**: Where should the city invest in EV charging infrastructure to serve the most people with the least resources?

---

##  What This Project Does

1. **Analyzes demand** based on vehicle ownership, income levels, and existing EV adoption across 73 Barcelona neighborhoods
2. **Identifies underserved areas** by calculating unmet demand (demand minus existing supply)
3. **Optimizes hub placement** using weighted K-Means clustering to find the best locations
4. **Compares strategies** through A/B testing: Smart (demand-driven) vs. Baseline (population-weighted) placement
5. **Quantifies impact** with efficiency metrics, coverage improvements, and cost-benefit analysis

**Preliminary Results**: Smart strategy shows 15-35% improvement in demand coverage compared to baseline, depending on hub count.

---

##  Tech Stack

- **Python 3.8+**: Core language
- **Machine Learning**: scikit-learn (weighted K-Means clustering)
- **Geospatial Analysis**: GeoPandas, Shapely (CRS transformations, spatial joins)
- **Data Processing**: pandas, NumPy
- **Visualization**: Folium (interactive maps), Matplotlib
- **Data Sources**: Barcelona Open Data Service (neighborhoods, vehicles, income, charging stations)

**Development Note**: This project used **GitHub Copilot** as a productivity tool for code scaffolding and boilerplate generation. All analytical decisions, methodology design, algorithm selection, and result validation were performed independently.

---

##  Project Structure

```
WIP-EV_hub_optimization/
├── data/
│   ├── raw/                        # Source datasets (geojson, csv)
│   └── processed/                  # Output files for analysis/visualization
│
├── notebooks/                      # Analysis pipeline (5 notebooks)
│   ├── 01_setup.ipynb             # Data exploration
│   ├── 02_data_loading.ipynb      # Load & validate datasets
│   ├── 03_data_processing.ipynb   # Calculate demand scores
│   ├── 04_optimization.ipynb      # Run K-Means optimization
│   └── 05_ab_simulation.ipynb     # A/B testing & KPIs
│
├── src/                            # Reusable Python package
│   ├── data_loader.py             # Data loading utilities
│   ├── preprocessing.py           # Demand calculation & feature engineering
│   ├── optimization.py            # K-Means & simulation algorithms
│   └── visualization.py           # Mapping & plotting
│
├── requirements.txt               # Python dependencies
└── README.md
```

---

##  Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/nsanvi/WIP-EV_hub_optimization.git
cd WIP-EV_hub_optimization

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Analysis

Execute the Jupyter notebooks in order (01 → 05):

```bash
jupyter notebook notebooks/
```

**Pipeline Overview**:
1. **Setup**: Load geographic data and existing infrastructure
2. **Data Loading**: Import vehicle census, income, and charger locations
3. **Processing**: Calculate demand scores and normalize features
4. **Optimization**: Run weighted K-Means for 10, 30, and 50 hub scenarios
5. **A/B Testing**: Compare smart vs. baseline strategies (300 iterations)

### Using as a Python Package

```python
from src import load_neighborhoods, generate_smart_locations, evaluate_coverage

# Load data
gdf_barrios = load_neighborhoods()

# Find optimal locations for 25 hubs
hub_locations = generate_smart_locations(gdf_barrios, n_hubs=25)

# Evaluate performance
metrics = evaluate_coverage(hub_locations, gdf_barrios)
print(f"Coverage: {metrics['avg_coverage']:.1f}%")
```

---

##  Datasets

All data sourced from [Barcelona Open Data Service](https://opendata-ajuntament.barcelona.cat/):

| Dataset | Description | Year |
|---------|-------------|------|
| **Neighborhood Boundaries** | Polygon geometries for 73 neighborhoods | 2023 |
| **Charging Stations** | Existing EV charging point locations | 2023 Q2 |
| **Vehicle Census** | Vehicle counts by propulsion type (Electric, Hybrid, Gas, Diesel) | 2024 |
| **Household Income** | Average disposable income per capita | 2022 |

---

## 🔬 Methodology Highlights

### Demand Score Formula
Weighted composite metric:
```
Demand = (EVs × 50%) + (Income × 30%) + (Total Vehicles × 20%)
```
- **EVs**: Electric + Hybrid vehicle count (adoption readiness)
- **Income**: Purchasing power (ability to afford EVs)
- **Total Vehicles**: Vehicle density (infrastructure need)

### Unmet Demand
```
Unmet Demand = max(0, Demand - Existing Supply)
```
Focuses optimization on underserved neighborhoods.

### Optimization Algorithm
- **Weighted K-Means Clustering**: Centroids weighted by unmet demand
- **Input**: Neighborhood coordinates + demand scores
- **Output**: N optimal hub locations minimizing weighted distance to demand

### A/B Testing
- **Strategy A (Smart)**: Demand-weighted K-Means
- **Strategy B (Baseline)**: Population-weighted random placement
- **Metrics**: Coverage %, neighborhoods served, demand satisfied
- **Robustness**: 300 iterations for baseline comparison

---

##  Preliminary Results

| Hub Count | Smart Coverage | Baseline Coverage | Improvement |
|-----------|----------------|-------------------|-------------|
| 10 hubs   | ~45%          | ~30%             | +15-25%     |
| 30 hubs   | ~72%          | ~52%             | +20-30%     |
| 50 hubs   | ~88%          | ~63%             | +25-35%     |

*Note: Final KPIs and interactive dashboards pending completion.*

---

##  Next Steps

- [ ] **Complete Tableau/Power BI dashboards** with final KPIs and scenario comparisons
- [ ] Add cost-benefit analysis (infrastructure cost vs. coverage gain)
- [ ] Incorporate temporal demand patterns (peak hours, seasonality)
- [ ] Explore multi-objective optimization (coverage + equity + cost)
- [ ] Validate with real deployment data (if available)

---

##  Contributing

This is an active work-in-progress project. Suggestions and contributions are welcome! Please open an issue or submit a pull request.

---

##  License

This project uses open data from Barcelona's Open Data Service. Refer to their licensing terms for data redistribution.

---

## 👤 Author

**Nicolas San Vicente**  
📧 Contact: [Open an issue on GitHub](https://github.com/nsanvi/WIP-EV_hub_optimization/issues)  
🔗 Repository: [github.com/nsanvi/WIP-EV_hub_optimization](https://github.com/nsanvi/WIP-EV_hub_optimization)

---

##  Acknowledgments

- Barcelona City Council for open datasets
- scikit-learn, GeoPandas, and Folium communities
- GitHub Copilot for development acceleration

---

**Last Updated**: February 2026 | **Version**: 0.1.0-WIP