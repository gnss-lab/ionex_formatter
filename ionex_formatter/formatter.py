from datetime import datetime
from collections import defaultdict
from typing import Any
from enum import Enum

from .spatial import SpatialRange
from .ionex_format import IonexHeader
from .ionex_map import IonexMap

class UnknownFormatingError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class UnknownLabelError(Exception):
    def __init__(self, label):
        msg = "Label '{}' is not specified in ionex format".format(label)
        super().__init__(msg)

class UnknownFormatSpecifier(Exception):
    """
    Raised when there unknow specifier in format. 

    Valid specifiers are [n]Im, [n]Fm.k, Am, mX, where  n, m , k are integers and
    n could appear or could not appear: 6I3 and I3 are both valid.
    """
    def __init__(self, specifier: str):
        msg = "There is no processing for {}".format(specifier)
        super().__init__(msg)


class HeaderDuplicatedLine(Exception):
    """
    Raised when try to set header line while it already has values
    """
    pass

class NumericTokenTooBig(Exception):
    """
    Raised when the number when converted to string does not fit 
    specified width.
    
    For example:
    
        number 123.456 when is fitted in to width 6 with 3 decimal digit, 
        while it can fitt with 1 decimal digit (123.4)
        
        
    """
    def __init__(self, val: float, widht: int, decimal: int):
        msg = "Value {} with {} decimal digit does not fit {} widht"
        msg.format(val, decimal, widht)
        super().__init__(msg)

class IonexMapType(Enum):
    TEC = 1
    RMS = 2
    HGT = 3


class IonexFile:
    
    header_line_length = 60
    max_line_length = 80
    VALUES_PER_LINE = 16

    
    def __init__(self):
        self._raw_data = dict()
        self.header = defaultdict(list)
        self.header_format = IonexHeader()
        self.maps = defaultdict(dict)
        self.set_header_order()

    def set_maps(self, maps: dict[list], dtype: IonexMapType):
        """
        Set maps to formatter.

        Maps are given as dictionary using epoch as map time (epoch). 
        For given time there could be several maps for different time 
        (in general there is one map)

        :param order: list of label in order
        :type order: list

        :param dtype: type of data stored in map
        :type dtype: IonexMapType
        """
        self.maps[dtype] = maps

    def get_map_lines(self, dtype: IonexMapType, epoch: datetime) -> list[str]:
        """
        Make formatted output for map.

        :param dtype: type of map to be formatted
        :type dtype: IonexMapType

        :param epoch: time (epoch) of map to be formatted
        :type epoch: datetime

        """
        lines = list()
        maps: dict = self.maps[dtype]
        epoch_map: IonexMap = maps[epoch]
        epochs = list(maps.keys())
        epochs.sort()
        map_index = epochs.index(epoch) + 1

        # add START OF TEC MAP line
        label = "START OF TEC MAP"
        line_format = self.header_format.HEADER_FORMATS[label]
        line  = self.format_header_line([map_index], line_format)
        lines.append((line+label).ljust(self.max_line_length))

        # add time specifier for a map
        label = "EPOCH OF CURRENT MAP"
        line = self._get_header_date_time(epoch)
        lines.append((line+label).ljust(self.max_line_length))
        
        # add values for same latitude
        for lat, lon_data in epoch_map.data.items():
            # add grid specifier
            label = "LAT/LON1/LON2/DLON/H"
            line_format = self.header_format.HEADER_FORMATS[label]
            grid_data =[
                lat, 
                epoch_map.lon_range.vmin, 
                epoch_map.lon_range.vmax, 
                epoch_map.lon_range.vstep, 
                epoch_map.height
            ]
            line = self.format_header_line(grid_data, line_format)
            lines.append((line+label).ljust(self.max_line_length))

            # add map data
            chunks = epoch_map.lon_range.get_chunks(self.VALUES_PER_LINE)
            for start, end in chunks:
                fmt = "{}I5".format(end - start)
                line = self.format_header_line(lon_data[start: end], fmt)
                lines.append(line.ljust(self.max_line_length))

        # add end of map
        label = "END OF TEC MAP"
        line_format = self.header_format.HEADER_FORMATS[label]
        line  = self.format_header_line([map_index], line_format)
        lines.append((line+label).ljust(self.max_line_length))
        return lines

    def set_header_order(self, order: list=[]):
        """
        Set new order of lines to be listed in header

        :param order: list of label in order
        :type order: list

        :raises ValueError: when first (IONEX VERSION / TYPE) and 
            last (END OF HEADER) lines are not correct
        """
        self.line_order=[
            "IONEX VERSION / TYPE",
            "PGM / RUN BY / DATE",
            "DESCRIPTION",
            "COMMENT",
            "EPOCH OF FIRST MAP",
            "EPOCH OF LAST MAP",
            "INTERVAL"
            "# OF MAPS IN FILE",
            "MAPPING FUNCTION",
            "ELEVATION CUTOFF",
            "# OF STATIONS",
            "# OF SATELLITES",
            "OBSERVABLES USED",
            "BASE RADIUS",
            "MAP DIMENSION",
            "HGT1 / HGT2 / DHGT",
            "LAT1 / LAT2 / DLAT",
            "LON1 / LON2 / DLON",
            "EXPONENT",
            "START OF AUX DATA",
            "END OF AUX DATA",
            "END OF HEADER"
        ]
        if order:
            if order[0] != "IONEX VERSION / TYPE":
                msg = "First record in file should be 'IONEX VERSION / TYPE'"
                raise ValueError(msg)
            elif order[-1] != "END OF HEADER":
                msg = "Last record in header should be 'END OF HEADER'"
                raise ValueError(msg)
            for label in order:
                if label not in self.header_format.HEADER_FORMATS:
                    raise UnknownLabelError(label)

            self.line_order=order


    def set_version_type_gnss(self, 
                              version: float=1.0, 
                              map_type:str="I", 
                              gnss_type: str="GPS"):
        label = "IONEX VERSION / TYPE"
        data = [version, map_type, gnss_type]
        self.update_label(label, data)

    def set_sites(self, sites: list[str]) -> None:
        """
        Sets station used to create maps in IONEX file

        :param sites: list of 4-symbol station names
        :type sites: list[str]
        """
        self._raw_data["sites"] = sites
        label = "COMMENT"
        sites_lines = self._format_header_long_string(" ".join(sites), 
                                                      label)
        self.header[label].extend(sites_lines)

    def add_comment(self, comment: str | list) -> None:
        """
        Adds comments to be reflected in IONEX file header.

        :param comment: description to be stored under COMMENT label
            in IONEX file header
        :type description: string or list
        """
        self._raw_data["comment"] = comment
        label = "COMMENT"
        header_lines = []
        if isinstance(comment, str):
            header_lines = self._format_header_long_string(comment, label)
        else:
            for line in comment:
                _line = line.ljust(self.header_line_length) + label
                header_lines.append(_line.ljust(self.max_line_length))
        self.header[label].extend(header_lines)

    def update_label(self, label: str, data: list) -> None:
        """
        Wrapper over format_header_line using line label instead of
        line format.
        """
        line_format = self.header_format.HEADER_FORMATS[label]
        formatted  = self.format_header_line(data, line_format)
        line = formatted + label
        self.header[label].append(line.ljust(self.max_line_length))


    def format_header_line(self, data: list, format_string: str) -> str:
        """
        Format a line of header data according to the given format specification.

        :param list data: A list of data elements to be formatted.
        :type data: list

        :param format_spec: A list of format specifications for each data element.
            Supported format specifiers: 'F' (float), 'I' (integer), 'A' (string),
            and 'X' (whitespace). The format specifiers are followed by the field width.
        :type format_string: str

        :return: The formatted line of header data.
        :rtype: str

        **Example**

        >>> data = [1, 'I', 'BEN', 5]
        >>> format_spec = ['F8.1', '12X', 'A1', '19X', 'A3', '16X', 'I1']
        >>> formatted_header_line = format_line(data, format_spec)
        >>> print(formatted_header_line)
             1.0            I                   BEN                5
        """
        formatted_line = ""
        format_string = self.unwrap_format_spec(format_string)
        tokens = format_string.split(', ')
        val_tokens = [f for f in tokens if not 'X' in f]

        if len(val_tokens) != len(data):
            msg = "Data length {} doesn't correspond to length of " \
                "format tokens {}. See data {} and format {}"
            msg = msg.format(len(data), len(val_tokens), data, format_string)
            raise ValueError(msg)
        i  = 0
        for token in tokens:
            formatted_data = ""
            width = 0
            precision = 0
            if token[0] == 'F':
                width, precision = map(int, token[1:].split('.'))
                formatted_data = f"{float(data[i]):.{precision}f}"
            elif token[0] == 'I':
                width = int(token[1:])
                formatted_data = str(data[i])
            elif token[0] == 'A':
                width = int(token[1:])
                formatted_data = data[i]
            elif token[-1] == 'X':
                width = int(token[:-1])
                formatted_data = "".rjust(width)
            # else:
                # raise UnknownFormatSpecifier(token)
            if token[-1] != 'X':
                self._verify_formatted(
                    data[i], token[0], formatted_data, width, precision
                )
                if token[0] == 'A':
                    formatted_data = formatted_data.ljust(width)
                else:
                    formatted_data = formatted_data.rjust(width)
                i += 1
            formatted_line += formatted_data
        
        return formatted_line

    def _verify_formatted(self, 
                          data: Any, 
                          fmt: str, 
                          formatted_data: str, 
                          width: int, 
                          precision: int):
        if len(formatted_data) > width:
            raise NumericTokenTooBig(data, width, precision)
        if fmt == "A":
            return True
        if fmt == "F":
            convert = float 
        elif fmt == "I":
            convert = int 
        else:
            raise UnknownFormatSpecifier(fmt)
        if convert(formatted_data) != convert(data):
            msg = "Formatted data '{}' does not match original data '{}'"
            msg = msg.format(formatted_data, data)
            raise UnknownFormatingError(msg)
        return True

    def unwrap_format_spec(self, format_string):
        """
        Unwrap a format specification string to expand the repetition 
        count for 'F', 'I', and 'A' format specifiers.

        :param format_string: The format specification string to unwrap.
        :type format_string: str

        :return: The unwrapped format specification string.
        :rtype: str

        **Example**

        >>> format_string = "2X, 3F6.1, I3, 10A2, 17X"
        >>> unwrapped_format = unwrap_format_spec(format_spec)
        >>> print(unwrapped_format)
        "2X, F6.1, F6.1, F6.1, I3, A2, A2, A2, A2, A2, A2, A2, A2, A2, A2, 17X"
        """
        unwrapped_tokens = []
        if not format_string:
            return ""
        tokens = format_string.split(", ")
        
        for token in tokens:
            if "X" in token:
                unwrapped_tokens.append(token)
            elif token[0] in ("F", "I", "A"):
                unwrapped_tokens.append(token)
            elif token[1] in ("F", "I", "A") or token[2] in ("F", "I", "A"):
                if token[1] in ("F", "I", "A"):
                    type_position = 1  
                else:
                    type_position = 2
                type_spec = token[type_position]
                count, specifier = token.split(type_spec)
                unwrapped_token = "{}{}".format(type_spec, specifier)
                for _ in range(int(count)):
                    unwrapped_tokens.append(unwrapped_token)
            else:
                raise UnknownFormatSpecifier(token)
        
        unwrapped_format = ", ".join(unwrapped_tokens)
        return unwrapped_format     
    
    def set_description(self, description: str | list) -> None:
        """
        Sets description to be reflected in IONEX file header

        :param description: description to be stored under DESCRIPTION label
            in IONEX file header

        :type description: string
        """
        self._raw_data["description"] = description
        label = "DESCRIPTION"
        header_lines = []
        if isinstance(description, str):
            header_lines = self._format_header_long_string(description, label)
        else:
            for line in description:
                _line = line.ljust(self.header_line_length) + label
                header_lines.append(_line.ljust(self.max_line_length))
        self.header[label] = header_lines 
        
        
    def set_epoch_range(self, start: datetime, last: datetime) -> None:
        """
        Sets range of epoch that correspond to first and last map in file.
        :param start: time of the first map in IONEX file
        :type start: datetime.datetime
        
        :param last: time of the last map in IONEX file
        :type last: datetime.datetime
        """
        self._raw_data["first_map_time"] = start
        self._raw_data["last_map_time"] = last
        ids = {"first_map_time": "EPOCH OF FIRST MAP",
               "last_map_time": "EPOCH OF LAST MAP"}
        times = {"first_map_time": start,
               "last_map_time": last}
        for time_type, time in times.items():
            _id = ids[time_type]
            line = self._get_header_date_time(time) + _id
            line = line.ljust(self.max_line_length)
            self.header[_id].append(line)

    def set_spatial_grid(self, 
                        lat_range: SpatialRange,
                        lon_range: SpatialRange,
                        height_range: SpatialRange) -> None:
        """
        Sets spatial range to be written to header.
        
        These include height, latitude and longitude: 
        
        450.0 450.0   0.0                   HGT1 / HGT2 / DHGT  
         87.5 -87.5  -2.5                   LAT1 / LAT2 / DLAT  
        -180.0 180.0   5.0                  LON1 / LON2 / DLON  
        
        Format for these lines is:  2X, 3F6.1, 40X 
       
        :param height_range: range and steps for height. Since the 
        :type height_range: SpatialRange
        
        :param lat_range: range and steps for latitude
        :type lat_range: SpatialRange
        
        :param lon_range: range and steps for longitude
        :type lon_range: SpatialRange
        """
        width = 6
        start_space = 2
        fin_space = 40
        ranges = {"lat": lat_range, 
                  "lon": lon_range, 
                  "height":height_range}
        ids = {"lat": "LAT1 / LAT2 / DLAT",
               "lon": "LON1 / LON2 / DLON",
                "height": "HGT1 / HGT2 / DHGT"}
        duplicates =[c for c in ids.values() if c in self.header]
        if duplicates:
            raise HeaderDuplicatedLine
        for rng_type, rng in ranges.items():
            rng.verify()
            mnt = self._get_header_numeric_token(rng.vmin, width, rng.decimal)
            mxt = self._get_header_numeric_token(rng.vmax, width, rng.decimal)
            stp = self._get_header_numeric_token(rng.vstep, width, rng.decimal)
            line = " " * start_space + mnt + mxt + stp + " " * fin_space
            _id = ids[rng_type]
            line = line + _id
            line = line.ljust(self.max_line_length)
            self.header[_id].append(line)
            
            
    def _get_header_numeric_token(self, 
                                  val: float, 
                                  width: int,
                                  decimal: int ) -> str:
        """
        Converts number to string given decimal digits and width.
        
        :param val: number to be converted
        :type val: float
        
        :param width: number of symbols occupied by token. If number is 
            shorter, then space are added to the left
        :type width: int
        
        :param decimal: number of decimal digits to be stored. If there is no
            enough decimal digit then zeros are added to the right
        :type decimal: int
        """
        token = str(round(float(val), decimal))
        point_pos = token.index(".")
        add_zeros = len(token) - (point_pos + decimal + 1)
        if add_zeros:
            token = token + "0" * add_zeros
        if len(token) > width:
            raise NumericTokenTooBig(val, width, decimal)
        token = token.rjust(width)
        return token
        
    def _get_header_date_time(self, epoch: datetime) -> str:
        """
        Converts datetime to string according to fit IONEX header.
        
        :param epoch: Epoch to be converted
        :type epoch: datetime.datetime
        
        :return: Formatted string that contains year, month, day, hour, minute
            and second. Each time field is five characters long and devided 
            by space
        :rtype: str
        """
        time_field_length = 5
        fields = [epoch.year, epoch.month, epoch.day, 
                  epoch.hour, epoch.minute, epoch.second]
        line = ""
        for field in fields:
            line = line + " " + str(field).rjust(time_field_length)
        line = line.ljust(self.header_line_length)
        return line

    def _format_header_long_string(self, info: str, string_id: str) -> list:
        """
        Formats long string to fit IONEX file header
        
        :param info: information to be stored in IONEX header for example 
            description or station list
        :type description: string
        """
        words = info.split()
        if len(words) == 0:
            return []
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word + " ") <= self.header_line_length:
                current_line = current_line + word + " "
            else:
                lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
            current_line = word + " "
            
        # add comment in the end of information and fotmat line to 80 symbols
        for i, line in enumerate(lines):
            current_line = line.ljust(self.header_line_length)
            current_line = current_line + string_id
            current_line = current_line.ljust(self.max_line_length)
            lines[i] = current_line
        
        return lines

            