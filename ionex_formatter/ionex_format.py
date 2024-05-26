from pathlib import Path
import json

class FormatDescriptionLabelMissing(Exception):
    """
    Raised when there no description for label listed in HEADER_FORMATS
    """
    pass

class IonexHeader_V_1_1:
    """
    Class is based on https://files.igs.org/pub/data/format/ionex1.pdf
    documetnt and contains all necessary header parts. HEADER LABEL in 
    the document serves as unique keys for dictionary that contain 
    FORMAT as a values. Class implements singleton pattern.
    
    Class provide HEADER_FORMATS and HEADER_DESCRIPTIONS for all fields
    HEADER_FORMATS is used to properly adjust data in every line of IONEX
    file. HEADER_DESCRIPTIONS can be used for reference is user have issue
    to define which data go which line of
    """

    HEADER_FORMATS = {
        "IONEX VERSION / TYPE": "F8.1, 12X, A1, 19X, A3, 17X",
        "PGM / RUN BY / DATE": "A20, A20, A20",
        "DESCRIPTION": "A60",
        "COMMENT": "A60",
        "EPOCH OF FIRST MAP": "6I6, 24X",
        "EPOCH OF LAST MAP": "6I6, 24X",
        "INTERVAL": "I6, 54X",
        "# OF MAPS IN FILE": "I6, 54X",
        "MAPPING FUNCTION": "2X, A4, 54X",
        "ELEVATION CUTOFF": "F8.1, 52X",
        "OBSERVABLES USED": "A60",
        "# OF STATIONS": "I6, 54X",
        "# OF SATELLITES": "I6, 54X",
        "SYS / # STA / # SAT": "5X, A1, I6, I6, 42X",
        "BASE RADIUS": "F8.1, 52X",
        "MAP DIMENSION": "I6, 54X",
        "HGT1 / HGT2 / DHGT": "2X, 3F6.1, 40X",
        "LAT1 / LAT2 / DLAT": "2X, 3F6.1, 40X",
        "LON1 / LON2 / DLON": "2X, 3F6.1, 40X",
        "EXPONENT": "I6, 54X",
        "START OF AUX DATA": "A60",
        "END OF AUX DATA": "A60",
        "START OF TEC MAP": "I6, 54X",
        "EPOCH OF CURRENT MAP": "6I6, 24X",
        "LAT/LON1/LON2/DLON/H": "2X, 5F6.1, 28X",
        "END OF TEC MAP": "I6, 54X",
        "START OF RMS MAP": "I6, 54X",
        "END OF RMS MAP": "I6, 54X",
        "START OF HEIGHT MAP": "I6, 54X",
        "END OF HEIGHT MAP": "I6, 54X",
        "END OF HEADER": "60X",
        "END OF FILE": "60X",
    }

    HEADER_DESCRIPTIONS = dict()

    AUTO_FORMATTED_LABELS = list()

    __instance = None

    def __new__(class_, *args, **kwargs):
        if class_.__instance is None:
            class_.__instance = object.__new__(class_, *args, **kwargs)
        class_.__instance.init_fields("ionex_formatter/header_line_descriptions.json")
        return class_.__instance

    def _update(self):
        self.init_fields("ionex_formatter/header_line_descriptions.json")

    def init_fields(self, description_path: str | Path) -> None:
        """
        Loads description and compares whether all labels contains necessary 
        description and formats

        :param description_path: path to json file with descriptions
        :type description_path: str or Path

        :raises: FormatDescriptionLabelMissing:
        """
        self.load_descriptions(description_path) 
        format_labels = list(self.HEADER_FORMATS.keys())
        description_labels = list(self.HEADER_DESCRIPTIONS.keys())
        format_labels.sort()
        description_labels.sort()
        if format_labels != description_labels:
            raise FormatDescriptionLabelMissing
        self.make_automatic_label_format_list()

    def make_automatic_label_format_list(self):
        self.AUTO_FORMATTED_LABELS = list()
        for label, format in self.HEADER_FORMATS.items():
            format_tokens = format.split(', ')
            label_tokens = label.split('/')
            label_tokens = [token.strip() for token in label_tokens]
            format_tokens_number = 0
            for token in format_tokens:
                if 'X' in token:
                    continue
                if len(token) > 2 and token[0].isnumeric() and token[1].isalpha():
                    format_tokens_number += int(token[0])
                    continue
                if token[-1] == 'A' or token[0].isalpha():
                    format_tokens_number += 1
                    continue
                # raise ValueError('Unknown format token {}'.format(token))
            if len(label_tokens) == format_tokens_number:
                self.AUTO_FORMATTED_LABELS.append(label)
        self.AUTO_FORMATTED_LABELS.sort()

    def load_descriptions(self, file_path: str | Path) -> None:
        """
        Loads description from file_path

        :param description_path: path to json file with descriptions
        :type description_path: str or Path

        :raises: IonexHeaderDescriptionFileMissing
        :raises: TypeError
        """
        descriptions_file = Path(file_path)
        if not descriptions_file.exists():  
            raise FileNotFoundError(str(file_path))
        with open(descriptions_file) as f:
            self.HEADER_DESCRIPTIONS = json.load(f)
        if not isinstance(self.HEADER_DESCRIPTIONS, dict):
            msg = "Descriptions in {} must be dict".format(file_path)
            raise TypeError(msg)
        for key, val in self.HEADER_DESCRIPTIONS.items():
            if not(isinstance(key, str) and isinstance(val, str)):
                key_type = type(key)
                val_type = type(val)
                msg = "Values and keys should be string."
                msg = msg + "For pair {} and  {} types are {} and  {}"
                msg = msg.format(key, val, key_type, val_type)
                raise TypeError(msg)
                
    def line_tokens(self, label):
        format_tokens = self.HEADER_FORMATS[label].split(', ')
        label_tokens = label.split(' / ')
        for token in format_tokens:
            if 'X' in token:
                continue

class IonexHeader(IonexHeader_V_1_1):
    pass