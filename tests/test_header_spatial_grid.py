import pytest
from ionex_formatter import formatter
from ionex_formatter.spatial import SpatialRange

class TestSpatialGridDimensions():
    
    @pytest.fixture
    def file_formatter(self):
        ionex_file_formatter = formatter.IonexFile()
        lat_grid = SpatialRange(87.5, -87.5, -2.5)
        lon_grid = SpatialRange(-180, 180, 5)
        height_grid = SpatialRange(450, 450, 0)
        ionex_file_formatter.set_spatial_grid(lat_grid, lon_grid, height_grid)
        return ionex_file_formatter
    
    def test_lat_grid(self, file_formatter):
        lat_lines = file_formatter.header["LAT1 / LAT2 / DLAT"] 
        assert len(lat_lines) == 1
        assert lat_lines[0] == "    87.5 -87.5  -2.5                    " \
                               "                    LAT1 / LAT2 / DLAT  "

    def test_lon_grid(self, file_formatter):
        lon_lines = file_formatter.header["LON1 / LON2 / DLON"] 
        assert len(lon_lines) == 1
        assert lon_lines[0] == "  -180.0 180.0   5.0                    " \
                               "                    LON1 / LON2 / DLON  "

    def test_height_grid(self, file_formatter):
        heigth_lines = file_formatter.header["HGT1 / HGT2 / DHGT"] 
        assert len(heigth_lines) == 1
        assert heigth_lines[0] == "   450.0 450.0   0.0                    " \
                                  "                    HGT1 / HGT2 / DHGT  "
