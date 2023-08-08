class NonIntegerStepCountError(Exception):
    """
    Raised when there is non integer step count in range.

    For example step 3 for range [0, 10].
    """
    def __init__(self, count: float, int_count: int):
        msg = "Count {} is not integer {}".format(count, int_count)
        super().__init__(msg)

class FiniteRangeZeroStepError(Exception):
    """
    Raised when the step is zero however the max-min != 0
    """
    
class DecimalDigitReduceAccuracyError(Exception):
    """
    Raised when the decimal digits declared to be stored in ionex
    reduces the accuracy of given value.
    
    For example:
    
    Step = 0.25 and decimal is set to 1, then ionex should store only 0.2
    for step
    """
    def __init__(self, 
                 key: str, 
                 value: float, 
                 rounded_value: float,
                 decimal: int):
        msg = "Value for {} is {} couldn't stored with ".format(key, value)
        msg = msg + "{} decimal digits, without accuracy loss".format(decimal)
        msg = msg + " resulting in {} when rounded".format(rounded_value)
        super().__init__(msg)

class SpatialRange():
    
    """
    Container for min, max and step storage.
    """
    
    def __init__(self, vmin: float, vmax: float, vstep: float, decimal: int=1):
        """
        Initialize and verify data.
        
        :param vmin: range minimum
        :type vmin: float
        
        :param vmax: range maximum
        :type vmax: float
        
        :param vstep: step to go from min to max including edges.
        :type vstep: float
        
        :param decimal: number of decimal digits to be stored in IONEX
        :type decimal: int
        """
        self.vmin = vmin
        self.vmax = vmax
        self.vstep = vstep
        self.decimal = decimal
        self.verify()
        
    def verify(self) -> None:
        """
        Verifies data passed to constructor.
        
        There are following tests:

        :raises FiniteRangeZeroStepError: is there integer number of steps 
            in given range
            
        :raises FiniteRangeZeroStepError: is there zero step with with finite 
            range
            
        :raises DecimalDigitReduceAccuracyError: is there accuracy loss when 
            writing to file
        
        """
        round_step = round(self.vstep, self.decimal)
        if round_step != self.vstep:
            raise DecimalDigitReduceAccuracyError("Range step", 
                                                  self.vstep,
                                                  round_step,
                                                  self.decimal)
        round_min = round(self.vmin, self.decimal)
        if round_min != self.vmin:
            raise DecimalDigitReduceAccuracyError("Range maximum", 
                                                  self.vmax,
                                                  round_min,
                                                  self.decimal)
        round_max = round(self.vmax, self.decimal)
        if round_max != self.vmax:
            raise DecimalDigitReduceAccuracyError("Range minimum", 
                                                  round_max,
                                                  self.vmin, 
                                                  self.decimal)

        if self.vstep != 0:
            count = (self.vmax - self.vmin) / self.vstep 
            if count != int(count):
                raise NonIntegerStepCountError(count, int(count))
        if self.vstep == 0 and self.vmax != self.vmin:
            raise FiniteRangeZeroStepError
    

