"""
Topographic plotting functions for EEG data.

This module provides functions for creating publication-quality topographic
maps of EEG data with proper head outlines and interpolation.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from .head import HeadOutline
from .interpolation import interpolate_topography


def plot_topomap(
    values: Union[Dict[str, float], np.ndarray],
    xy: np.ndarray,
    ch_names: Optional[List[str]] = None,
    *,
    ax: Optional[matplotlib.axes.Axes] = None,
    cmap: str = "RdBu_r",
    vlim: Optional[Tuple[float, float]] = None,
    sig_mask: Optional[np.ndarray] = None,
    title: Optional[str] = None,
    colorbar: bool = True,
    head: bool = True,
    grid_res: int = 256,
    nan_fill: float = 0.0,
    sig_dot_size: float = 24,
    non_sig_dot_size: float = 6,
    sig_alpha: float = 0.9,
    non_sig_alpha: float = 0.3,
    extrapolate: bool = True,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes, Any]:
    """
    Plot an interpolated topographic scalp map.

    Parameters
    ----------
    values : dict | array-like
        Per-channel scalar values. If dict, keyed by channel name;
        missing channels are filled with *nan_fill*. If array-like, must
        match the length of *xy*.
    xy : ndarray (n, 2)
        2-D electrode positions.
    ch_names : list[str] | None
        Channel names corresponding to rows of *xy*. Required when
        *values* is a dict.
    ax : matplotlib Axes | None
        Target axes. A new figure is created when ``None``.
    cmap : str
        Matplotlib colourmap name.
    vlim : tuple (vmin, vmax) | None
        Colour limits. Auto-computed from data when ``None``.
    sig_mask : array-like of bool | None
        Boolean mask (same length as *xy*). ``True`` = significant
        (bold dot); ``False`` = non-significant (small dot).
        When ``None``, all electrodes get small dots.
    title : str | None
        Axes title.
    colorbar : bool
        Add a colour bar.
    head : bool
        Draw the head outline.
    grid_res : int
        Interpolation grid resolution (default 256 for smooth coverage).
    nan_fill : float
        Substitute for NaN / missing channels before interpolation.
    sig_dot_size : float
        Size of significant electrode markers (default 24).
    non_sig_dot_size : float
        Size of non-significant electrode markers (default 6).
    sig_alpha : float
        Alpha for significant markers.
    non_sig_alpha : float
        Alpha for non-significant markers.
    extrapolate : bool
        Whether to add extrapolation points for smoother interpolation
        at the edges (default True).

    Returns
    -------
    fig : Figure
    ax : Axes
    im : AxesImage
    """
    xy = np.asarray(xy, dtype=float)
    n = len(xy)

    # --- Resolve values to 1-D array ---
    if isinstance(values, dict):
        if ch_names is None:
            raise ValueError("ch_names required when values is a dict")
        data = np.array(
            [values.get(ch, np.nan) for ch in ch_names],
            dtype=float,
        )
    else:
        data = np.asarray(values, dtype=float)

    if len(data) != n:
        raise ValueError(f"len(values)={len(data)} != len(xy)={n}")

    # Replace NaN with nan_fill for interpolation
    data_clean = np.where(np.isfinite(data), data, nan_fill)

    # --- Auto vlim ---
    if vlim is None:
        vmax = np.percentile(np.abs(data_clean), 97)
        vmax = max(vmax, 1e-6)
        vlim = (-vmax, vmax)

    # --- Create head outline ---
    head_outline = HeadOutline(xy)
    Xi, Yi, xmin, xmax, ymin, ymax = head_outline.get_grid_bounds(grid_res)

    # --- Interpolation ---
    Zi = interpolate_topography(xy, data_clean, Xi, Yi, extrapolate=extrapolate)

    # Mask outside head circle for visualization
    # But keep interpolation data for electrodes outside head
    mask = head_outline.get_mask(Xi, Yi)
    Zi_masked = Zi.copy()
    Zi_masked[~mask] = np.nan

    # --- Plot ---
    created_fig = ax is None
    if created_fig:
        fig, ax = plt.subplots(figsize=(6, 5))
    else:
        fig = ax.figure

    # Plot interpolated surface
    im = ax.imshow(
        Zi_masked,
        extent=[xmin, xmax, ymin, ymax],
        origin="lower",
        cmap=cmap,
        vmin=vlim[0],
        vmax=vlim[1],
        aspect="equal",
        interpolation="bilinear",
    )

    # Head outline
    if head:
        head_outline.draw(ax)

    # Electrode markers - always show all electrodes
    if sig_mask is not None:
        sig_mask = np.asarray(sig_mask, dtype=bool)
        non_sig = ~sig_mask
        ax.scatter(
            xy[non_sig, 0],
            xy[non_sig, 1],
            s=non_sig_dot_size,
            color="black",
            alpha=non_sig_alpha,
            zorder=4,
        )
        if sig_mask.any():
            ax.scatter(
                xy[sig_mask, 0],
                xy[sig_mask, 1],
                s=sig_dot_size,
                color="black",
                alpha=sig_alpha,
                zorder=5,
            )
    else:
        ax.scatter(
            xy[:, 0],
            xy[:, 1],
            s=non_sig_dot_size,
            color="black",
            alpha=non_sig_alpha,
            zorder=4,
        )

    if title:
        ax.set_title(title, fontsize=12, pad=10)
    if colorbar:
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.06)

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig, ax, im


def plot_cluster_topomap(
    t_obs: np.ndarray,
    clusters: List[np.ndarray],
    cluster_pv: np.ndarray,
    xy: np.ndarray,
    ch_names: Optional[List[str]] = None,
    alpha: float = 0.05,
    **kwargs,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes, Any]:
    """
    Plot a t-statistic topographic map with significant clusters highlighted.

    Parameters
    ----------
    t_obs : ndarray (n_channels,)
        Observed t-statistics.
    clusters : list of ndarray
        Boolean cluster masks from cluster_permutation_test.
    cluster_pv : ndarray
        p-value per cluster.
    xy : ndarray (n, 2)
        2-D electrode positions.
    ch_names : list[str] | None
        Channel names.
    alpha : float
        Significance threshold for cluster p-values.
    **kwargs
        Passed to plot_topomap.

    Returns
    -------
    fig, ax, im
    """
    sig_mask = np.zeros(len(t_obs), dtype=bool)
    for cluster, pv in zip(clusters, cluster_pv):
        if pv < alpha:
            sig_mask |= cluster

    return plot_topomap(
        t_obs,
        xy,
        ch_names=ch_names,
        sig_mask=sig_mask if sig_mask.any() else None,
        **kwargs,
    )
