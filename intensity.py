
import numpy as np

def pga_to_intensity(pga_arr):
    p = np.asarray(pga_arr, dtype=float)
    return 1.5*np.log(np.maximum(p, 1e-6)) + 8.0

def classify_intensity_levels_from_pga(pga_arr):
    p = np.asarray(pga_arr, dtype=float)
    levels = np.full(p.shape, np.nan, dtype=float)
    m = np.isfinite(p)
    levels[(m) & (p < 0.457)] = 0
    levels[(m) & (p >= 0.457) & (p <= 0.936)] = 1
    levels[(m) & (p > 0.936) & (p <= 1.94)] = 2
    levels[(m) & (p > 1.94) & (p <= 4.01)] = 3
    levels[(m) & (p > 4.01) & (p <= 8.30)] = 4
    levels[(m) & (p > 8.30) & (p <= 17.2)] = 5
    levels[(m) & (p > 17.2) & (p <= 35.5)] = 6
    levels[(m) & (p > 35.5)] = 7
    return levels
