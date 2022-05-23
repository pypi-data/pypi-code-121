from PySide6.QtCore import QObject, Signal


class MainWinSignal(QObject):
    """
    主窗口 自定义信号
    """

    setOutPutBox = Signal(str)
    clearOutPutBox = Signal()
    appendOutPutBox = Signal(str)
    getOutPutBox = Signal()

    setStartButtonText = Signal(str)
    setStartButtonState = Signal(bool)

    setOutPutBoxCursor = Signal(str)


main_win_signal = MainWinSignal()
