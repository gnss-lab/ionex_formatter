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

