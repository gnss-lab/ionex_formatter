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
    
    def get_node_number(self) -> int:
        """
        Rerturn a number of nodes in range including both limits
        """
        if self.vstep == 0:
            return 1
        else:
            return int(round((self.vmax - self.vmin) / self.vstep, 0)) + 1

    def get_chunks(self, chunk_size: int) -> list:
        """
        Return ranges for chunks given chunk_size.

        :param chunk_size: number of element for a chunk

        :returns: list of (start, stop) for chunk        
        :rtype: list
        """
        num = self.get_node_number()
        if chunk_size <= 0:
            return [(0, num)]
        start_end = [(s, s + chunk_size) for s in range(0, num, chunk_size)]
        very_last = start_end[-1][1]
        if very_last > num:
            start_end = start_end[:-1]
        # add last chunk that could be not full 
        if num % chunk_size != 0:
            start = (num // chunk_size) * chunk_size
            if start < 0:
                start_end = [(0, num)]
            else:
                start_end.append((start, num)) 
        return start_end