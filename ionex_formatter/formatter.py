from datetime import datetime

class IonexFile:
    
    header_line_length = 60
    max_line_length = 80

    
    def __init__(self):
        self._raw_description = ""
        self.description = ""
        self._raw_start_time = ""
        self._raw_last_time = ""
        self.start_time = ""
        self.last_time = ""

    
    def set_description(self, description: str) -> None:
        """
        Sets description to be reflected in IONEX file header

        :param description: description to be stored under DESCRIPTION comment
            in IONEX file header

        :type description: string
        """
        self._raw_description = self.description
        self.description = self._format_header_long_string(description, 
                                                           "DESCRIPTION")
        
    def set_epoch_range(self, start: datetime, last: datetime) -> None:
        """
        Sets range of epoch that correspond to first and last map in file.
        :param start: time of the first map in IONEX file
        :type start: datetime.datetime
        
        :param last: time of the last map in IONEX file
        :type last: datetime.datetime
        """
        self._raw_start_time = start
        self._raw_last_time = last
        self.start_time = self._header_date_time(start) + "EPOCH OF FIRST MAP"
        self.last_time = self._header_date_time(last) + "EPOCH OF LAST MAP"
        self.start_time = self.start_time.ljust(self.max_line_length) + "\n"
        self.last_time = self.last_time.ljust(self.max_line_length) + "\n"
        
    def _header_date_time(self, epoch: datetime) -> str:
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

    def _format_header_long_string(self, info: str, comment: str) -> str:
        """
        Formats long string to fit IONEX file header
        
        :param info: information to be stored in IONEX header for example 
            description or station list
        :type description: string
        """
        words = info.split()
        if len(words) == 0:
            return ""
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
            current_line = current_line + comment
            current_line = current_line.ljust(self.max_line_length)
            lines[i] = current_line
        
        result = '\n'.join(lines)
        return result + '\n'

            