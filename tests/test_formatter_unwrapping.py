import pytest
from ionex_formatter.formatter import (
    HeaderDuplicatedLine,
    IonexFile,
    NumericTokenTooBig,
    UnknownFormatSpecifier,
    UnknownFormatingError
)

class TestFormatterUnwrappingFields():

    @pytest.fixture
    def header_formatter(self):
        return IonexFile()

    def test_unwrap_format_spec_with_repeat(self, header_formatter):
        format_spec = "2X, 3F6.1, I3, 10A2, 17X"
        unwrapped_format = header_formatter.unwrap_format_spec(format_spec)
        expected = "2X, F6.1, F6.1, F6.1, I3, A2, A2, A2, A2, A2, A2," \
            " A2, A2, A2, A2, 17X"
        assert unwrapped_format == expected

    def test_unwrap_format_spec_no_repeat(self, header_formatter):
        format_spec = "2X, F6.1, I3, A2, 17X"
        unwrapped_format = header_formatter.unwrap_format_spec(format_spec)
        assert unwrapped_format == format_spec

    def test_unwrap_format_spec_empty_input(self, header_formatter):
        format_spec = ""
        unwrapped_format = header_formatter.unwrap_format_spec(format_spec)
        assert unwrapped_format == format_spec

    def test_unwrap_format_spec_only_repeats(self, header_formatter):
        format_spec = "3F6.1, 2I3, 4A2"
        unwrapped_format = header_formatter.unwrap_format_spec(format_spec)
        expected = "F6.1, F6.1, F6.1, I3, I3, A2, A2, A2, A2"
        assert unwrapped_format == expected

    def test_unwrap_format_spec_mixed_repeats(self, header_formatter):
        format_spec = "2X, 2F6.1, I3, A2, 17X, F5.2, 3A3"
        unwrapped_format = header_formatter.unwrap_format_spec(format_spec)
        expected = "2X, F6.1, F6.1, I3, A2, 17X, F5.2, A3, A3, A3"
        assert unwrapped_format == expected

    def test_unwrap_format_spec_single_repeats(self, header_formatter):
        format_spec = "F6.1, I3, A2"
        unwrapped_format = header_formatter.unwrap_format_spec(format_spec)
        assert unwrapped_format == format_spec

    
    def test_unwrap_format_spec_single_token(self, header_formatter):
        format_spec = "A60"
        unwrapped_format = header_formatter.unwrap_format_spec(format_spec)
        assert unwrapped_format == format_spec

    def test_unwrap_format_spec_too_many_repeats(self, header_formatter):
        format_spec = "3F6.1, 100I3, 10A2"
        with pytest.raises(UnknownFormatSpecifier):
            _ = header_formatter.unwrap_format_spec(format_spec)
    
    def test_1(self):
        ionfile = IonexFile()
        ionfile.add_comment('lolol')
    
    def test_2(self):
        with pytest.raises(UnknownFormatSpecifier):
            ionfile = IonexFile()
            ionfile.format_header_line([1, 2, 3, 5], "F6.1, L6.1, F6.1, F6.1")

    def test_3(self):
        with pytest.raises(UnknownFormatSpecifier):
            ionfile = IonexFile()
            ionfile._verify_formatted([1, 2, 3, 5], 'lolo', 'lol', 4, 3)
    
    def test_4(self):
        with pytest.raises(UnknownFormatingError):
            ionfile = IonexFile()
            ionfile._verify_formatted(2.0, "F", "3", 4, 3)
    
    def test_5(self):
        ionfile = IonexFile()
        ionfile._get_header_numeric_token(2.13, 6, 10)

    def test_6(self):
        with pytest.raises(NumericTokenTooBig):
            ionfile = IonexFile()
            ionfile._get_header_numeric_token(2.13, 2, 10)
            