import numpy as np
from ionex_formatter.reader import get_npz_data

def test_basic_structure(npz_file):
    content = np.load(npz_file)
    assert "map" in content
    assert "datetime" in content

def test_grid_dims(npz_file):
    content = np.load(npz_file)
    assert content["datetime"].shape[0] == content["map"].shape[0]
    assert content["map"].shape[1] == 71
    assert content["map"].shape[2] == 72

def test_data_vs_grid_dims(npz_file):
    maps, grid = get_npz_data(npz_file)
    assert maps.shape[0] == len(grid["time"])
    assert maps.shape[1] == len(grid["lats"])
    assert maps.shape[2] == len(grid["lons"])
    