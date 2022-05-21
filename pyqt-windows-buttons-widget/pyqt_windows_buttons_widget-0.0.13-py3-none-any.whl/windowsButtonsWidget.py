from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget
from pyqt_titlebar_buttons_widget import TitlebarButtonsWidget


class WindowsButtonsWidget(TitlebarButtonsWidget):
    def __init__(self, base_widget: QWidget, hint: list = ['min', 'max', 'close']):
        super().__init__(base_widget, hint)
        self.__initUi()

    def __initUi(self):
        self._minimizeBtn.setText('🗕')
        self._maximizeBtn.setText('🗖')
        self._closeBtn.setText('🗙')

        # fill the button's background with color
        background_color = self._base_widget.palette().color(QPalette.Base).name()
        for btn in self._btn_dict.values():
            btn.setBackground(background_color)

        self.__styleInit()

    def __styleInit(self):
        close_button_style = self._closeBtn.styleSheet() + f'''
                             QPushButton:hover 
                             {{ 
                             background-color: #EE0000; 
                             color: #ffffff;
                             }}
                             QPushButton:pressed
                             {{
                             background-color: #CC0000;
                             }}
                             '''

        self._closeBtn.setStyleSheet(close_button_style)

    def event(self, e):
        if e.type() == 100:
            self.__styleInit()
        return super().event(e)