class IonexFile:
    
    header_line_length = 60
    max_line_length = 80

    
    def __init__(self):
        self.description = ""
    
    def set_description(self, description):
        """
        Sets description to be reflected in IONEX file header
        
        :param description: description to be stored under DESCRIPTION comment
            in IONEX file header
            
        :type description: string
        """
        self.description = self._format_header_long_string(description, 
                                                           "DESCRIPTION")


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

            