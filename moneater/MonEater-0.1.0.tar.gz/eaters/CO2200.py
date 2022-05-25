import re

class CO2200:
    """ CO2-200 from amprobe """

    def __init__(self):
        self.re_format=re.compile('C([0-9]+)ppm:T(-?[0-9]+\.[0-9]+)C:H([0-9]+\.[0-9]+)%:d(-?[0-9]+\.[0-9]+)C:w(-?[0-9]+\.[0-9]+)C')

    def parse_line(self,line):
        # Check if line matches pattern
        parts=self.re_format.search(line)
        if parts==None:
            return None

        # Get point
        return {
            'CO2': float(parts[1]),
            'Temperature': float(parts[2]),
            'Humidity': float(parts[3]),
            'DewPoint': float(parts[4]),
            'WetBulbTemperature': float(parts[5]),
        }
