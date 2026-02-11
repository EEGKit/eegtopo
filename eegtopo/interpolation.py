"""
Interpolation utilities for EEG topographic mapping.

This module provides functions for smooth interpolation of EEG data
across the scalp surface.
"""

import numpy as np
from scipy.interpolate import CloughTocher2DInterpolator


def add_extrapolation_points(xy: np.ndarray, n_points: int = 16) -> np.ndarray:
    """
    Add extrapolation points around the periphery for better interpolation.

    This follows MNE's approach of adding points outside the electrode array
    to ensure smooth interpolation at the edges.

    Parameters
    ----------
    xy : ndarray, shape (n, 2)
        Electrode positions
    n_points : int
        Number of extrapolation points to add

    Returns
    -------
    xy_extended : ndarray
        Original positions plus extrapolation points
    """
    # Calculate center and max radius
    center = np.mean(xy, axis=0)
    dists = np.sqrt(np.sum((xy - center) ** 2, axis=1))
    max_dist = np.max(dists)

    # Add points in a circle beyond the electrodes
    angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    extra_radius = max_dist * 1.15  # 15% beyond furthest electrode

    extra_x = center[0] + extra_radius * np.cos(angles)
    extra_y = center[1] + extra_radius * np.sin(angles)
    extra_points = np.column_stack([extra_x, extra_y])

    return np.vstack([xy, extra_points])


def interpolate_topography(
    xy: np.ndarray,
    values: np.ndarray,
    Xi: np.ndarray,
    Yi: np.ndarray,
    extrapolate: bool = True,
) -> np.ndarray:
    """
    Interpolate values across a 2D grid using Clough-Tocher interpolation.

    Parameters
    ----------
    xy : ndarray, shape (n, 2)
        Electrode positions
    values : ndarray, shape (n,)
        Values at each electrode
    Xi, Yi : ndarray
        Grid coordinates for interpolation
    extrapolate : bool
        Whether to add extrapolation points for smoother edges

    Returns
    -------
    Zi : ndarray
        Interpolated values on the grid
    """
    if extrapolate:
        # Add extrapolation points for smoother edges
        xy_extended = add_extrapolation_points(xy)
        values_extended = np.concatenate([values, np.full(16, np.mean(values))])
    else:
        xy_extended = xy
        values_extended = values

    # Use Clough-Tocher 2D interpolator for smooth surface
    interp = CloughTocher2DInterpolator(xy_extended, values_extended)
    Zi = interp(Xi, Yi)

    return Zi
