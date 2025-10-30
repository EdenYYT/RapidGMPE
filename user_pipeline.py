
from __future__ import annotations
from typing import Tuple, Optional, List
import numpy as np

from gmpe_registry import list_gmpes, set_gmpes, active_pairs
from vs30_io import read_vs30_crop_resample
from distances import Cal_Re, Cal_Rh
from weights import estimate_weights
from intensity import pga_to_intensity, classify_intensity_levels_from_pga  # re-exported

__all__ = [
    "list_gmpes", "set_gmpes",
    "generate_pga",
    "pga_to_intensity", "classify_intensity_levels_from_pga",
]

def generate_pga(name: str, lon: float, lat: float, ms: float, mw: float, depth_km: float,
                 radius_km: float, vs30_path: str, selected_gmpes: Optional[List[str]]=None) -> Tuple[np.ndarray, object, object, list, list]:
    """
    Returns (pga_arr [m/s^2], transform, crs, per_model_preds, weights_list).
    - per_model_preds: List[(model_name, unweighted_pga_grid)]
    - weights_list:    List[(model_name, weight)]
    - Output GeoTIFF extent is rectangular (crop to square bbox of radius_km in EPSG:3395),
      but values are only preserved inside the radius; outside are NaN.
    """
    vs30, lat_grid, lon_grid, transform, crs = read_vs30_crop_resample(vs30_path, lon, lat, radius_km)

    Re = Cal_Re(lon, lat, lon_grid, lat_grid)
    Rh = Cal_Rh(Re, depth_km)
    mask = Re <= float(radius_km)  # only inside radius are valid for weights & outputs

    # Model subset
    set_gmpes(selected_gmpes)  # None/[] means "use all"
    active = active_pairs()
    print("[GMPE] Active models:", [nm for nm,_ in active])
    if not active:
        raise RuntimeError("No active GMPEs. Check GMPE.py registry.")

    # Use ALL cells within radius for weighting
    idx = np.where(mask)

    # Collect samples per GMPE
    samples = []
    for name_i, fn in active:
        pred = fn(float(ms), float(mw), Re[idx], Rh[idx], vs30[idx], float(depth_km))
        samples.append(np.asarray(pred, dtype=float))

    w_arr = estimate_weights(samples)
    weights_list = [(nm, float(wi)) for (nm,_), wi in zip(active, w_arr)]

    # Per-model full predictions and weighted sum
    per_model_preds = []
    pga_stack = []
    for (name_i, fn), wi in zip(active, w_arr):
        pred_full = fn(float(ms), float(mw), Re, Rh, vs30, float(depth_km))
        arr = np.asarray(pred_full, dtype=float)
        # mask per-model outside radius
        a = arr.copy(); a[~mask] = np.nan
        per_model_preds.append((name_i, a))
        if wi > 0 and np.isfinite(wi):
            pga_stack.append(wi * a)

    if not pga_stack:
        raise RuntimeError("No predictions produced by active GMPEs.")

    pga = np.sum(pga_stack, axis=0)
    return pga, transform, crs, per_model_preds, weights_list
