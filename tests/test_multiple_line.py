import pytest
from ionex_formatter import formatter

class TestMultipleLines:

    @pytest.fixture
    def header_formatter(self):
        return formatter.IonexFile()

    def test_empty_input(self, header_formatter):
        description = ""
        res = header_formatter._format_header_long_string(description, "ANY")
        assert type(res) == list
        assert len(res) == 0
        
    def test_spaces_input(self, header_formatter):
        description = "    "
        res = header_formatter._format_header_long_string(description, "ANY")
        assert type(res) == list
        assert len(res) == 0
        
    def test_one_line(self, header_formatter):
        description = "Map"
        res = header_formatter._format_header_long_string(description, "ANY")
        expected_output = ["Map" + " " * 57 + "ANY" + " " * 17]
        assert type(res) == list
        assert len(res) == 1
        assert res == expected_output
        
    def test_several_lines(self, header_formatter):
        description = "Global Ionospheric Maps (GIM) are generated on an " \
                      "hourly and daily basis at JPL using data from " \
                      "up to 100 GPS sites of the IGS and others institutions." 
        expected_output = ["Global Ionospheric Maps (GIM) are generated o" \
                          "n an hourly    ANY                 ",
                          "and daily basis at JPL using data from up to " \
                          "100 GPS sites  ANY                 ",
                          "of the IGS and others institutions.          " \
                          "               ANY                 "]
        res = header_formatter._format_header_long_string(description, "ANY")
        assert len(res) == len(expected_output)
        assert res == expected_output

class TestDescriptionFormating:
    
    @pytest.fixture
    def header_formatter(self):
        return formatter.IonexFile()
    
    def test_several_lines(self, header_formatter):
        description = "Global Ionospheric Maps (GIM) are generated on an " \
                      "hourly and daily basis at JPL using data from " \
                      "up to 100 GPS sites of the IGS and others institutions." 
        expected_output = ["Global Ionospheric Maps (GIM) are generated o" \
                          "n an hourly    DESCRIPTION         ",
                          "and daily basis at JPL using data from up to " \
                          "100 GPS sites  DESCRIPTION         ",
                          "of the IGS and others institutions.          " \
                          "               DESCRIPTION         "]
        header_formatter.set_description(description)
        res = header_formatter.header["DESCRIPTION"]
        assert res == expected_output