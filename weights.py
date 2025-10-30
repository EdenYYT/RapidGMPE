
from typing import List
import numpy as np

# ----------------------------
# Strict B-version (raw method)
# ----------------------------
# 1) Log-transform PGA samples (ln) before fitting (only positive values).
# 2) Fit mu, sigma via MLE (ddof=0).
# 3) Compute base-2 LLH without clipping or shifting.
# 4) DSI selection: keep models with DSI > 0; others set to -1.
#    Final positive weights are proportional to 2^(-LLH) *within the positive-DSI subset*,
#    normalized to sum to 1 over the kept subset.
# Notes:
# - If all models are excluded (no positive-DSI), fall back to uniform weights (1/M).
# - If a model has insufficient/invalid data, its LLH becomes +inf and it will be excluded.

def _fit_mu_sigma_mle(x: np.ndarray):
    """Return (mu, sigma_MLE) using ddof=0. Require at least 3 points."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < 3:
        return float("nan"), float("nan")
    mu = float(np.mean(x))
    # ddof=0 MLE
    sigma = float(np.sqrt(np.mean((x - mu) ** 2)))
    if not np.isfinite(sigma) or sigma <= 0:
        return float("nan"), float("nan")
    return mu, sigma

def _llh_base2(x: np.ndarray, mu: float, sigma: float) -> float:
    """Base-2 average negative log-likelihood for Normal(mu, sigma^2)."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    N = x.size
    if N == 0 or not np.isfinite(mu) or not np.isfinite(sigma) or sigma <= 0:
        return float("inf")
    term1 = np.log2(np.sqrt(2.0 * np.pi))
    term2 = np.log2(sigma)
    term3 = (np.log2(np.e) / N) * np.sum((x - mu) ** 2) / (2.0 * sigma ** 2)
    return float(term1 + term2 + term3)

def _weights_from_llh_raw(llh_list: np.ndarray) -> np.ndarray:
    """Raw DSI method: keep only DSI>0, others -> -1; normalize within kept subset."""
    llh = np.asarray(llh_list, dtype=float)
    mask_finite = np.isfinite(llh)
    M = int(np.sum(mask_finite))
    if M == 0:
        return np.full_like(llh, -1.0)

    # Unshifted weights ~ 2^(-LLH)
    w_all = np.exp(-np.log(2.0) * llh)
    # Normalize over finite entries to compute DSI
    w_all = np.where(mask_finite, w_all, 0.0)
    tot = w_all.sum()
    if not np.isfinite(tot) or tot <= 0:
        # No usable models → return uniform (no exclusion)
        return np.where(mask_finite, 1.0 / M, -1.0)

    w_norm = w_all / tot
    w_unif = 1.0 / M
    DSI = 100.0 * (w_norm - w_unif) / w_unif

    # Keep only positive-DSI models
    keep = (DSI > 0) & mask_finite
    if not np.any(keep):
        # If all non-positive → uniform (no exclusion)
        out = np.where(mask_finite, 1.0 / M, -1.0)
        return out

    # Recompute weights only on kept subset (proportional to 2^(-LLH))
    kept = w_all[keep]
    kept_sum = kept.sum()
    if not np.isfinite(kept_sum) or kept_sum <= 0:
        # Fallback: uniform on kept
        kept_w = np.full(kept.shape, 1.0 / kept.size)
    else:
        kept_w = kept / kept_sum

    out = np.full_like(llh, -1.0)
    out[keep] = kept_w
    return out

def estimate_weights(samples: List[np.ndarray]) -> np.ndarray:
    """Compute weights for GMPEs using the strict B-version raw method.

    Parameters
    ----------
    samples : List[np.ndarray]
        Each element is the PGA predictions for a GMPE at the same set of grid cells.
        We will log-transform (natural log) the positive values before fitting.

    Returns
    -------
    np.ndarray
        Weights array, where excluded models are -1. If all excluded, uniform over finite models.
    """
    llh_list = []
    for s in samples:
        s = np.asarray(s, dtype=float)
        s = s[np.isfinite(s) & (s > 0.0)]  # only positive PGA, finite
        if s.size < 3:
            llh_list.append(float("inf"))
            continue
        s_log = np.log(s)  # log-transform before fitting
        mu, sigma = _fit_mu_sigma_mle(s_log)
        llh = _llh_base2(s_log, mu, sigma)
        llh_list.append(llh)

    w = _weights_from_llh_raw(np.array(llh_list, dtype=float))
    return w
