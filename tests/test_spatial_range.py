import pytest
from ionex_formatter.spatial import SpatialRange
from ionex_formatter.spatial import (NonIntegerStepCountError,
                                     FiniteRangeZeroStepError,
                                     DecimalDigitReduceAccuracyError)

class TestSpatialGridDimensions():
    
    def test_zero_step(self):
        rng = SpatialRange(450.0, 450.0, 0.0)
        assert rng.vmin == 450.0
        assert rng.vmax == 450.0
        assert rng.vstep == 0.0
        
    def test_non_zero_step(self):
        rng = SpatialRange(-180.0, 180, 5.0)
        assert rng.vmin == -180.0
        assert rng.vmax == 180.0
        assert rng.vstep == 5.0

    def test_number_of_nodes(self):
        rng = SpatialRange(-180.0, 180, 5.0)
        assert rng.get_node_number() == 73

        rng = SpatialRange(450.0, 450, 0.0)
        assert rng.get_node_number() == 1

    def test_chunks_non_zero_step(self):
        rng = SpatialRange(-180.0, 180, 5.0)
        chunks = rng.get_chunks(15)
        expected = [
            (0, 15), 
            (15, 30), 
            (30, 45), 
            (45, 60),
            (60, 73)
        ]
        assert chunks == expected

        chunks = rng.get_chunks(45)
        expected = [
            (0, 45), 
            (45, 73)
        ]
        assert chunks == expected

        chunks = rng.get_chunks(100)
        expected = [(0, 73)]
        assert chunks == expected

        chunks = rng.get_chunks(73)
        expected = [(0, 73)]
        assert chunks == expected

        chunks = rng.get_chunks(0)
        expected = [(0, 73)]
        assert chunks == expected

        chunks = rng.get_chunks(-1)
        expected = [(0, 73)]
        assert chunks == expected

    def test_chunks_zero_step(self):
        rng = SpatialRange(450.0, 450, 0.0)
        chunks = rng.get_chunks(100)
        expected = [(0, 1)]
        assert chunks == expected

        chunks = rng.get_chunks(0)
        assert chunks == expected

        
    def test_finate_range_zero_step_raises(self):
        with pytest.raises(FiniteRangeZeroStepError):
            SpatialRange(400.0, 450.0, 0.0)
            
    def test_non_integer_step_count_raises(self):
        with pytest.raises(NonIntegerStepCountError):
            SpatialRange(400.0, 450.0, 9.0)

    def test_step_decimal_reduce_accuracy_raises(self):
        with pytest.raises(DecimalDigitReduceAccuracyError):
            SpatialRange(0.0, 1.0, 0.125, decimal=2)
            
    def test_max_decimal_reduce_accuracy_raises(self):
        with pytest.raises(DecimalDigitReduceAccuracyError):
            SpatialRange(0.0, 1.125, 0.125, decimal=2)

    def test_min_decimal_reduce_accuracy_raises(self):
        with pytest.raises(DecimalDigitReduceAccuracyError):
            SpatialRange(0.125, 1.0, 0.125, decimal=2)
    
    def test_round_min(self):
        with pytest.raises(DecimalDigitReduceAccuracyError):
            SpatialRange(0.125, 1.0, 0.3, decimal=1)

    def test_round_max(self):
        with pytest.raises(DecimalDigitReduceAccuracyError):
            SpatialRange(1, 1.456, 0.9, decimal=1)

    def test_get_chunks_with_negative_start(self):
        rng = SpatialRange(0, 10, 1)
        chunks = rng.get_chunks(-1)
        expected = [(0, rng.get_node_number())]
        assert chunks == expected
