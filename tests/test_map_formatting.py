import pytest

from datetime import datetime
from ionex_formatter.spatial import SpatialRange
from ionex_formatter.formatter import (
    IonexFile,
    IonexMapType
)
from ionex_formatter.ionex_map import (
    IonexMap,
    GridCell
)

class TestMapFormating():

    @pytest.fixture
    def formatter(self):
        return IonexFile()

    def test_map_lines(self, map_lines, map_data):
        cells = GridCell.get_list_from_csv(map_data)
        ionex_map = IonexMap(lat_range=SpatialRange(87.5, -87.5, -87.5),
                             lon_range=SpatialRange(-180, 180, 5),
                             height=450,
                             epoch=datetime(2010, 12, 28)
        ) 
        ionex_map.set_data(cells)
        formatter = IonexFile()
        formatter.set_maps(
            {datetime(2010, 12, 28):ionex_map}, 
            dtype=IonexMapType.TEC
        )
        lines = formatter.get_map_lines(
            IonexMapType.TEC, 
            datetime(2010, 12, 28)
        )
        assert "\n".join(lines) == map_lines
