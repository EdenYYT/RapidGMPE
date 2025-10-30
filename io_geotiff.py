
import numpy as np
import rasterio

def save_geotiff(path, arr, transform, crs, nodata=None):
    if arr.ndim != 2: raise ValueError("Expect 2D array")
    h, w = arr.shape
    with rasterio.open(path, 'w', driver='GTiff', width=w, height=h, count=1,
                       dtype=arr.dtype, crs=crs, transform=transform, nodata=nodata) as dst:
        data = np.array(arr, copy=False)
        dst.write(data, 1)
