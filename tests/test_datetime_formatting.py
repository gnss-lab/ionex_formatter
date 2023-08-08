import pytest
from datetime import datetime
from ionex_formatter import formatter

class TestDatetimeFormatting:
    
    @pytest.fixture
    def header_formatter(self):
        return formatter.IonexFile()

    def test_datetime_to_header_line(self, header_formatter):
        test_date = datetime(2018, 12, 30)
        res = header_formatter._header_date_time(test_date)
        out ="  2018    12    30     0     0     0                        "
        assert res == out
        test_date = datetime(2018, 12, 1, 23, 45, 30)
        res = header_formatter._header_date_time(test_date)
        out ="  2018    12     1    23    45    30                        "
        assert res == out
        
    def test_datetime_line(self, header_formatter):
        start = datetime(2018, 12, 30)
        last = datetime(2018, 12, 31)
        header_formatter.set_epoch_range(start, last)
        epochs = header_formatter.start_time + header_formatter.last_time
        out = "  2018    12    30     0     0     0" \
              "                        EPOCH OF FIRST MAP  \n" \
              "  2018    12    31     0     0     0" \
              "                        EPOCH OF LAST MAP   \n"
        assert epochs == out

