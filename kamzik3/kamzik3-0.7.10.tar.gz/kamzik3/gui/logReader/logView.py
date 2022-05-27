import os
import re

from PyQt5.QtCore import Qt, pyqtSlot, QItemSelection, QItemSelectionModel, QDateTime
from PyQt5.QtWidgets import QWidget, QMdiSubWindow, QFileDialog
from pyqtgraph import exporters
from reportlab.platypus import SimpleDocTemplate, Image, LayoutError

import kamzik3
from kamzik3.constants import ATTR_CACHE_DIRECTORY
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.logReader.logPlotView import (
    LogPlotView,
    LogPlotViewMaster,
    QMdiSubWindowPlot,
)
from kamzik3.gui.logReader.logViewHeaderModel import (
    LogViewHeaderModel,
    LogHeaderSelectionModel,
)
from kamzik3.gui.templates.logViewTemplate import Ui_Form
from kamzik3.snippets.snippetsUnits import get_scaled_time_duration
from kamzik3.snippets.snippetsWidgets import show_error_message

# View modes constants declaration

MODE_LIST = 0
MODE_ZOOM = 1


class LogView(Ui_Form, DeviceWidget):
    """
    Log Viewer widget.

    Display plots in different modes.
    Use DeviceLogParser as a data source.
    """

    view_mode = MODE_LIST
    square_function_values = [x**2 for x in range(255)]
    pandas_dt = None
    master_window = None
    last_zoom_region = None
    view_tiled = True

    # Below are valid class attributes but mypy can't find them
    sub_windows_hint = (
        Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint  # type: ignore
    )
    master_window_hint = Qt.CustomizeWindowHint | Qt.WindowTitleHint  # type: ignore

    def setupUi(self, form):
        Ui_Form.setupUi(self, form)
        # Setup scrollbars width and height
        self.mdi_area.verticalScrollBar().setMaximumWidth(15)
        self.mdi_area.horizontalScrollBar().setMaximumHeight(15)
        # Connect activated sub-window to self.slot_window_activated method
        self.mdi_area.subWindowActivated.connect(self.slot_window_activated)

    def open(self, path, append=False, refresh=True, filter=None):
        """
        Open logfile.

        Should be replaced.

        :param path:
        :param append:
        :param refresh:
        :param filter:
        """
        try:
            self.logger.info(
                "Opening {}, append: {}, refresh: {}, filter: {}".format(
                    path, append, refresh, filter
                )
            )
            padas_dt = self.device.parse(path=path, format="mag_log", filter=filter)
            if append:
                self.pandas_dt = self.pandas_dt.append(padas_dt)
            else:
                self.pandas_dt = padas_dt
            if refresh:
                self.refresh()
        except Exception as e:
            error_message = (
                "Error parsing file {}, probably unsupported format. {}".format(path, e)
            )
            self.logger.error(error_message)
            show_error_message(error_message, self)
            return

    def refresh(self):
        self.slot_reset_all()
        filtered_columns = []
        for column, dtype in zip(self.pandas_dt.columns, self.pandas_dt.dtypes):
            if dtype == "bool":
                self.pandas_dt[column] = self.pandas_dt[column].astype(int, copy=False)
            if self.pandas_dt[column].isnull().all():
                # Ignore column if all values are NaN
                continue
            if dtype != "object":
                filtered_columns.append(column)
        model = LogViewHeaderModel(filtered_columns)
        self.input_header_items.setModel(model)
        max_selected_rows = self.input_max_selected_rows.value()
        selection_model = LogHeaderSelectionModel(
            model, max_selected_rows=max_selected_rows
        )
        self.input_header_items.setSelectionModel(selection_model)
        self.input_master_row.addItems(filtered_columns)

    def create_sub_window(self, id, master=False):
        """
        Create new sub-window with plot view widget.

        :param id: str
        :param master: bool
        :return:
        """
        window = QMdiSubWindowPlot(id)
        window.setWindowIcon(self.windowIcon())
        win_title, unit = id.split(" (")
        unit = unit[:-1]
        if not master:
            widget = LogPlotView(unit=unit, bottom_label=None)
            window.setWindowFlags(self.sub_windows_hint)
            window.closeEvent = lambda event, w=window: self.sub_window_closed(event, w)
            window.setMinimumSize = lambda w=window: self.set_master(w)
        else:
            widget = LogPlotViewMaster(unit=unit, bottom_label=None, color=(0, 0, 0))
            window.setWindowFlags(self.master_window_hint)
            self.master_window = window

            def region_chane_finished():
                self.master_zoom_changed(widget.lookingGlass.getRegion())

            widget.lookingGlass.sigRegionChangeFinished.connect(region_chane_finished)
            win_title = "{} - {}".format("Master", win_title)

        window.setWindowTitle(win_title)
        window.setWidget(widget)
        window.master = master
        real_values_at = self.pandas_dt[id].notna()
        y = self.pandas_dt[id][real_values_at].values
        x = self.pandas_dt["Timestamp (sec)"][real_values_at].values

        widget.slot_set_data(x=x, y=y)

        return window

    def tile_sub_windows(self):
        """
        Method to keep sub-windows tiled if input_keep_tiled checkbox is checked.

        Set tile mode based on self.view_mode variable.
        For some reason mdi area needs to be on top when reorganizing.
        That's why I'm scrolling to the top of the view first.
        """
        if self.input_keep_tiled.isChecked():
            # Get width and height of mdi area
            w, h = self.mdi_area.width(), self.mdi_area.height()
            # Get all sub-windows in mdi area
            windows_list = self.mdi_area.subWindowList()
            if len(windows_list) > 0:
                # Scroll to the top of mdi area
                self.mdi_area.verticalScrollBar().setValue(0)
                self.mdi_area.horizontalScrollBar().setValue(0)
                if self.view_mode == MODE_LIST:
                    # List mode tiling
                    plot_height = None
                    if not self.input_view_scale_plots.isChecked():
                        plot_height = h * (self.input_view_plot_height.value() / 100)
                    self.tile_list_windows(
                        list_windows=list(reversed(windows_list)),
                        plot_height=plot_height,
                    )
                elif self.view_mode == MODE_ZOOM:
                    # Zoom mode tiling
                    master_height = h / 3.8
                    master_window = self.master_window
                    windows_list.remove(master_window)
                    master_window.setGeometry(0, h - master_height, w, master_height)
                    self.tile_slave_windows(
                        slave_windows=windows_list, h=h - master_height
                    )

    def sub_window_closed(self, event, window):
        """
        Sub Window closing event.

        Closed window needs to be removed from mdi area and selected rows as well.

        :param event:
        :param window:
        """
        window.setParent(None)
        selection_model = self.input_header_items.selectionModel()
        model = self.input_header_items.model()
        row = model.model_data.index(window.id)
        deselection = QItemSelection(
            model.createIndex(row, row), model.createIndex(row, row)
        )
        selection_model.select(
            deselection, QItemSelectionModel.Deselect | QItemSelectionModel.Rows
        )
        if self.view_tiled:
            self.slot_selection_changed()

    def master_zoom_changed(self, region):
        """
        Zoom changed in master window.

        :param region:
        """
        self.last_zoom_region = region
        for window in self.mdi_area.subWindowList():
            if not window.master:
                window.widget().setXRange(*region, padding=0, update=False)
                window.widget().setClipToView(True)
                x1, x2 = int(region[0]), int(region[1])
                self.input_from_dt.setDateTime(QDateTime.fromTime_t(x1))
                self.input_to_dt.setDateTime(QDateTime.fromTime_t(x2))
                self.readout_diff_dt.setText(get_scaled_time_duration(x2 - x1))

    def add_sub_window(self, window):
        """
        Add sub window into mdi area.

        :param window:
        """
        self.mdi_area.addSubWindow(window)
        if self.sub_windows_hint == Qt.FramelessWindowHint:
            window.widget().setTitle(window.windowTitle())
        else:
            window.widget().setTitle(None)
        window.show()

    def tile_slave_windows(self, slave_windows=None, x=0, y=0, w=None, h=None):
        """
        Organize set of slave windows in tile fashion.

        :param slave_windows: list
        :param x: int
        :param y: int
        :param w: int
        :param h: int
        """
        if slave_windows is None:
            slave_windows = self.mdi_area.subWindowList()
        if len(slave_windows) == 0:
            return
        if w is None:
            w = self.mdi_area.width()
        if h is None:
            h = self.mdi_area.height()
        for rows, i in enumerate(self.square_function_values):
            if i >= len(slave_windows):
                break
        try:
            if len(slave_windows) % rows:
                cols = int(len(slave_windows) / rows) + 1
            else:
                cols = int(len(slave_windows) / rows)
        except ZeroDivisionError:
            rows, cols = 1, 1
        slave_w = w / cols
        slave_h = h / rows
        w_pos, h_pos = 0, 0
        for index, window in enumerate(slave_windows):
            window.setGeometry(w_pos, h_pos, slave_w, slave_h)
            w_pos += slave_w
            if ((index + 1) % cols) == 0:
                h_pos += slave_h
                w_pos = 0

    def tile_list_windows(self, list_windows=None, plot_height=None):
        """
        Organize list windows in tile fashion.

        :param list_windows: list
        :param plot_height: int
        """
        if list_windows is None and len():
            list_windows = self.mdi_area.subWindowList()
        rows = len(list_windows)
        if rows == 0:
            return
        h = self.mdi_area.height()
        if plot_height is None:
            plot_height = h / rows

        w_offset = 0
        if plot_height * rows > h:
            w_offset = self.mdi_area.verticalScrollBar().width()

        w_width = self.mdi_area.width() - w_offset
        w_height = plot_height
        pos_w, pos_h = 0, 0
        for index, window in enumerate(list_windows):
            window.setGeometry(pos_w, pos_h, w_width, w_height)
            pos_h += w_height

    def resizeEvent(self, QResizeEvent):
        """
        Tile windows on resize event.

        :param QResizeEvent:
        """
        self.tile_sub_windows()
        QWidget.resizeEvent(self, QResizeEvent)

    @pyqtSlot(QMdiSubWindow)
    def slot_window_activated(self, window):
        """
        Sub window was activated, perform following actions.

        :param window:
        """
        follow_zoom_flag = self.input_zoom_follow.isChecked()
        if (
            window is not None
            and not window.master
            and self.view_mode == MODE_ZOOM
            and follow_zoom_flag
        ):
            self.input_master_row.setCurrentText(window.id)

    @pyqtSlot(bool)
    def slot_set_zoom_mode(self, flag):
        """
        View was changed zoom.

        Do nothing if flag is False.

        :param flag: bool
        """
        if flag:
            self.logger.info("View set to zoom mode.")
            self.view_mode = MODE_ZOOM
            self.tabs_view_tools.setCurrentIndex(0)
            current_sub_window = self.mdi_area.currentSubWindow()
            if current_sub_window is None:
                return
            zoom_master = self.input_master_row.currentText()
            if current_sub_window is not None:
                zoom_master = current_sub_window.id
            self.input_master_row.blockSignals(True)
            self.input_master_row.setCurrentText(zoom_master)
            self.input_master_row.blockSignals(False)
            self.slot_master_row_changed(zoom_master)

    @pyqtSlot(bool)
    def slot_set_list_mode(self, flag):
        """
        View was changed list.

        Do nothing if flag is False.

        :param flag: bool
        """
        if flag:
            self.logger.info("View set to list mode.")
            self.view_mode = MODE_LIST
            if self.master_window is not None:
                mater_window_id = self.master_window.id
                self.master_window.close()
                self.master_window.setParent(None)
                self.master_window = None
                for w in self.mdi_area.subWindowList():
                    if w.id == mater_window_id:
                        self.mdi_area.setActiveSubWindow(w)
                        break
            self.tabs_view_tools.setCurrentIndex(1)
            self.tile_sub_windows()

    @pyqtSlot(int, int)
    def slot_splitter_moved(self, x, y):
        """
        Layout splitter was moved.

        Tile all sub windows.

        :param x: int
        :param y: int
        """
        self.tile_sub_windows()

    @pyqtSlot(int)
    def slot_set_max_selected_rows(self, rows):
        """
        Maximum number of rows was changed.

        :param rows: int
        """
        self.logger.info("Maximum number of rows was set to: {}".format(rows))
        self.input_header_items.selectionModel().max_selected_rows = rows

    @pyqtSlot(str)
    def slot_master_row_changed(self, window_id):
        """
        Master row was changed.

        :param window_id: str
        """
        if self.view_mode == MODE_ZOOM:
            self.mdi_area.blockSignals(True)
            last_zoom_region = self.last_zoom_region
            master_window = self.master_window
            if master_window is not None:
                master_window.close()
                master_window.setParent(None)
            sub_window = self.create_sub_window(window_id, master=True)
            self.add_sub_window(sub_window)
            self.tile_sub_windows()

            if last_zoom_region is not None:
                self.master_window.widget().lookingGlass.setRegion(last_zoom_region)
            self.mdi_area.blockSignals(False)

    @pyqtSlot()
    def slot_set_list_min_height(self):
        """Value of minimum plot height was changed."""
        self.tile_sub_windows()

    @pyqtSlot()
    def slot_reset_zoom(self):
        """Reset zoom of Master plot."""
        self.logger.info("Resetting zoom.")
        if self.master_window is not None:
            self.master_window.widget().reset_zoom()

    @pyqtSlot()
    def slot_reset_all(self):
        """Reset zoom of Master plot."""
        self.logger.info("Resetting all plots, zoom and views.")
        self.slot_set_list_mode(True)
        self.master_window = None
        self.last_zoom_region = None
        self.view_tiled = True
        self.button_list_view.click()
        self.pushButton.click()
        self.pushButton_2.click()
        self.input_master_row.clear()

    @pyqtSlot()
    def slot_selection_changed(self, row_model_index=None):
        """
        Selection in rows list was changed.

        :param row_model_index: QItemSelection
        """
        self.view_tiled = False
        active_windows = []
        for w in self.mdi_area.subWindowList():
            if not w.master:
                active_windows.append(w.id)
        selection_model = self.input_header_items.selectionModel()
        if selection_model is not None:
            selected_row_indexes = selection_model.selectedIndexes()
            selected_rows = [
                str(row_index.data()) for row_index in selected_row_indexes
            ]

            for window in self.mdi_area.subWindowList():
                if (window.id not in selected_rows) and not window.master:
                    window.close()
                    window.setParent(None)

            for row in selected_rows:
                if row not in active_windows:
                    self.add_sub_window(self.create_sub_window(row))

        self.tile_sub_windows()
        if self.view_mode == MODE_ZOOM:
            self.master_zoom_changed(
                self.master_window.widget().lookingGlass.getRegion()
            )
        self.view_tiled = True

    def slot_select_rows(self, rows=None):
        if rows is None:
            return

        selection_model = self.input_header_items.selectionModel()
        model = self.input_header_items.model()
        for row_data in reversed(rows):
            index = model.model_data.index(row_data)
            if index > 0:
                selection = QItemSelection(
                    model.createIndex(index, 0), model.createIndex(index, 0)
                )
                selection_model.select(
                    selection, QItemSelectionModel.Select | QItemSelectionModel.Rows
                )
        self.slot_selection_changed()

    @pyqtSlot(bool)
    def slot_set_windowed_plots(self, flag):
        """
        Toggle windowed sub plots.

        Change sub windows hints and titles.

        :param flag: bool
        """
        self.input_keep_tiled.blockSignals(True)
        if not flag:
            self.input_keep_tiled.setEnabled(False)
            self.input_keep_tiled.setChecked(True)
        else:
            self.input_keep_tiled.setEnabled(True)
        self.input_keep_tiled.blockSignals(False)

        default_sub_window_hints = (
            Qt.WindowSystemMenuHint
            | Qt.WindowCloseButtonHint
            | Qt.WindowMaximizeButtonHint
        )
        self.sub_windows_hint = (
            default_sub_window_hints if flag else Qt.FramelessWindowHint
        )
        default_master_window_hint = Qt.CustomizeWindowHint | Qt.WindowTitleHint
        self.master_window_hint = (
            default_master_window_hint if flag else Qt.FramelessWindowHint
        )
        for window in self.mdi_area.subWindowList():
            if self.sub_windows_hint == Qt.FramelessWindowHint:
                window.widget().setTitle(window.windowTitle())
            else:
                window.widget().setTitle(None)

            if window.master and flag:
                window.setWindowFlags(self.master_window_hint)
            else:
                window.setWindowFlags(self.sub_windows_hint)

        self.tile_sub_windows()

    @pyqtSlot(bool)
    def slot_keep_tiled_changed(self, flag):
        """
        Toggle keep tiled changed.

        :param flag: bool
        """
        if flag:
            self.tile_sub_windows()

    def slot_export_to_pdf(self):
        if self.input_windowed_plots.isChecked():
            self.slot_set_windowed_plots(False)

        if len(self.mdi_area.subWindowList()) == 0:
            error_msg = "Export error: {}".format(
                "Please select at least one plot to export."
            )
            self.logger.error(error_msg)
            show_error_message(error_msg, self)
            return

        plot_width, plot_height = (
            self.input_plot_width.value(),
            self.input_plot_height.value(),
        )
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        extension_filter = "pdf [*.pdf] (*.pdf)"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Set output file",
            "./{}".format("output.pdf"),
            filter=extension_filter,
            initialFilter=extension_filter,
            options=options,
        )
        if file_path != "":
            self.logger.info(
                "Exporting plots to {} using w: {}px, h: {}px".format(
                    file_path, plot_width, plot_height
                )
            )
            parts = []
            cache_dir = kamzik3.session.get_value(ATTR_CACHE_DIRECTORY)
            for index, window in enumerate(reversed(self.mdi_area.subWindowList())):
                actual_size = window.widget().size()
                window.widget().resize(plot_width, plot_height)
                exporter = exporters.ImageExporter(window.widget().plotItem)
                exporter.parameters()["width"] = plot_width
                img_path = os.path.join(cache_dir, "img{}.png".format(index))
                exporter.export(img_path)
                parts.append(Image(img_path))
                window.widget().resize(actual_size)

            while True:
                try:
                    use_parts = parts.copy()
                    report = SimpleDocTemplate(
                        file_path, pagesize=(plot_width, plot_height)
                    )
                    report.build(use_parts)
                    break
                except LayoutError as e:
                    pw, ph = re.findall("([\-0-9\.]+)\sx\s([\-0-9\.]+)", str(e))[0]
                    plot_width += abs(plot_width - float(pw))
                    plot_height += abs(plot_height - float(ph))
                except Exception as e:
                    error_msg = "Export error: {}".format(e)
                    self.logger.error(error_msg)
                    show_error_message(error_msg, self)

            if self.input_windowed_plots.isChecked():
                self.slot_set_windowed_plots(True)

    def slot_export_to_csv(self):
        if len(self.mdi_area.subWindowList()) == 0:
            error_msg = "Export error: {}".format(
                "Please select at least one plot to export."
            )
            self.logger.error(error_msg)
            show_error_message(error_msg, self)
            return

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        extension_filter = "csv [*.csv] (*.csv)"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Set output file",
            "./{}".format("output.csv"),
            filter=extension_filter,
            initialFilter=extension_filter,
            options=options,
        )
        if file_path != "":
            self.logger.info("Exporting plots to {}".format(file_path))
            sel_mode = self.input_header_items.selectionModel()
            columns = []

            for item in sel_mode.selectedRows(0):
                columns.append(item.data())
            if self.last_zoom_region is None:
                self.pandas_dt.to_csv(file_path, columns=columns, index=False)
            else:
                head = self.pandas_dt.columns
                self.pandas_dt[
                    (self.pandas_dt[head[1]] >= self.last_zoom_region[0])
                    & (self.pandas_dt[head[1]] <= self.last_zoom_region[1])
                ].to_csv(file_path, columns=columns, index=False)
