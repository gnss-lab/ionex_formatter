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

    @pytest.fixture
    def sample_map_lines(self):
        map_lines = """
     1                                                      START OF TEC MAP    
  2010    12    28     0     0     0                        EPOCH OF CURRENT MAP
    87.5-180.0 180.0   5.0 450.0                            LAT/LON1/LON2/DLON/H
   49   50   50   49   47   46   44   43   42   41   40   39   38   38   38   37
   36   34   31   32   33   32   31   30   32   32   32   30   31   32   34   35
   35   35   34   34   32   33   33   33   33   32   32   31   30   30   30   30
   31   31   30   30   33   35   34   32   31   31   34   37   38   38   38   39
   39   39   40   42   43   44   45   44   42                                   
     0.0-180.0 180.0   5.0 450.0                            LAT/LON1/LON2/DLON/H
  217  199  156  128   99   83   84   88   88   82   85   84   78   72   63   65
   70   82   94  115  127  111  114  102   88   78   70   64   55   52   58   62
   65   58   47   46   52   66   96  114  117  130  149  157  171  183  192  198
  204  211  223  217  219  234  259  269  288  304  313  323  340  334  317  316
  298  280  269  265  264  261  252  242  220                                   
   -87.5-180.0 180.0   5.0 450.0                            LAT/LON1/LON2/DLON/H
  128  130  132  133  126  123  120  133  144  140  143  149  153  142  140  140
  137  141  127  133  147  146  142  144  139  133  126  125  126  127  127  126
  128  128  126  132  134  132  124  125  135  143  143  132  127  132  145  140
  134  132  129  129  128  126  121  117  115  114  112  115  122  121  126  126
  124  126  128  128  127  126  128  129  129                                   
     1                                                      END OF TEC MAP      
"""
        map_lines = map_lines[1:-1] # to remove \n
        return map_lines

    def test_map_lines(self, sample_map_lines, map_data, formatter):
        cells = GridCell.get_list_from_csv(map_data)
        ionex_map = IonexMap(lat_range=SpatialRange(87.5, -87.5, -87.5),
                             lon_range=SpatialRange(-180, 180, 5),
                             height=450,
                             epoch=datetime(2010, 12, 28)
        ) 
        ionex_map.set_data(cells)
        formatter.set_maps(
            {datetime(2010, 12, 28):ionex_map}, 
            dtype=IonexMapType.TEC
        )
        lines = formatter.get_map_lines(
            IonexMapType.TEC, 
            datetime(2010, 12, 28)
        )
        assert "\n".join(lines) == sample_map_lines
