from collections import defaultdict
from datetime import datetime
from .spatial import SpatialRange

class LongitudeCellIsNotSet(Exception):
    """
    Raised when user didn't define value for longitude cell
    """

    def __init__(self, lons: list[float], lat: float):
        msg = "Check longitudes {} for latitude {}, some values are missing."
        msg.format(lons, lat)
        super().__init__(msg)


class GridCell():
    lat: float 
    lon: float
    val: float

    @staticmethod
    def get_list_from_csv(data: list[tuple]) -> list:
        """
        Converts list of tuples (lat, lon, val) into GridCell objects

        :param data: list of tuples in form of (lat, lon, val)
        :type: list

        :rtype: list of GridCell
        """
        result = list()
        for cell in data:
            c = GridCell()
            c.lat = cell[0]
            c.lon = cell[1]
            c.val = cell[2]
            result.append(c)
        return result


class IonexMap():
    """
    Stores ionex map as it is written in file.

    Format assumes stroing all longitude cell for a single latitude. Hence
    this class implement the same feature. The object that stores map is a dict 
    of lists the keys of dict are latitudes.

     1                                                      START OF TEC MAP    
  2010    12    28     0     0     0                        EPOCH OF CURRENT MAP
    87.5-180.0 180.0   5.0 450.0                            LAT/LON1/LON2/DLON/H
   49   50   50   49   47   46   44   43   42   41   40   39   38   38   38   37
   36   34   31   32   33   32   31   30   32   32   32   30   31   32   34   35
   35   35   34   34   32   33   33   33   33   32   32   31   30   30   30   30
   31   31   30   30   33   35   34   32   31   31   34   37   38   38   38   39
   39   39   40   42   43   44   45   44   42
    85.0-180.0 180.0   5.0 450.0                            LAT/LON1/LON2/DLON/H
   51   52   50   49   47   46   46   45   45   43   42   41   39   39   39   35
   35   35   33   33   33   31   30   29   30   31   30   29   30   30   32   34
   32   32   31   31   29   30   29   30   30   29   29   28   28   27   27   27
   28   28   27   28   30   33   33   31   30   31   34   36   37   37   37   39
   39   39   39   40   43   45   44   44   42

   ....

   -87.5-180.0 180.0   5.0 450.0                            LAT/LON1/LON2/DLON/H
  128  130  132  133  126  123  120  133  144  140  143  149  153  142  140  140
  137  141  127  133  147  146  142  144  139  133  126  125  126  127  127  126
  128  128  126  132  134  132  124  125  135  143  143  132  127  132  145  140
  134  132  129  129  128  126  121  117  115  114  112  115  122  121  126  126
  124  126  128  128  127  126  128  129  129
     1                                                      END OF TEC MAP   
    """

    NO_VALUE = 999

    def __init__(self, 
                 lat_range: SpatialRange,
                 lon_range: SpatialRange,
                 height: float,
                 epoch: datetime
                 ):
        self.lat_range = lat_range
        self.lon_range = lon_range
        self.height = height
        self.data = defaultdict(list)
        self.epoch = epoch
    

    def set_data(self, data: list[GridCell]) -> None:
        """
        Sets data given as objects containing lat, lon, val and make map 
        out of it. There

        :param :
        """
        _data = defaultdict(list)
        for cell in data:
            _data[cell.lat].append((cell.lon, cell.val))

        lat_cells = ((self.lat_range.vmax - self.lat_range.vmin ) / 
                         self.lat_range.vstep + 1)
        if len(_data.keys()) != lat_cells:
            msg = "Some latitudes are missing {}".format(list(_data.keys()))
            raise ValueError(msg)

        for lat, lon_data in _data.items():
            lons = [lon for lon, _ in lon_data]
            lon_cells = ((self.lon_range.vmax - self.lon_range.vmin ) / 
                         self.lon_range.vstep + 1)
            if len(set(lons)) != lon_cells:
                raise LongitudeCellIsNotSet(lons, lat)
            if self.lon_range.vmin < self.lon_range.vmax:
                _data[lat].sort(key=lambda x: x[0], reverse=False)
            else:
                _data[lat].sort(key=lambda x: x[0], reverse=True)
            self.data[lat] = [val for _, val in _data[lat]]

            
    def get_cell(self, lat: float, lon: float) -> float:
        """
        Return a value on cell given by latitude and longitude.
        """
        lon_index = (lon - self.lon_range.vmin) / self.lon_range.vstep
        print(lon_index)
        return self.data[lat][int(round(lon_index, 0))]
