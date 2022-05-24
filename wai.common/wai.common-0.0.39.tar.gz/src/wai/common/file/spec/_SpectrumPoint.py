class SpectrumPoint:
    """
    Class representing a single data point in a spectrum.
    """
    def __init__(self, wave_number: float = -1.0, amplitude: float = -1.0):
        self.wave_number: float = wave_number
        self.amplitude: float = amplitude
