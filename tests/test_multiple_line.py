import pytest
from ionex_formatter import formatter

class TestMultipleLines:

    @pytest.fixture
    def header_formatter(self):
        return formatter.IonexFile()

    def test_empty_input(self, header_formatter):
        description = ""
        res = header_formatter._format_header_long_string(description, "ANY")
        assert res == ""
        
    def test_spaces_input(self, header_formatter):
        description = "    "
        res = header_formatter._format_header_long_string(description, "ANY")
        assert res == ""
        
    def test_one_line(self, header_formatter):
        description = "Map"
        res = header_formatter._format_header_long_string(description, "ANY")
        expected_output = "Map" + " " * 57 + "ANY" + " " * 17 + "\n"
        assert res == expected_output
        
    def test_several_lines(self, header_formatter):
        description = "Global Ionospheric Maps (GIM) are generated on an " \
                      "hourly and daily basis at JPL using data from " \
                      "up to 100 GPS sites of the IGS and others institutions." 
        expected_output = "Global Ionospheric Maps (GIM) are generated o" \
                          "n an hourly    ANY                 \n" \
                          "and daily basis at JPL using data from up to " \
                          "100 GPS sites  ANY                 \n" \
                          "of the IGS and others institutions.          " \
                          "               ANY                 \n"
        res = header_formatter._format_header_long_string(description, "ANY")
        assert res == expected_output

class TestDescriptionFormating:
    
    @pytest.fixture
    def header_formatter(self):
        return formatter.IonexFile()
    
    def test_several_lines(self, header_formatter):
        description = "Global Ionospheric Maps (GIM) are generated on an " \
                      "hourly and daily basis at JPL using data from " \
                      "up to 100 GPS sites of the IGS and others institutions." 
        expected_output = "Global Ionospheric Maps (GIM) are generated o" \
                          "n an hourly    DESCRIPTION         \n" \
                          "and daily basis at JPL using data from up to " \
                          "100 GPS sites  DESCRIPTION         \n" \
                          "of the IGS and others institutions.          " \
                          "               DESCRIPTION         \n"
        header_formatter.set_description(description)
        res = header_formatter.description
        assert res == expected_output