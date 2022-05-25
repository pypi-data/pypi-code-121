class TabEater:
    def __init__(self):
        self.colnames=None

    def parse_line(self,line):
        # First line are column names
        if self.colnames==None:
            self.colnames=line.split()
            return None

        parts=[float(x) for x in line.split()]
        data=zip(self.colnames,parts)
        return dict(data)
