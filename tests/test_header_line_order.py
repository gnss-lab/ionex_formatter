import pytest
from ionex_formatter.formatter import (
    IonexFile,
    UnknownLabelError
)

class TestFormatterUnwrappingFields():

    @pytest.fixture
    def header_formatter(self):
        return IonexFile()

    def test_default_order(self, header_formatter):
        header_formatter.set_header_order()
        assert header_formatter.line_order[0] == "IONEX VERSION / TYPE"
        assert header_formatter.line_order[-1] == "END OF HEADER"

    def test_missed_first_line(self, header_formatter):
        header_formatter.set_header_order()
        miss_first_line_order = header_formatter.line_order[1:]
        miss_last_line_order = header_formatter.line_order[:-1]
        with pytest.raises(ValueError):
            header_formatter.set_header_order(miss_first_line_order)
        with pytest.raises(ValueError):
            header_formatter.set_header_order(miss_last_line_order)        

    def test_unknown_label(self, header_formatter):
        header_formatter.set_header_order()
        line_order=[
            "IONEX VERSION / TYPE",
            "UNKNOWN",
            "END OF HEADER"
        ]
        with pytest.raises(UnknownLabelError):
            header_formatter.set_header_order(line_order)
    
    def test_set_header(self, header_formatter):
        line_order=[
            "IONEX VERSION / TYPE",
            "PGM / RUN BY / DATE",
            "DESCRIPTION",
            "MAP DIMENSION",
            "HGT1 / HGT2 / DHGT",
            "LAT1 / LAT2 / DLAT",
            "LON1 / LON2 / DLON",
            "END OF HEADER"
        ]
        header_formatter.set_header_order(line_order)
        assert header_formatter.line_order == line_order