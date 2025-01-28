import numpy as np
import pytz
from datetime import datetime
from typing import Tuple, Any
from pathlib import Path

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