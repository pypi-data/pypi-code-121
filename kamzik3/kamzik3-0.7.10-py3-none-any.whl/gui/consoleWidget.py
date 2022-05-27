import sys
from collections import deque
from threading import Thread
from time import sleep

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QWidget

from kamzik3.gui.templates.consoleTemplate import Ui_Form
from kamzik3.snippets.snippetsYaml import YamlSerializable


class OutputStream(QObject):
    sig_write = pyqtSignal("QString")

    def write(self, message):
        self.sig_write.emit(message)


class ConsoleWidget(Ui_Form, QWidget, YamlSerializable):
    sig_stdout_write = pyqtSignal("QString")
    sig_stderr_write = pyqtSignal("QString")
    sig_flush_output = pyqtSignal()
    info_color = "blue"
    error_color = "red"
    warning_color = "orange"
    debug_color = "green"
    output_paused = False

    def __init__(self, title=None, config=None, parent=None):
        QWidget.__init__(self, parent)
        self.config = config
        if self.config is None:
            self.config = {}
        self.output_buffer = deque(maxlen=500)
        self.message_counter = 0
        self.error_counter = 0
        self.title = title
        self.previous_stdout = None
        self.previous_stderr = None
        if self.config.get("clone", True):
            self.previous_stdout = sys.stdout
            self.previous_stderr = sys.stderr
        sys.stdout = OutputStream()
        sys.stderr = OutputStream()

        self.sig_flush_output.connect(self.flush_output_buffer)
        sys.stdout.sig_write.connect(self.slot_write_stdout)
        sys.stderr.sig_write.connect(self.slot_write_stderr)
        self.setupUi(self)

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    @pyqtSlot("QString")
    def slot_write_stdout(self, text):
        if not self.output_paused:
            if text != "\n":
                text = "> " + text
                self.output_buffer.appendleft(self.format_html(text.strip()))
                self.message_counter += 1

        if self.previous_stdout is not None:
            self.previous_stdout.write(text)

    @pyqtSlot("QString")
    def slot_write_stderr(self, text):
        if not self.output_paused:
            if text != "\n":
                self.output_buffer.appendleft(self.format_html(text.strip()))
                self.message_counter += 1

        if self.previous_stderr is not None:
            self.previous_stderr.write(text)

    @pyqtSlot()
    def flush_output_buffer(self):
        if self.message_counter != self.input_messages_count.value():
            output = "".join(self.output_buffer)
            self.input_console_text.setHtml(output)
            self.input_messages_count.setValue(self.message_counter)
            self.input_errors_count.setValue(self.error_counter)

    @pyqtSlot()
    def scroll_down(self):
        vs = self.input_console_text.verticalScrollBar()
        vs.setValue(vs.maximum())

    @pyqtSlot()
    def scroll_up(self):
        vs = self.input_console_text.verticalScrollBar()
        vs.setValue(vs.minimum())

    @pyqtSlot()
    def clear_all(self):
        self.message_counter = 0
        self.error_counter = 0
        self.input_console_text.clear()
        self.input_messages_count.setValue(0)
        self.input_errors_count.setValue(0)

    @pyqtSlot()
    def pause_output(self):
        self.output_paused = True
        self.button_resume_output.setEnabled(True)
        self.button_pause_output.setEnabled(False)

    @pyqtSlot()
    def resume_output(self):
        self.output_paused = False
        self.button_resume_output.setEnabled(False)
        self.button_pause_output.setEnabled(True)

    def _move_cursor_to_end(self):
        tc = self.input_console_text.textCursor()
        tc.setPosition(self.input_console_text.document().characterCount() - 1)
        self.input_console_text.setTextCursor(tc)

    def _move_cursor_to_beginning(self):
        tc = self.input_console_text.textCursor()
        tc.setPosition(0)
        self.input_console_text.setTextCursor(tc)

    def format_html(self, text):
        if ", INFO," in text:
            text = "<span style='color:{}'>{}</span><br/>".format("blue", text)
        elif ", DEBUG," in text:
            text = "<span style='color:{}'>{}</span><br/>".format("green", text)
        elif ", WARNING," in text:
            text = "<span style='color:{}'>{}</span><br/>".format("orange", text)
        elif ", ERROR," in text:
            self.error_counter += 1
            text = "<span style='color:{}'>{}</span><br/>".format("red", text)
        else:
            text = "<span>{}</span>".format(text)
        return text

    # pylint: disable=unused-argument
    def showEvent(self, QShowEvent):
        def flush_output_thread():
            while self.isVisible():
                self.sig_flush_output.emit()
                sleep(2)

        Thread(target=flush_output_thread).start()
