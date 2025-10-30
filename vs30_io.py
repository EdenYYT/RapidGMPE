"""
vs30_io.py
----------
Radius-based crop & resample around an epicenter using a metric CRS.

Workflow
1) Transform epicenter (lon/lat, EPSG:4326) to EPSG:3395 (meters).
2) Build a square bounding box with side = 2 * radius_km (in meters).
3) Create a target grid in EPSG:3395 with pixel size = target_resolution_km (meters).
4) Reproject source VS30 into that target grid (crop + resample in one step).
5) Build per-pixel center coordinates (x,y) analytically from the target transform,
   then inverse-transform to lon/lat (EPSG:4326) for distance calculation.

Returns
-------
vs30 : (H, W) ndarray
    Cropped & resampled VS30 grid (float), nodata as NaN.
lat_grid, lon_grid : (H, W) ndarray
    Latitude/Longitude grids (degrees) matching vs30 shape.
transform : rasterio.Affine
    Target grid transform in EPSG:3395.
crs : rasterio.crs.CRS
    Target CRS (EPSG:3395).
"""
from typing import Tuple
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from pyproj import Transformer, CRS


def read_vs30_crop_resample(
    vs30_path: str,
    center_lon: float,
    center_lat: float,
    radius_km: float,
    target_resolution_km: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, object, object]:
    """Crop & resample VS30 around (lon,lat) within a given radius.

    Parameters
    ----------
    vs30_path : str
        Path to source VS30 GeoTIFF.
    center_lon, center_lat : float
        Epicenter longitude/latitude in degrees (EPSG:4326).
    radius_km : float
        Half side-length of the square window (km); output bbox is 2*radius_km per side.
    target_resolution_km : float, default 1.0
        Target pixel size in kilometers (in the metric 3395 space).

    Returns
    -------
    vs30, lat_grid, lon_grid, transform, crs
        See module docstring.
    """
    radius_m = float(radius_km) * 1000.0
    res_m = float(target_resolution_km) * 1000.0

    # Target/projected CRS for cropping/resampling (meters)
    dst_crs = CRS.from_epsg(3395)  # World Mercator

    # Define forward/backward transformers
    to_3395 = Transformer.from_crs("EPSG:4326", dst_crs, always_xy=True)  # lon/lat -> 3395
    to_ll   = Transformer.from_crs(dst_crs, "EPSG:4326", always_xy=True)  # 3395 -> lon/lat

    # Center point in meters
    cx, cy = to_3395.transform(float(center_lon), float(center_lat))

    # Square bbox in meters
    xmin, xmax = cx - radius_m, cx + radius_m
    ymin, ymax = cy - radius_m, cy + radius_m

    # Output grid geometry
    width  = max(1, int(np.ceil((xmax - xmin) / res_m)))
    height = max(1, int(np.ceil((ymax - ymin) / res_m)))
    transform = from_origin(xmin, ymax, res_m, res_m)  # (xoff, yoff, xsize, ysize)

    # Allocate destination array and reproject
    with rasterio.open(vs30_path) as src:
        src_nodata = src.nodata
        # Prepare destination array in float; nodata as NaN
        dst = np.full((height, width), np.nan, dtype=np.float32)

        reproject(
            source=rasterio.band(src, 1),
            destination=dst,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            resampling=Resampling.bilinear,
            src_nodata=src_nodata,
            dst_nodata=np.nan,
        )

    # Build center-of-pixel x/y grids analytically (robust across rasterio versions)
    rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
    xs = xmin + (cols + 0.5) * res_m
    ys = ymax - (rows + 0.5) * res_m

    # Back to lon/lat for distance (vectorized); keep (H,W) shape
    lon_grid, lat_grid = to_ll.transform(xs, ys)

    return dst, np.asarray(lat_grid), np.asarray(lon_grid), transform, dst_crs
