"""
Head outline drawing for EEG topographic plots.

This module provides the HeadOutline class for managing head geometry
and drawing head outlines, noses, and ears in EEGLAB/MNE style.
"""

from typing import Tuple, Optional
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


class HeadOutline:
    """
    Manages head outline geometry for topographic plots.

    This class handles the calculation of head dimensions following MNE/EEGLAB
    conventions:
    - Head outline uses a standard radius based on electrode positions
    - The head circle represents the 10-20 circumference line
    - Interpolation extends beyond head to cover all electrodes
    """

    def __init__(self, xy: np.ndarray, head_radius: Optional[float] = None):
        """
        Parameters
        ----------
        xy : ndarray (n, 2)
            2-D electrode positions
        head_radius : float | None
            Head outline radius. If None, auto-detects based on electrode
            positions using the 90th percentile approach (MNE-style).
        """
        self.xy = np.asarray(xy, dtype=float)

        # Calculate center (mean of electrode positions)
        self.cx = float(np.mean(self.xy[:, 0]))
        self.cy = float(np.mean(self.xy[:, 1]))

        # Calculate distances from center
        dists = np.sqrt((self.xy[:, 0] - self.cx) ** 2 + (self.xy[:, 1] - self.cy) ** 2)

        # Head radius: use 90th percentile to avoid outlier influence
        # This ensures consistent head size regardless of electrode coverage
        if head_radius is None:
            self.radius = float(np.percentile(dists, 90))
        else:
            self.radius = float(head_radius)

        # Ensure head radius is reasonable (not too small)
        min_radius = np.max(dists) * 0.5
        self.radius = max(self.radius, min_radius)

        # Extended radius for interpolation grid
        # Must cover ALL electrodes plus padding
        max_dist = np.max(dists)
        self.extended_radius = max_dist * 1.05  # 5% padding beyond furthest electrode

    def draw(
        self,
        ax: matplotlib.axes.Axes,
        nose: bool = True,
        ears: bool = True,
        linewidth: float = 1.5,
        color: str = "black",
    ):
        """Draw the head outline on the given axes."""
        # Head circle
        head = Circle(
            (self.cx, self.cy),
            self.radius,
            fill=False,
            lw=linewidth,
            ec=color,
            zorder=3,
        )
        ax.add_patch(head)

        if nose:
            # Nose - EEGLAB style: above the head circle
            nw = self.radius * 0.12
            nh = self.radius * 0.12
            ny = self.cy + self.radius
            ax.plot(
                [self.cx - nw, self.cx, self.cx + nw],
                [ny - nh * 0.3, ny + nh, ny - nh * 0.3],
                color=color,
                lw=linewidth,
                zorder=3,
                clip_on=False,
            )

        if ears:
            # Ears - EEGLAB style ears on sides of head
            ew = self.radius * 0.06
            eh = self.radius * 0.16
            for side in (-1, 1):
                ex = self.cx + side * self.radius
                # Create ear shape
                ear_y = np.linspace(-eh, eh, 50) + self.cy
                ear_curve = ex + side * ew * (1 - (ear_y - self.cy) ** 2 / eh**2) ** 0.5
                ax.plot(
                    ear_curve, ear_y, color=color, lw=linewidth, zorder=3, clip_on=False
                )

    def get_grid_bounds(
        self, grid_res: int = 256
    ) -> Tuple[np.ndarray, np.ndarray, float, float, float, float]:
        """
        Get interpolation grid bounds that cover all electrodes.

        Returns
        -------
        Xi, Yi : meshgrid arrays
        xmin, xmax, ymin, ymax : grid bounds
        """
        # Grid must encompass ALL electrodes, not just head
        span = 2 * self.extended_radius
        half = span / 2

        xmin, xmax = self.cx - half, self.cx + half
        ymin, ymax = self.cy - half, self.cy + half

        xi = np.linspace(xmin, xmax, grid_res)
        yi = np.linspace(ymin, ymax, grid_res)
        Xi, Yi = np.meshgrid(xi, yi)

        return Xi, Yi, xmin, xmax, ymin, ymax

    def get_mask(self, Xi: np.ndarray, Yi: np.ndarray) -> np.ndarray:
        """
        Get mask for points inside head circle.

        Returns
        -------
        mask : ndarray
            Boolean array, True for points inside head circle
        """
        dist = np.sqrt((Xi - self.cx) ** 2 + (Yi - self.cy) ** 2)
        return dist <= self.radius
