import pytest
from ionex_formatter.reader import convet_npz_to_internal
from ionex_formatter.formatter import IonexFile, IonexMapType

class TestIntegrationNPZ():
    
    def test_npz_integration(self, npz_file):
        npz_maps = convet_npz_to_internal(npz_file)
        assert len(npz_maps) == 1
        for map_type, maps in npz_maps.items():
            assert len(maps) == 24 
            formatter = IonexFile()
            formatter.set_maps(maps, dtype=map_type)
        file_lines = formatter.get_all_maps_lines(saved_types=[IonexMapType.TEC])
        assert len(file_lines) == 10296

