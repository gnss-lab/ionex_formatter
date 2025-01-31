import numpy as np
import pytz
from datetime import datetime
from typing import Tuple, Any
from pathlib import Path
from ionex_formatter.ionex_map import GridCell, IonexMap, SpatialRange
from ionex_formatter.formatter import IonexMapType

def get_npz_data(fpath: Path) -> Tuple[np.ndarray, dict[str, Any]]:
    """Loads content of maps.npz file and returns data along with grid
    
    In general data are 3-dimensional data with times, latitudes, and 
    longitudes as axis.

    :param fpath: path of the file with data
    :type data: pathlib.Path

    Returns data and grids. grids include time, lat, lon and mesh spatial grid
    """
    data = np.load(fpath)
    timestamps = data["datetime"]
    datetimes = [datetime.fromtimestamp(t, tz=pytz.utc) for t in timestamps]
    # TODO put spatial grid in file to avoid misreading
    grids = {
        "time": datetimes,
        "lats": [lat / 10 for lat in range(875, -900, -25)],
        "lons": [lon for lon in range(-180, 180, 5)]
    }
    grids["spatial"] = np.meshgrid(grids["lons"], grids["lats"])

    return data['map'], grids

def get_single_map(
    map_data: np.ndarray, 
    epoch: datetime, 
    lat_grid: np.ndarray, 
    lon_grid: np.ndarray
) -> IonexMap:
    """
    Convert single map from NPZ file to internal object IonexMap
    """
    vals = map_data.flatten()
    lats = lat_grid.flatten()
    lons = lon_grid.flatten()
    cells = list()
    for val, lat, lon in zip(vals, lats, lons):
        cell = GridCell()
        cell.lat = float(lat)
        cell.lon = float(lon)
        cell.val = int(round(float(val), 3) * 10)
        cells.append(cell)  
        if lon == -180:
            cell = GridCell()
            cell.lat = float(lat)
            cell.lon = -float(lon)
            cell.val = int(round(float(val), 3) * 10)
            cells.append(cell)  
    ionex_map = IonexMap(
        lat_range=SpatialRange(87.5, -87.5, -2.5),
        lon_range=SpatialRange(-180, 180, 5),
        height=450,
        epoch=epoch
    ) 
    ionex_map.set_data(cells)
    return ionex_map


def convet_npz_to_internal(fpath: Path) -> dict[IonexMapType, dict[datetime, IonexMap]]:
    """
    Converts entire file to dict of maps that can be directly feeded to formatter
    """
    maps, grids = get_npz_data(fpath)
    lon_grid = grids["spatial"][0]
    lat_grid = grids["spatial"][1]
    prepared_data = {}
    for epoch in grids["time"]:
        ionex_map = get_single_map(maps, epoch, lat_grid, lon_grid)
        prepared_data[epoch] = ionex_map
    # TODO make for different maps types
    return {IonexMapType.TEC: prepared_data}