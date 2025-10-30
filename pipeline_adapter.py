
from pathlib import Path
from typing import Optional, Tuple, List
from io_geotiff import save_geotiff

import user_pipeline

def run_simulation(name: str, lon: float, lat: float, mag_value: float, mag_type: str, event_date: str,
                   depth_km: float, radius_km: float, vs30_path: str, out_dir: str,
                   convert_to_intensity: bool, selected_gmpes=None, save_per_model: bool=False) -> Tuple[str, Optional[str], str, List[str], List[tuple]]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)

    # Ms <-> Mw conversion
    from mag_convert import ms_to_mw, mw_to_ms
    if mag_type.upper() == 'MS':
        ms = float(mag_value)
        mw = float(ms_to_mw(ms, event_date))
    else:
        mw = float(mag_value)
        ms = float(mw_to_ms(mw, event_date))

    # Generate PGA (m/s^2)
    pga_arr, transform, crs, per_model_preds, weights_list = user_pipeline.generate_pga(
        name, lon, lat, ms, mw, depth_km, radius_km, vs30_path, selected_gmpes=selected_gmpes
    )
    pga_path = out / f"{name}_PGA.tif"
    save_geotiff(pga_path, pga_arr, transform, crs)

    # Optional: save per-GMPE unweighted maps (masked to radius)
    per_model_paths: List[str] = []
    if save_per_model:
        for model_name, arr in per_model_preds:
            mp = out / f"{name}_PGA_{model_name}.tif"
            save_geotiff(mp, arr, transform, crs)
            per_model_paths.append(str(mp))

    # Save weights as txt
    weights_txt = out / f"{name}_GMPE_weights.txt"
    with open(weights_txt, 'w', encoding='utf-8') as f:
        f.write("# GMPE Weights\n")
        for model_name, w in weights_list:
            f.write(f"{model_name}\t{w:.6f}\n")

    intensity_path = None
    if convert_to_intensity:
        if hasattr(user_pipeline, 'pga_to_intensity'):
            I_arr = user_pipeline.pga_to_intensity(pga_arr)
        else:
            raise RuntimeError("Convert to intensity selected, but pga_to_intensity() not found.")
        intensity_path = out / f"{name}_IntensityI.tif"
        save_geotiff(intensity_path, I_arr, transform, crs)

        if hasattr(user_pipeline, 'classify_intensity_levels_from_pga'):
            lvl_arr = user_pipeline.classify_intensity_levels_from_pga(pga_arr)
            lvl_path = out / f"{name}_IntensityLevel.tif"
            save_geotiff(lvl_path, lvl_arr, transform, crs, nodata=None)

    return str(pga_path), (str(intensity_path) if intensity_path else None), str(weights_txt), per_model_paths, weights_list
