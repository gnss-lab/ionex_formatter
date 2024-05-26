import pytest
from datetime import datetime
from ionex_formatter.ionex_map import (
    IonexMap,
    GridCell,
    LongitudeCellIsNotSet
)
from ionex_formatter.spatial import SpatialRange

class TestDatetimeFormatting:
        
    def test_basic(self, map_data):
        cells = GridCell.get_list_from_csv(map_data)
        ionex_map = IonexMap(lat_range=SpatialRange(87.5, -87.5, -87.5),
                             lon_range=SpatialRange(-180, 180, 5),
                             height=450,
                             epoch=datetime(2010, 12, 28)
        ) 
        ionex_map.set_data(cells)
        assert ionex_map.get_cell(87.5, -165) == 49
        assert ionex_map.get_cell(0, 0) == 52
        assert ionex_map.get_cell(-87.5, 160) == 127

    def test_missing_lat_data(self, map_data):
        cells = GridCell.get_list_from_csv(map_data)
        corrupted_data = cells[:73] + cells[-73:]
        ionex_map = IonexMap(lat_range=SpatialRange(87.5, -87.5, -87.5),
                             lon_range=SpatialRange(-180, 180, 5),
                             height=450,
                             epoch=datetime(2010, 12, 28)
        ) 
        with pytest.raises(ValueError):
            ionex_map.set_data(corrupted_data)

    def test_missing_lat_range(self, map_data):
        cells = GridCell.get_list_from_csv(map_data)
        # changed range so there are no such a latitudes in data
        ionex_map = IonexMap(lat_range=SpatialRange(87.5, -87.5, -2.5), 
                             lon_range=SpatialRange(-180, 180, 5),
                             height=450,
                             epoch=datetime(2010, 12, 28)
        ) 
        with pytest.raises(ValueError):
            ionex_map.set_data(cells)

    def test_missing_lon_data(self, map_data):
        cells = GridCell.get_list_from_csv(map_data)
        corrupted_data = cells[:-1]
        ionex_map = IonexMap(lat_range=SpatialRange(87.5, -87.5, -87.5),
                             lon_range=SpatialRange(-180, 180, 5),
                             height=450,
                             epoch=datetime(2010, 12, 28)
        ) 
        with pytest.raises(LongitudeCellIsNotSet):
            ionex_map.set_data(corrupted_data)

    def test_missing_lon_range(self, map_data):
        cells = GridCell.get_list_from_csv(map_data)
        # changed range so there are no such a longitudes in data
        ionex_map = IonexMap(lat_range=SpatialRange(87.5, -87.5, -87.5),
                             lon_range=SpatialRange(-180, 180, 2.5),
                             height=450,
                             epoch=datetime(2010, 12, 28)
        ) 
        with pytest.raises(LongitudeCellIsNotSet):
            ionex_map.set_data(cells)

    def test_set_data(self, map_data):
        cells = GridCell.get_list_from_csv(map_data)
        ionex_map = IonexMap(lat_range=SpatialRange(87.5, -87.5, -87.5),
                             lon_range=SpatialRange(180, -180, -5),
                             height=550,
                             epoch=datetime(2010, 12, 28)
        ) 
        ionex_map.set_data(cells)
        assert ionex_map.get_cell(-87.5, 165) == 126
