import pytest
import json

from ionex_formatter.ionex_format import (
    IonexHeader_V_1_1,
    FormatDescriptionLabelMissing
)

class TestIoneHeaderFormat:

    def test_init(self):
        IonexHeader_V_1_1()

    def test_label_description_is_missing(self, tmp_path):
        with open("ionex_formatter/header_line_descriptions.json", "r") as f:
            corrupted_descrition = json.load(f)
        del corrupted_descrition["COMMENT"]
        corrupted_descrition_path = tmp_path / "corrupted_descriptions.json"
        with open(corrupted_descrition_path, "w") as f:
            corrupted_descrition = json.dump(corrupted_descrition, f)
        header = IonexHeader_V_1_1()
        with pytest.raises(FormatDescriptionLabelMissing):
            header.init_fields(corrupted_descrition_path)

    def test_label_worng_value_type(self, tmp_path):
        with open("ionex_formatter/header_line_descriptions.json", "r") as f:
            corrupted_descrition = json.load(f)
        corrupted_descrition["COMMENT"] = 123
        corrupted_descrition_path = tmp_path / "corrupted_descriptions.json"
        with open(corrupted_descrition_path, "w") as f:
            corrupted_descrition = json.dump(corrupted_descrition, f)
        header = IonexHeader_V_1_1()
        with pytest.raises(TypeError):
            header.load_descriptions(corrupted_descrition_path)