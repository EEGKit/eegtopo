"""
Cluster-based permutation testing for EEG topographic analysis.

This module provides statistical testing functionality using MNE-Python's
cluster-based permutation tests with spatial adjacency.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np


def cluster_permutation_test(
    data: np.ndarray,
    info: Any,
    n_permutations: int = 1024,
    threshold: Optional[Union[float, Dict]] = None,
    tail: int = 0,
    seed: int = 42,
    n_jobs: int = 1,
) -> Tuple[np.ndarray, List[np.ndarray], np.ndarray]:
    """
    Cluster-based permutation test on channel-level data.

    Wraps ``mne.stats.permutation_cluster_1samp_test`` with spatial
    adjacency derived from the channel montage.

    Parameters
    ----------
    data : ndarray (n_subjects, n_channels)
        Paired-difference values per subject and channel.
    info : mne.Info
        MNE Info with montage (used to compute channel adjacency).
    n_permutations : int
        Number of permutations.
    threshold : float | dict | None
        Cluster-forming threshold. Options:
        - None: Uses critical t for two-tailed p < 0.05 (default)
        - float: Direct t-value threshold
        - dict: MNE threshold parameters (e.g., {'start': 0, 'step': 0.2})
    tail : {-1, 0, 1}
        Tail of the test (0 = two-tailed).
    seed : int
        Random seed for reproducibility.
    n_jobs : int
        Number of parallel jobs.

    Returns
    -------
    t_obs : ndarray (n_channels,)
        Observed t-statistic per channel.
    clusters : list of ndarray
        Boolean masks indicating cluster membership.
    cluster_pv : ndarray
        p-value per cluster.
    """
    try:
        from mne.stats import permutation_cluster_1samp_test
        from mne.channels import find_ch_adjacency
        from scipy.stats import t as t_dist
    except ImportError:
        raise ImportError("mne and scipy are required for cluster testing")

    adjacency, _ = find_ch_adjacency(info, ch_type="eeg")

    # Handle threshold
    if threshold is None:
        # Default: critical t for two-tailed p < 0.05
        n_obs = data.shape[0]
        threshold = t_dist.ppf(1 - 0.025, df=n_obs - 1)
    elif isinstance(threshold, dict):
        # MNE-style threshold dict
        pass  # Let MNE handle it

    t_obs, clusters, cluster_pv, _ = permutation_cluster_1samp_test(
        data,
        adjacency=adjacency,
        n_permutations=n_permutations,
        threshold=threshold,
        tail=tail,
        seed=seed,
        out_type="mask",
        n_jobs=n_jobs,
        verbose=False,
    )

    return t_obs, clusters, cluster_pv
