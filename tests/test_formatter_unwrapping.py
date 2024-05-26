import pytest
from ionex_formatter.formatter import (
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

    def test_verify_formatted(self):
        with pytest.raises(UnknownFormatingError):
            test_ionex_file = IonexFile()
            test_ionex_file._verify_formatted(3.4, "F", "3.21", 4, 3)
        with pytest.raises(UnknownFormatSpecifier):
            test_ionex_file2 = IonexFile()
            test_ionex_file2._verify_formatted(3.4, "X", "2", 4, 3)
    
    def test_add_comment(self):
        test_ionex_file = IonexFile()
        test_ionex_file.add_comment("hi")

    def test_format_header_line(self):
        with pytest.raises(UnknownFormatSpecifier):
            test_ionex_file = IonexFile()
            test_ionex_file.format_header_line([1, 2, 3, 5], "F1.1, L2.1, F3.1, F5.1")

    def test_add_zeros(self):
        ionfile = IonexFile()
        ionfile._get_header_numeric_token(2.13, 6, 10)

    def test_token_too_big(self):
        with pytest.raises(NumericTokenTooBig):
            ionfile = IonexFile()
            ionfile._get_header_numeric_token(2.13, 2, 10)

    
    