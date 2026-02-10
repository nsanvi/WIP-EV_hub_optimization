"""
Visualization utilities for EV Hub Optimization project.

This module provides functions for:
- Creating interactive Folium maps
- Plotting with matplotlib
- Styling map layers
"""

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, List, Tuple
from . import config


def create_folium_map(
    center: Optional[List[float]] = None,
    zoom_start: int = config.MAP_ZOOM,
    tiles: str = 'OpenStreetMap'
) -> folium.Map:
    """
    Create a base Folium map centered on Barcelona.
    
    Args:
        center: [latitude, longitude] for map center. If None, uses config default.
        zoom_start: Initial zoom level
        tiles: Tile layer to use
        
    Returns:
        Folium Map object
    """
    if center is None:
        center = config.MAP_CENTER
    
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles=tiles
    )
    
    return m


def add_choropleth_layer(
    m: folium.Map,
    gdf: gpd.GeoDataFrame,
    column: str,
    legend_name: str,
    colormap: str = 'YlOrRd',
    fill_opacity: float = 0.7,
    line_opacity: float = 0.2
) -> folium.Map:
    """
    Add a choropleth layer to a Folium map.
    
    Args:
        m: Folium Map object
        gdf: GeoDataFrame with data to visualize
        column: Column name to use for coloring
        legend_name: Name to display in the legend
        colormap: Color scheme to use
        fill_opacity: Opacity of filled areas
        line_opacity: Opacity of boundary lines
        
    Returns:
        Updated Folium Map object
    """
    # Ensure CRS is EPSG:4326 for Folium
    if gdf.crs is not None and gdf.crs != config.TARGET_CRS:
        gdf = gdf.to_crs(config.TARGET_CRS)
    
    # Create choropleth layer
    folium.Choropleth(
        geo_data=gdf,
        data=gdf,
        columns=[config.COL_BARRI_ID, column],
        key_on=f'feature.properties.{config.COL_BARRI_ID}',
        fill_color=colormap,
        fill_opacity=fill_opacity,
        line_opacity=line_opacity,
        legend_name=legend_name,
        nan_fill_color='lightgray'
    ).add_to(m)
    
    return m


def add_points_layer(
    m: folium.Map,
    locations: np.ndarray,
    color: str = 'red',
    radius: int = 5,
    fill: bool = True,
    popup_text: Optional[List[str]] = None,
    tooltip_text: Optional[List[str]] = None
) -> folium.Map:
    """
    Add point markers to a Folium map.
    
    Args:
        m: Folium Map object
        locations: Array of shape (n, 2) with [lat, lng] coordinates
        color: Color for markers
        radius: Radius of circular markers
        fill: Whether to fill the circles
        popup_text: List of popup texts for each point (optional)
        tooltip_text: List of tooltip texts for each point (optional)
        
    Returns:
        Updated Folium Map object
    """
    for i, (lat, lng) in enumerate(locations):
        popup = popup_text[i] if popup_text and i < len(popup_text) else None
        tooltip = tooltip_text[i] if tooltip_text and i < len(tooltip_text) else None
        
        folium.CircleMarker(
            location=[lat, lng],
            radius=radius,
            color=color,
            fill=fill,
            fillColor=color,
            fillOpacity=0.6,
            popup=popup,
            tooltip=tooltip
        ).add_to(m)
    
    return m


def add_geojson_layer(
    m: folium.Map,
    gdf: gpd.GeoDataFrame,
    style_function=None,
    highlight_function=None,
    tooltip_fields: Optional[List[str]] = None,
    tooltip_aliases: Optional[List[str]] = None
) -> folium.Map:
    """
    Add a GeoJSON layer to a Folium map with tooltips.
    
    Args:
        m: Folium Map object
        gdf: GeoDataFrame to add
        style_function: Function to style features
        highlight_function: Function to style highlighted features
        tooltip_fields: List of field names to show in tooltip
        tooltip_aliases: List of display names for tooltip fields
        
    Returns:
        Updated Folium Map object
    """
    # Ensure CRS is EPSG:4326 for Folium
    if gdf.crs is not None and gdf.crs != config.TARGET_CRS:
        gdf = gdf.to_crs(config.TARGET_CRS)
    
    # Create tooltip if fields are specified
    if tooltip_fields:
        tooltip = folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases if tooltip_aliases else tooltip_fields,
            localize=True
        )
    else:
        tooltip = None
    
    # Add GeoJSON layer
    folium.GeoJson(
        gdf,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip
    ).add_to(m)
    
    return m


def visualize_hub_locations(
    gdf_barrios: gpd.GeoDataFrame,
    smart_hubs: np.ndarray,
    baseline_hubs: Optional[np.ndarray] = None,
    demand_column: str = config.COL_UNMET_DEMAND,
    save_path: Optional[str] = None
) -> folium.Map:
    """
    Create a map visualizing hub locations and demand.
    
    Args:
        gdf_barrios: GeoDataFrame with neighborhood data
        smart_hubs: Array of smart hub locations [lat, lng]
        baseline_hubs: Array of baseline hub locations [lat, lng] (optional)
        demand_column: Column to use for choropleth
        save_path: Path to save the map HTML (optional)
        
    Returns:
        Folium Map object
    """
    # Create base map
    m = create_folium_map()
    
    # Add demand choropleth
    m = add_choropleth_layer(
        m,
        gdf_barrios,
        column=demand_column,
        legend_name='Unmet Demand Score',
        colormap=config.COLOR_UNMET
    )
    
    # Add smart hub locations
    m = add_points_layer(
        m,
        smart_hubs,
        color='blue',
        radius=8,
        tooltip_text=[f'Smart Hub {i+1}' for i in range(len(smart_hubs))]
    )
    
    # Add baseline hub locations if provided
    if baseline_hubs is not None:
        m = add_points_layer(
            m,
            baseline_hubs,
            color='orange',
            radius=6,
            tooltip_text=[f'Baseline Hub {i+1}' for i in range(len(baseline_hubs))]
        )
    
    # Save if path provided
    if save_path:
        m.save(save_path)
    
    return m


def plot_comparison_metrics(
    results: dict,
    metric_keys: List[str] = None,
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot comparison metrics between smart and baseline strategies.
    
    Args:
        results: Results dictionary from run_ab_simulation
        metric_keys: List of metric keys to plot (default: all available)
        figsize: Figure size (width, height)
        save_path: Path to save the figure (optional)
        
    Returns:
        Matplotlib Figure object
    """
    if metric_keys is None:
        # Use first scenario to get available metrics
        first_scenario = list(results.keys())[0]
        metric_keys = list(results[first_scenario]['smart'].keys())
    
    # Prepare data
    n_hubs_list = sorted(results.keys())
    
    # Create subplots
    n_metrics = len(metric_keys)
    fig, axes = plt.subplots(1, n_metrics, figsize=figsize)
    
    if n_metrics == 1:
        axes = [axes]
    
    for idx, metric in enumerate(metric_keys):
        ax = axes[idx]
        
        # Extract values
        smart_values = [results[n]['smart'][metric] for n in n_hubs_list]
        baseline_values = [results[n]['baseline'][metric] for n in n_hubs_list]
        
        # Plot
        ax.plot(n_hubs_list, smart_values, 'o-', label='Smart', linewidth=2, markersize=8)
        ax.plot(n_hubs_list, baseline_values, 's--', label='Baseline', linewidth=2, markersize=8)
        
        ax.set_xlabel('Number of Hubs')
        ax.set_ylabel(metric.replace('_', ' ').title())
        ax.set_title(metric.replace('_', ' ').title())
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_improvement_percentage(
    results: dict,
    metric_keys: List[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot percentage improvement of smart strategy over baseline.
    
    Args:
        results: Results dictionary from run_ab_simulation
        metric_keys: List of metric keys to plot (default: all available)
        figsize: Figure size (width, height)
        save_path: Path to save the figure (optional)
        
    Returns:
        Matplotlib Figure object
    """
    if metric_keys is None:
        # Use first scenario to get available metrics
        first_scenario = list(results.keys())[0]
        metric_keys = list(results[first_scenario]['improvement_pct'].keys())
    
    # Prepare data
    n_hubs_list = sorted(results.keys())
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot bars for each metric
    x = np.arange(len(n_hubs_list))
    width = 0.8 / len(metric_keys)
    
    for idx, metric in enumerate(metric_keys):
        values = [results[n]['improvement_pct'][metric] for n in n_hubs_list]
        offset = (idx - len(metric_keys) / 2) * width + width / 2
        ax.bar(x + offset, values, width, label=metric.replace('_', ' ').title())
    
    ax.set_xlabel('Number of Hubs')
    ax.set_ylabel('Improvement (%)')
    ax.set_title('Smart Strategy Improvement Over Baseline')
    ax.set_xticks(x)
    ax.set_xticklabels(n_hubs_list)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig
