
from promium.base import Element


class Frame(Element):

    def switch_to_frame(self):
        self.driver.switch_to.frame(self.lookup())

    def exit_from_frame(self):
        self.driver.switch_to.window(self.driver.current_window_handle)
