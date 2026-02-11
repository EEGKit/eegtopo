"""
EEG Topographic Analysis Package

A clean, pip-installable Python package for EEG topographic mapping and cluster-based
permutation testing. Designed for researchers working with channel-level EEG data.

Example
-------
>>> import pandas as pd
>>> from eegtopo import TopographicAnalysis
>>>
>>> # Your dataframe with columns: subject, channel, condition, value
>>> df = pd.read_csv('my_data.csv')
>>>
>>> # Run analysis
>>> analysis = TopographicAnalysis(df, value_col='power')
>>> results = analysis.run_cluster_test('pre', 'post', n_permutations=1024)
>>> analysis.plot_topomap(results.t_obs, title="t-statistic map")
"""

__version__ = "0.1.0"

# Coordinate transformations
from .coordinates import (
    cartesian_to_spherical,
    azimuthal_equidistant_projection,
)

# Montage handling
from .montage import (
    get_channel_positions,
    create_mne_info,
)

# Head outline
from .head import HeadOutline

# Interpolation
from .interpolation import (
    add_extrapolation_points,
    interpolate_topography,
)

# Plotting
from .plotting import plot_topomap

# Statistics
from .statistics import cluster_permutation_test

# High-level interface
from .dataframe_interface import (
    TopographicAnalysis,
    ClusterResults,
    run_cluster_analysis,
)

# Legacy imports for backward compatibility
from .montage import get_channel_positions as montage_xy
from .montage import create_mne_info as build_mne_info

__all__ = [
    # Version
    "__version__",
    # Coordinates
    "cartesian_to_spherical",
    "azimuthal_equidistant_projection",
    # Montage
    "get_channel_positions",
    "montage_xy",
    "create_mne_info",
    "build_mne_info",
    # Head
    "HeadOutline",
    # Interpolation
    "add_extrapolation_points",
    "interpolate_topography",
    # Plotting
    "plot_topomap",
    # Statistics
    "cluster_permutation_test",
    # High-level interface
    "TopographicAnalysis",
    "ClusterResults",
    "run_cluster_analysis",
]
