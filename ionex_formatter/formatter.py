from datetime import datetime
from collections import defaultdict

from .spatial import SpatialRange
from .ionex_format import IonexHeader

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

class IonexFile:
    
    header_line_length = 60
    max_line_length = 80

    
    def __init__(self):
        self._raw_data = dict()
        self.header = defaultdict(list)
        self.header_format = IonexHeader()


    def unwrap_format_spec(self, format_spec):
        """
        Unwrap a format specification string to expand the repetition 
        count for 'F', 'I', and 'A' format specifiers.

        :param format_spec: The format specification string to unwrap.
        :type format_spec: str

        :return: The unwrapped format specification string.
        :rtype: str

        **Example**

        >>> format_spec = "2X, 3F6.1, I3, 10A2, 17X"
        >>> unwrapped_format = unwrap_format_speciefrs(format_spec)
        >>> print(unwrapped_format)
        "2X, F6.1, F6.1, F6.1, I3, A2, A2, A2, A2, A2, A2, A2, A2, A2, A2, 17X"
        """
        unwrapped_tokens = []
        if not format_spec:
            return ""
        tokens = format_spec.split(", ")
        
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

    def format_header_line(self, data, format_spec):
        pass        
    
    def set_description(self, description: str) -> None:
        """
        Sets description to be reflected in IONEX file header

        :param description: description to be stored under DESCRIPTION comment
            in IONEX file header

        :type description: string
        """
        self._raw_data["description"] = description
        _id = "DESCRIPTION"
        description = self._format_header_long_string(description, 
                                                      "DESCRIPTION")
        self.header[_id] = description
        
        
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

    def _format_header_long_string(self, info: str, string_id: str) -> str:
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

            