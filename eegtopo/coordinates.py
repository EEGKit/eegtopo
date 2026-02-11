"""
Coordinate transformation utilities for EEG topographic mapping.

This module provides functions for converting between 3D Cartesian coordinates
and 2D projected coordinates using azimuthal equidistant projection.
"""

import numpy as np


def cartesian_to_spherical(pos: np.ndarray) -> np.ndarray:
    """
    Convert Cartesian coordinates to spherical coordinates.

    Parameters
    ----------
    pos : ndarray, shape (N, 3)
        Cartesian coordinates (x, y, z)

    Returns
    -------
    sph : ndarray, shape (N, 3)
        Spherical coordinates (r, theta, phi) where:
        - r: radius
        - theta: polar angle from +z axis
        - phi: azimuthal angle in xy-plane
    """
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    rho = np.sqrt(x**2 + y**2)
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arctan2(rho, z)
    phi = np.arctan2(y, x)
    return np.column_stack([r, theta, phi])


def azimuthal_equidistant_projection(pos_3d: np.ndarray) -> np.ndarray:
    """
    Azimuthal equidistant projection of 3D Cartesian to 2D.

    This projection preserves distances from the center point, making it
    ideal for EEG topographic mapping where electrode distances should be
    preserved relative to the head center.

    Parameters
    ----------
    pos_3d : ndarray, shape (N, 3)
        3D Cartesian coordinates

    Returns
    -------
    xy : ndarray, shape (N, 2)
        2D projected coordinates
    """
    sph = cartesian_to_spherical(np.atleast_2d(pos_3d))
    theta, phi = sph[:, 1], sph[:, 2]
    return np.column_stack([theta * np.cos(phi), theta * np.sin(phi)])
