"""
Montage handling utilities for EEG topographic mapping.

This module provides functions for working with EEG montages, including
loading standard montages from MNE-Python and extracting 2D positions.
"""

from typing import List, Optional, Tuple, Any
import numpy as np


def get_channel_positions(
    ch_names: List[str],
    montage_name: str = "GSN-HydroCel-256",
    exclude: Optional[List[str]] = None,
) -> Tuple[List[str], np.ndarray]:
    """
    Return 2-D projected positions for channels from a standard MNE montage.

    Parameters
    ----------
    ch_names : list[str]
        Channel names present in the data.
    montage_name : str
        MNE standard montage identifier (e.g., 'GSN-HydroCel-256',
        'standard_1020', 'biosemi64', etc.)
    exclude : list[str] | None
        Channels to exclude (e.g., rim electrodes, fiducials).

    Returns
    -------
    ordered_channels : list[str]
        Channel names in montage order (after exclusion & intersection).
    xy : ndarray, shape (n_channels, 2)
        2-D projected positions.

    Raises
    ------
    ValueError
        If no valid channels are found.
    """
    import mne

    from .coordinates import azimuthal_equidistant_projection

    montage = mne.channels.make_standard_montage(montage_name)
    valid = set(montage.ch_names)
    exclude_set = set(exclude or [])
    keep = (set(ch_names) & valid) - exclude_set
    ordered = [ch for ch in montage.ch_names if ch in keep]

    if not ordered:
        return [], np.empty((0, 2))

    pos_3d = montage.get_positions()["ch_pos"]
    coords = np.array([pos_3d[ch] for ch in ordered])
    xy = azimuthal_equidistant_projection(coords)

    return ordered, xy


def create_mne_info(
    ch_names: List[str],
    montage_name: str = "GSN-HydroCel-256",
    exclude: Optional[List[str]] = None,
) -> Tuple[Any, List[str]]:
    """
    Build an MNE Info object with a subset montage.

    Useful for computing channel adjacency matrices needed for cluster-based
    permutation testing.

    Parameters
    ----------
    ch_names : list[str]
        Channel names to include.
    montage_name : str
        MNE standard montage identifier.
    exclude : list[str] | None
        Channels to exclude.

    Returns
    -------
    info : mne.Info | None
        MNE Info object with montage set, or None if no valid channels.
    ordered_channels : list[str]
        List of channel names in order.
    """
    import mne

    montage_std = mne.channels.make_standard_montage(montage_name)
    valid = set(montage_std.ch_names)
    exclude_set = set(exclude or [])
    keep = (set(ch_names) & valid) - exclude_set
    ordered = [ch for ch in montage_std.ch_names if ch in keep]

    if not ordered:
        return None, []

    positions = montage_std.get_positions()["ch_pos"]
    ch_pos = {ch: positions[ch] for ch in ordered}
    montage_sub = mne.channels.make_dig_montage(ch_pos=ch_pos, coord_frame="head")

    info = mne.create_info(ch_names=ordered, sfreq=100, ch_types="eeg")
    info.set_montage(montage_sub)

    return info, ordered
