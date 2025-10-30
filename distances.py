
import numpy as np

def Cal_Re(lon_src: float, lat_src: float, lon_grid: np.ndarray, lat_grid: np.ndarray) -> np.ndarray:
    lon_src = float(lon_src); lat_src = float(lat_src)
    rad = np.pi/180.0
    lon1 = lon_src*rad; lat1 = lat_src*rad
    lon2 = np.asarray(lon_grid, dtype=float)*rad
    lat2 = np.asarray(lat_grid, dtype=float)*rad
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2.0)**2
    c = 2.0*np.arcsin(np.minimum(1.0, np.sqrt(a)))
    return 6371.0 * c

def Cal_Rh(Re: np.ndarray, depth_km: float) -> np.ndarray:
    Re = np.asarray(Re, dtype=float)
    return np.sqrt(Re**2 + float(depth_km)**2)
