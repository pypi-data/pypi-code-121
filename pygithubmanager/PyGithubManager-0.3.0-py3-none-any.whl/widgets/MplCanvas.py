from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=4, dpi=100, xlabel='', ylabel='', title='', rotate_xlabel=False):
        """
        Initialize the canvas.

        Parameters
        ----------
        parent : QWidget
            The parent widget.
        width : int
            The width of the canvas.
        height : int
            The height of the canvas.
        dpi : int
            The resolution of the canvas.
        xlabel : str
            The label of the x-axis.
        ylabel : str
            The label of the y-axis.
        title : str
            The title of the canvas.
        rotate_xlabel : bool
            Whether to rotate the x-axis label.
        """
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        if rotate_xlabel:
            plt.xticks(rotation=90)
        super().__init__(fig)
        self.setParent(parent)
        self.ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
