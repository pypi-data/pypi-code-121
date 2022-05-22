
import matplotlib.pyplot as plt

class PlotBase:
    """Basement class for plot classes"""
    def __init__(self,
        figsize: tuple[float, float] = (6,4),
        dpi: int = 150,
        layout: str = 'tight',
        show: bool =True,
        **kwagrs):
        
        self.fig = plt.figure(figsize=figsize, dpi=dpi, layout=layout, **kwagrs)
        self.show = show
        self.axes = None

    def __enter__(self):
        return(self)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        plt.show() if self.show else None