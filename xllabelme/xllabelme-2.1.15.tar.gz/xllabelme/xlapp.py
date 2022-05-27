# -*- coding: utf-8 -*-

import functools
import os
import os.path as osp

import numpy as np
from qtpy import QtCore
from qtpy.QtCore import Qt
from qtpy import QtGui
from qtpy import QtWidgets

from xllabelme import __appname__
from xllabelme import PY2

from xllabelme import utils
from xllabelme.config import get_config
from xllabelme.label_file import LabelFile
from xllabelme.label_file import LabelFileError
from xllabelme.logger import logger
from xllabelme.widgets import Canvas
from xllabelme.widgets import LabelDialogExt
from xllabelme.widgets import LabelListWidget
from xllabelme.widgets import LabelListWidgetItem
from xllabelme.widgets import UniqueLabelQListWidget
from xllabelme.widgets import ZoomWidget
from xllabelme.config.xllabellib import XlLabel

from xllabelme.app import set_default_shape_colors, MainWindow

from pyxllib.prog.newbie import round_int
from pyxllib.file.specialist import XlPath

from pyxllib.cv.rgbfmt import RgbFormatter

try:  # 该组件不是必须的
    from shapely.geometry import Polygon
    from pyxllib.algo.shapelylib import ShapelyPolygon
except ModuleNotFoundError:
    ShapelyPolygon = None

# ckz relabel2项目定制映射
_COLORS = {
    '印刷体': '鲜绿色',
    '手写体': '黄色',
    '印章': '红色',
    'old': '黑色'
}
_COLORS.update({'姓名': '黑色',
                '身份证': '黄色',
                '联系方式': '金色',
                '采样时间': '浅天蓝',
                '检测时间': '蓝色',
                '核酸结果': '红色',
                '14天经过或途经': '绿色',
                '健康码颜色': '鲜绿色',
                '其他类': '亮灰色'})

_COLORS = {k: np.array(RgbFormatter.from_name(v).to_tuple(), 'uint8') for k, v in _COLORS.items()}


class XlMainWindow(MainWindow):
    def __init__(
            self,
            config=None,
            filename=None,
            output=None,
            output_file=None,
            output_dir=None,
    ):
        if output is not None:
            logger.warning(
                "argument output is deprecated, use output_file instead"
            )
            if output_file is None:
                output_file = output

        # see labelme/config/default_config.yaml for valid configuration
        if config is None:
            config = get_config()
        self._config = config

        set_default_shape_colors(self._config)

        super(MainWindow, self).__init__()
        self.setWindowTitle(f'{__appname__}')

        # Whether we need to save or not.
        self.dirty = False

        self._noSelectionSlot = False

        # Main widgets and related state.
        self.labelDialog = LabelDialogExt(
            parent=self,
            labels=self._config["labels"],
            sort_labels=self._config["sort_labels"],
            show_text_field=self._config["show_label_text_field"],
            completion=self._config["label_completion"],
            fit_to_content=self._config["fit_to_content"],
            flags=self._config["label_flags"],
        )

        # Polygon Labels 控件
        self.labelList = LabelListWidget()
        self.lastOpenDir = None

        self.flag_dock = self.flag_widget = None
        self.flag_dock = QtWidgets.QDockWidget(self.tr("Flags"), self)
        self.flag_dock.setObjectName("Flags")
        self.flag_widget = QtWidgets.QListWidget()
        if config["flags"]:
            self.loadFlags({k: False for k in config["flags"]})
        self.flag_dock.setWidget(self.flag_widget)
        self.flag_widget.itemChanged.connect(self.setDirty)

        self.labelList.itemSelectionChanged.connect(self.labelSelectionChanged)
        self.labelList.itemDoubleClicked.connect(self.editLabel)
        self.labelList.itemChanged.connect(self.labelItemChanged)
        self.labelList.itemDropped.connect(self.labelOrderChanged)
        self.shape_dock = QtWidgets.QDockWidget(
            self.tr("Polygon Labels"), self
        )
        self.shape_dock.setObjectName("Labels")
        self.shape_dock.setWidget(self.labelList)

        self.uniqLabelList = UniqueLabelQListWidget()
        self.uniqLabelList.setToolTip(
            self.tr(
                "Select label to start annotating for it. "
                "Press 'Esc' to deselect."
            )
        )
        if self._config["labels"]:
            for label in self._config["labels"]:
                item = self.uniqLabelList.createItemFromLabel(label)
                self.uniqLabelList.addItem(item)
                rgb = self._get_rgb_by_label(label)
                self.uniqLabelList.setItemLabel(item, label, rgb)
        self.label_dock = QtWidgets.QDockWidget(self.tr("Label List"), self)
        self.label_dock.setObjectName("Label List")
        self.label_dock.setWidget(self.uniqLabelList)

        self.fileSearch = QtWidgets.QLineEdit()
        self.fileSearch.setPlaceholderText(self.tr("Search Filename"))
        self.fileSearch.textChanged.connect(self.fileSearchChanged)
        self.fileListWidget = QtWidgets.QListWidget()
        self.fileListWidget.itemSelectionChanged.connect(
            self.fileSelectionChanged
        )
        fileListLayout = QtWidgets.QVBoxLayout()
        fileListLayout.setContentsMargins(0, 0, 0, 0)
        fileListLayout.setSpacing(0)
        fileListLayout.addWidget(self.fileSearch)
        fileListLayout.addWidget(self.fileListWidget)
        self.file_dock = QtWidgets.QDockWidget(self.tr("File List"), self)
        self.file_dock.setObjectName("Files")
        fileListWidget = QtWidgets.QWidget()
        fileListWidget.setLayout(fileListLayout)
        self.file_dock.setWidget(fileListWidget)

        self.zoomWidget = ZoomWidget()
        self.setAcceptDrops(True)

        self.canvas = self.labelList.canvas = Canvas(
            self,
            epsilon=self._config["epsilon"],
            double_click=self._config["canvas"]["double_click"],
            num_backups=self._config["canvas"]["num_backups"],
        )
        self.canvas.zoomRequest.connect(self.zoomRequest)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(self.canvas)
        scrollArea.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: scrollArea.verticalScrollBar(),
            Qt.Horizontal: scrollArea.horizontalScrollBar(),
        }
        self.canvas.scrollRequest.connect(self.scrollRequest)

        self.canvas.newShape.connect(self.newShape)
        self.canvas.shapeMoved.connect(self.setDirty)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)
        self.canvas.drawingPolygon.connect(self.toggleDrawingSensitive)

        self.setCentralWidget(scrollArea)

        features = QtWidgets.QDockWidget.DockWidgetFeatures()
        for dock in ["flag_dock", "label_dock", "shape_dock", "file_dock"]:
            if self._config[dock]["closable"]:
                features = features | QtWidgets.QDockWidget.DockWidgetClosable
            if self._config[dock]["floatable"]:
                features = features | QtWidgets.QDockWidget.DockWidgetFloatable
            if self._config[dock]["movable"]:
                features = features | QtWidgets.QDockWidget.DockWidgetMovable
            getattr(self, dock).setFeatures(features)
            if self._config[dock]["show"] is False:
                getattr(self, dock).setVisible(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.flag_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.label_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.shape_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.file_dock)

        # Actions
        action = functools.partial(utils.newAction, self)
        shortcuts = self._config["shortcuts"]
        quit = action(
            self.tr("&Quit"),
            self.close,
            shortcuts["quit"],
            "quit",
            self.tr("Quit application"),
        )
        open_ = action(
            self.tr("&Open"),
            self.openFile,
            shortcuts["open"],
            "open",
            self.tr("Open image or label file"),
        )
        opendir = action(
            self.tr("&Open Dir"),
            self.openDirDialog,
            shortcuts["open_dir"],
            "open",
            self.tr("Open Dir"),
        )
        openNextImg = action(
            self.tr("&Next Image"),
            self.openNextImg,
            shortcuts["open_next"],
            "next",
            self.tr("Open next (hold Ctl+Shift to copy labels)"),
            enabled=False,
        )
        openPrevImg = action(
            self.tr("&Prev Image"),
            self.openPrevImg,
            shortcuts["open_prev"],
            "prev",
            self.tr("Open prev (hold Ctl+Shift to copy labels)"),
            enabled=False,
        )
        save = action(
            self.tr("&Save"),
            self.saveFile,
            shortcuts["save"],
            "save",
            self.tr("Save labels to file"),
            enabled=False,
        )
        saveAs = action(
            self.tr("&Save As"),
            self.saveFileAs,
            shortcuts["save_as"],
            "save-as",
            self.tr("Save labels to a different file"),
            enabled=False,
        )

        deleteFile = action(
            self.tr("&Delete File"),
            self.deleteFile,
            shortcuts["delete_file"],
            "delete",
            self.tr("Delete current label file"),
            enabled=False,
        )

        changeOutputDir = action(
            self.tr("&Change Output Dir"),
            slot=self.changeOutputDirDialog,
            shortcut=shortcuts["save_to"],
            icon="open",
            tip=self.tr("Change where annotations are loaded/saved"),
        )

        saveAuto = action(
            text=self.tr("Save &Automatically"),
            slot=lambda x: self.actions.saveAuto.setChecked(x),
            icon="save",
            tip=self.tr("Save automatically"),
            checkable=True,
            enabled=True,
        )
        saveAuto.setChecked(self._config["auto_save"])

        saveWithImageData = action(
            text="Save With Image Data",
            slot=self.enableSaveImageWithData,
            tip="Save image data in label file",
            checkable=False,
            checked=False,
            enabled=False,
        )

        close = action(
            "&Close",
            self.closeFile,
            shortcuts["close"],
            "close",
            "Close current file",
        )

        toggle_keep_prev_mode = action(
            self.tr("Keep Previous Annotation"),
            self.toggleKeepPrevMode,
            shortcuts["toggle_keep_prev_mode"],
            None,
            self.tr('Toggle "keep pevious annotation" mode'),
            checkable=True,
        )
        toggle_keep_prev_mode.setChecked(self._config["keep_prev"])

        createMode = action(
            self.tr("Create Polygons"),
            lambda: self.toggleDrawMode(False, createMode="polygon"),
            shortcuts["create_polygon"],
            "objects",
            self.tr("Start drawing polygons"),
            enabled=False,
        )
        createRectangleMode = action(
            self.tr("Create Rectangle"),
            lambda: self.toggleDrawMode(False, createMode="rectangle"),
            shortcuts["create_rectangle"],
            "objects",
            self.tr("Start drawing rectangles"),
            enabled=False,
        )
        createCircleMode = action(
            self.tr("Create Circle"),
            lambda: self.toggleDrawMode(False, createMode="circle"),
            shortcuts["create_circle"],
            "objects",
            self.tr("Start drawing circles"),
            enabled=False,
        )
        createLineMode = action(
            self.tr("Create Line"),
            lambda: self.toggleDrawMode(False, createMode="line"),
            shortcuts["create_line"],
            "objects",
            self.tr("Start drawing lines"),
            enabled=False,
        )
        createPointMode = action(
            self.tr("Create Point"),
            lambda: self.toggleDrawMode(False, createMode="point"),
            shortcuts["create_point"],
            "objects",
            self.tr("Start drawing points"),
            enabled=False,
        )
        createLineStripMode = action(
            self.tr("Create LineStrip"),
            lambda: self.toggleDrawMode(False, createMode="linestrip"),
            shortcuts["create_linestrip"],
            "objects",
            self.tr("Start drawing linestrip. Ctrl+LeftClick ends creation."),
            enabled=False,
        )
        editMode = action(
            self.tr("Edit Polygons"),
            self.setEditMode,
            shortcuts["edit_polygon"],
            "edit",
            self.tr("Move and edit the selected polygons"),
            enabled=False,
        )

        delete = action(
            self.tr("Delete Polygons"),
            self.deleteSelectedShape,
            shortcuts["delete_polygon"],
            "cancel",
            self.tr("Delete the selected polygons"),
            enabled=False,
        )
        duplicate = action(
            self.tr("Duplicate Polygons"),
            self.duplicateSelectedShape,
            shortcuts["duplicate_polygon"],
            "copy",
            self.tr("Create a duplicate of the selected polygons"),
            enabled=False,
        )
        copy = action(
            self.tr("Copy Polygons"),
            self.copySelectedShape,
            shortcuts["copy_polygon"],
            "copy_clipboard",
            self.tr("Copy selected polygons to clipboard"),
            enabled=False,
        )
        paste = action(
            self.tr("Paste Polygons"),
            self.pasteSelectedShape,
            shortcuts["paste_polygon"],
            "paste",
            self.tr("Paste copied polygons"),
            enabled=False,
        )
        undoLastPoint = action(
            self.tr("Undo last point"),
            self.canvas.undoLastPoint,
            shortcuts["undo_last_point"],
            "undo",
            self.tr("Undo last drawn point"),
            enabled=False,
        )
        removePoint = action(
            text="Remove Selected Point",
            slot=self.removeSelectedPoint,
            shortcut=shortcuts["remove_selected_point"],
            icon="edit",
            tip="Remove selected point from polygon",
            enabled=False,
        )

        undo = action(
            self.tr("Undo"),
            self.undoShapeEdit,
            shortcuts["undo"],
            "undo",
            self.tr("Undo last add and edit of shape"),
            enabled=False,
        )

        hideAll = action(
            self.tr("&Hide\nPolygons"),
            functools.partial(self.togglePolygons, False),
            icon="eye",
            tip=self.tr("Hide all polygons"),
            enabled=False,
        )
        showAll = action(
            self.tr("&Show\nPolygons"),
            functools.partial(self.togglePolygons, True),
            icon="eye",
            tip=self.tr("Show all polygons"),
            enabled=False,
        )

        help = action(
            self.tr("&Tutorial"),
            self.tutorial,
            icon="help",
            tip=self.tr("Show tutorial page"),
        )

        zoom = QtWidgets.QWidgetAction(self)
        zoom.setDefaultWidget(self.zoomWidget)
        self.zoomWidget.setWhatsThis(
            str(
                self.tr(
                    "Zoom in or out of the image. Also accessible with "
                    "{} and {} from the canvas."
                )
            ).format(
                utils.fmtShortcut(
                    "{},{}".format(shortcuts["zoom_in"], shortcuts["zoom_out"])
                ),
                utils.fmtShortcut(self.tr("Ctrl+Wheel")),
            )
        )
        self.zoomWidget.setEnabled(False)

        zoomIn = action(
            self.tr("Zoom &In"),
            functools.partial(self.addZoom, 1.1),
            shortcuts["zoom_in"],
            "zoom-in",
            self.tr("Increase zoom level"),
            enabled=False,
        )
        zoomOut = action(
            self.tr("&Zoom Out"),
            functools.partial(self.addZoom, 0.9),
            shortcuts["zoom_out"],
            "zoom-out",
            self.tr("Decrease zoom level"),
            enabled=False,
        )
        zoomOrg = action(
            self.tr("&Original size"),
            functools.partial(self.setZoom, 100),
            shortcuts["zoom_to_original"],
            "zoom",
            self.tr("Zoom to original size"),
            enabled=False,
        )
        keepPrevScale = action(
            self.tr("&Keep Previous Scale"),
            self.enableKeepPrevScale,
            tip=self.tr("Keep previous zoom scale"),
            checkable=True,
            checked=self._config["keep_prev_scale"],
            enabled=True,
        )
        fitWindow = action(
            self.tr("&Fit Window"),
            self.setFitWindow,
            shortcuts["fit_window"],
            "fit-window",
            self.tr("Zoom follows window size"),
            checkable=True,
            enabled=False,
        )
        fitWidth = action(
            self.tr("Fit &Width"),
            self.setFitWidth,
            shortcuts["fit_width"],
            "fit-width",
            self.tr("Zoom follows window width"),
            checkable=True,
            enabled=False,
        )
        brightnessContrast = action(
            "&Brightness Contrast",
            self.brightnessContrast,
            None,
            "color",
            "Adjust brightness and contrast",
            enabled=False,
        )
        # Group zoom controls into a list for easier toggling.
        zoomActions = (
            self.zoomWidget,
            zoomIn,
            zoomOut,
            zoomOrg,
            fitWindow,
            fitWidth,
        )
        self.zoomMode = self.FIT_WINDOW
        fitWindow.setChecked(Qt.Checked)
        self.scalers = {
            self.FIT_WINDOW: self.scaleFitWindow,
            self.FIT_WIDTH: self.scaleFitWidth,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM: lambda: 1,
        }

        edit = action(
            self.tr("&Edit Label"),
            self.editLabel,
            shortcuts["edit_label"],
            "edit",
            self.tr("Modify the label of the selected polygon"),
            enabled=False,
        )

        fill_drawing = action(
            self.tr("Fill Drawing Polygon"),
            self.canvas.setFillDrawing,
            None,
            "color",
            self.tr("Fill polygon while drawing"),
            checkable=True,
            enabled=True,
        )
        fill_drawing.trigger()

        self.add_point_to_edge_action = utils.qt.newCheckableAction(
            self,
            self.tr("Add Point to Edge Enable"),
            tip=self.tr("选中shape的edge时，增加分割点"),
        )

        self.delete_selected_shape_with_warning_action = utils.qt.newCheckableAction(
            self,
            self.tr("Delete Selected Shape With Warning"),
            checked=True,
        )

        # Lavel list context menu.
        labelMenu = QtWidgets.QMenu()
        utils.addActions(labelMenu, (edit, delete))
        self.labelList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.labelList.customContextMenuRequested.connect(
            self.popLabelListMenu
        )

        # ckz扩展的一些高级功能
        self.xllabel = XlLabel(self)

        # Store actions for further handling.
        self.actions = utils.struct(
            saveAuto=saveAuto,
            saveWithImageData=saveWithImageData,
            changeOutputDir=changeOutputDir,
            save=save,
            saveAs=saveAs,
            open=open_,
            close=close,
            deleteFile=deleteFile,
            toggleKeepPrevMode=toggle_keep_prev_mode,
            delete=delete,
            edit=edit,
            duplicate=duplicate,
            copy=copy,
            paste=paste,
            undoLastPoint=undoLastPoint,
            undo=undo,
            removePoint=removePoint,
            createMode=createMode,
            editMode=editMode,
            createRectangleMode=createRectangleMode,
            createCircleMode=createCircleMode,
            createLineMode=createLineMode,
            createPointMode=createPointMode,
            createLineStripMode=createLineStripMode,
            zoom=zoom,
            zoomIn=zoomIn,
            zoomOut=zoomOut,
            zoomOrg=zoomOrg,
            keepPrevScale=keepPrevScale,
            fitWindow=fitWindow,
            fitWidth=fitWidth,
            brightnessContrast=brightnessContrast,
            zoomActions=zoomActions,
            openNextImg=openNextImg,
            openPrevImg=openPrevImg,
            fileMenuActions=(open_, opendir, save, saveAs, close, quit),
            tool=(),
            # XXX: need to add some actions here to activate the shortcut
            editMenu=(
                edit,
                duplicate,
                delete,
                None,
                undo,
                undoLastPoint,
                None,
                removePoint,
                None,
                toggle_keep_prev_mode,
                None,
                self.add_point_to_edge_action,
                self.delete_selected_shape_with_warning_action,
            ),
            # menu shown at right click
            menu=(
                createMode,
                createRectangleMode,
                createCircleMode,
                createLineMode,
                createPointMode,
                createLineStripMode,
                editMode,
                edit,
                duplicate,
                copy,
                paste,
                delete,
                undo,
                undoLastPoint,
                removePoint,
                None,
                self.xllabel.convert_to_rectangle_action(),
                self.xllabel.split_shape_action(),
            ),
            onLoadActive=(
                close,
                createMode,
                createRectangleMode,
                createCircleMode,
                createLineMode,
                createPointMode,
                createLineStripMode,
                editMode,
                brightnessContrast,
            ),
            onShapesPresent=(saveAs, hideAll, showAll),
        )

        # self.canvas.edgeSelected.connect(self.canvasShapeEdgeSelected)
        self.canvas.vertexSelected.connect(self.actions.removePoint.setEnabled)

        self.menus = utils.struct(
            file=self.menu(self.tr("&File")),
            edit=self.menu(self.tr("&Edit")),
            view=self.menu(self.tr("&View")),
            help=self.menu(self.tr("&Help")),
            label=self.menu(self.tr("&Label")),  # 标注文本相关工具
            recentFiles=QtWidgets.QMenu(self.tr("Open &Recent")),
            labelList=labelMenu,
        )

        utils.addActions(
            self.menus.file,
            (
                open_,
                openNextImg,
                openPrevImg,
                opendir,
                self.menus.recentFiles,
                save,
                saveAs,
                saveAuto,
                changeOutputDir,
                saveWithImageData,
                close,
                deleteFile,
                None,
                quit,
            ),
        )
        utils.addActions(self.menus.help, (help,))
        utils.addActions(
            self.menus.view,
            (
                self.flag_dock.toggleViewAction(),
                self.label_dock.toggleViewAction(),
                self.shape_dock.toggleViewAction(),
                self.file_dock.toggleViewAction(),
                None,
                fill_drawing,
                None,
                hideAll,
                showAll,
                None,
                zoomIn,
                zoomOut,
                zoomOrg,
                keepPrevScale,
                None,
                fitWindow,
                fitWidth,
                None,
                brightnessContrast,
            ),
        )

        self.menus.file.aboutToShow.connect(self.updateFileMenu)

        self.xllabel.config_label_menu()

        # Custom context menu for the canvas widget:
        utils.addActions(self.canvas.menus[0], self.actions.menu)
        utils.addActions(
            self.canvas.menus[1],
            (
                action("&Copy here", self.copyShape),
                action("&Move here", self.moveShape),
            ),
        )

        self.tools = self.toolbar("Tools")
        # Menu buttons on Left
        self.actions.tool = (
            open_,
            opendir,
            openNextImg,
            openPrevImg,
            save,
            deleteFile,
            None,
            createMode,
            editMode,
            duplicate,
            copy,
            paste,
            delete,
            undo,
            brightnessContrast,
            None,
            zoom,
            fitWidth,
        )

        self.statusBar().showMessage(str(self.tr("%s started.")) % __appname__)
        self.statusBar().show()

        if output_file is not None and self._config["auto_save"]:
            logger.warn(
                "If `auto_save` argument is True, `output_file` argument "
                "is ignored and output filename is automatically "
                "set as IMAGE_BASENAME.json."
            )
        self.output_file = output_file
        self.output_dir = output_dir

        # Application state.
        self.image = QtGui.QImage()
        self.imagePath = None
        self.arr_image = None  # cv2格式的图片
        self.recentFiles = []
        self.maxRecent = 7
        self.otherData = None
        self.zoom_level = 100
        self.fit_window = False
        self.zoom_values = {}  # key=filename, value=(zoom_mode, zoom_value)
        self.brightnessContrast_values = {}
        self.scroll_values = {
            Qt.Horizontal: {},
            Qt.Vertical: {},
        }  # key=filename, value=scroll_value

        if filename is not None and osp.isdir(filename):
            self.importDirImages(filename, load=False)
        else:
            self.filename = filename

        if config["file_search"]:
            self.fileSearch.setText(config["file_search"])
            self.fileSearchChanged()

        # XXX: Could be completely declarative.
        # Restore application settings.
        self.settings = QtCore.QSettings("labelme", "labelme")
        # FIXME: QSettings.value can return None on PyQt4
        self.recentFiles = self.settings.value("recentFiles", []) or []
        size = self.settings.value("window/size", QtCore.QSize(600, 500))
        position = self.settings.value("window/position", QtCore.QPoint(0, 0))
        state = self.settings.value("window/state", QtCore.QByteArray())
        self.resize(size)
        self.move(position)
        # or simply:
        # self.restoreGeometry(settings['window/geometry']
        self.restoreState(state)

        # Populate the File menu dynamically.
        self.updateFileMenu()
        # Since loading the file may take some time,
        # make sure it runs in the background.
        if self.filename is not None:
            self.queueEvent(functools.partial(self.loadFile, self.filename))

        # Callbacks:
        self.zoomWidget.valueChanged.connect(self.paintCanvas)

        self.populateModeActions()

        # self.firstStart = True
        # if self.firstStart:
        #    QWhatsThis.enterWhatsThisMode()

    def extendShapeMessage(self, shape):
        """ shape中自定义字段等信息

        :param shape: shape对象
        :return: 格式化的字符串内容
        """
        # 只考虑other_data中的数据
        datas = shape.other_data
        # 去掉扩展的颜色功能
        hides = {'shape_color', 'line_color', 'vertex_fill_color', 'hvertex_fill_color',
                 'fill_color', 'select_line_color', 'select_fill_color'}
        if self.label_hide_attrs.checked:
            hides |= {k for k in self.label_hide_attrs.value}
        keys = datas.keys() - hides
        msgs = [f'{k}={datas[k]}' for k in sorted(keys)]
        return ', '.join(msgs)

    def editLabel(self, item=None):
        if item and not isinstance(item, LabelListWidgetItem):
            raise TypeError("item must be LabelListWidgetItem type")

        if not self.canvas.editing():
            return
        if not item:
            item = self.currentItem()
        if item is None:
            return
        shape = item.shape()
        if shape is None:
            return

        shape2 = self.labelDialog.popUp2(shape, self)
        if shape2 is None:
            return

        text, flags, group_id = shape2.label, shape2.flags, shape2.group_id

        if text is None:
            return
        if not self.validateLabel(text):
            self.errorMessage(
                self.tr("Invalid label"),
                self.tr("Invalid label '{}' with validation type '{}'").format(
                    text, self._config["validate_label"]
                ),
            )
            return
        shape.label = text
        shape.flags = flags
        shape.group_id = group_id
        self.updateShape(shape, item)

        self.setDirty()
        if not self.uniqLabelList.findItemsByLabel(shape.label):
            item = QtWidgets.QListWidgetItem()
            item.setData(Qt.UserRole, shape.label)
            self.uniqLabelList.addItem(item)

    def addLabel(self, shape):
        """ 重载了官方的写法，这里这种写法才能兼容xllabelme的shape颜色渲染规则
        """
        label_list_item = self.updateShape(shape)
        self.labelList.addItem(label_list_item)
        shape.other_data = {}

    def updateShapes(self, shapes):
        """ 自己扩展的

        输入新的带顺序的shapes集合，更新canvas和labelList相关配置
        """
        self.canvas.shapes = shapes
        self.canvas.storeShapes()  # 备份形状

        # 不知道怎么insertItem，干脆全部清掉，重新画
        self.labelList.clear()
        for sp in self.canvas.shapes:
            label_list_item = self.updateShape(sp)
            self.labelList.addItem(label_list_item)

    def updateLabelListItems(self):
        for i in range(len(self.labelList)):
            item = self.labelList[i]
            self.updateShape(item.shape(), item)

    def updateShape(self, shape, label_list_item=None):
        """
        :param shape:
        :param label_list_item: item是shape的父级，挂在labelList下的项目
        """
        # 1 确定显示的文本 text
        self.xllabel.update_other_data(shape)
        showtext, hashtext, labelattr = self.xllabel.parse_shape(shape)
        if label_list_item:
            label_list_item.setText(showtext)
        else:
            label_list_item = LabelListWidgetItem(showtext, shape)

        # 2 保存label处理历史
        def parse_htext(htext):
            if htext and not self.uniqLabelList.findItemsByLabel(htext):
                item = self.uniqLabelList.createItemFromLabel(htext)
                self.uniqLabelList.addItem(item)
                rgb = self._get_rgb_by_label(htext)
                self.uniqLabelList.setItemLabel(item, htext, rgb)
                return rgb
            elif htext:
                return self._get_rgb_by_label(htext)
            else:
                return None

        parse_htext(hashtext)
        self.labelDialog.addLabelHistory(hashtext)
        for action in self.actions.onShapesPresent:
            action.setEnabled(True)

        # 3 定制颜色
        # 如果有定制颜色，则取用户设置的r, g, b作为shape颜色
        # 否则按照官方原版labelme的方式，通过label哈希设置
        hash_colors = self._get_rgb_by_label(hashtext)
        r, g, b = 0, 0, 0

        def seleter(key, default=None):
            if default is None:
                default = [r, g, b]

            if key in labelattr:
                v = labelattr[key]
            else:
                v = None

            if v:
                if len(v) == 3 and len(default) == 4:
                    # 如果默认值有透明通道，而设置的时候只写了rgb，没有写alpha通道，则增设默认的alpha透明度
                    v.append(default[-1])
                for i in range(len(v)):
                    if v[i] == -1:  # 用-1标记的位，表示用原始的hash映射值
                        v[i] = hash_colors[i]
                return v
            else:
                return default

        r, g, b = seleter('shape_color', hash_colors.tolist())[:3]
        label_list_item.setText(
            '{} <font color="#{:02x}{:02x}{:02x}">●</font>'.format(
                showtext, r, g, b
            )
        )

        # 注意，只有用shape_color才能全局调整颜色，下面六个属性是单独调的
        # 线的颜色
        rgb_ = parse_htext(self.xllabel.get_hashtext(labelattr, 'label_line_color'))
        shape.line_color = QtGui.QColor(*seleter('line_color', rgb_))
        # 顶点颜色
        rgb_ = parse_htext(self.xllabel.get_hashtext(labelattr, 'label_vertex_fill_color'))
        shape.vertex_fill_color = QtGui.QColor(*seleter('vertex_fill_color', rgb_))
        # 悬停时顶点颜色
        shape.hvertex_fill_color = QtGui.QColor(*seleter('hvertex_fill_color', (255, 255, 255)))
        # 填充颜色
        shape.fill_color = QtGui.QColor(*seleter('fill_color', (r, g, b, 128)))
        # 选中时的线、填充颜色
        shape.select_line_color = QtGui.QColor(*seleter('select_line_color', (255, 255, 255)))
        shape.select_fill_color = QtGui.QColor(*seleter('select_fill_color', (r, g, b, 155)))

        return label_list_item

    def _get_rgb_by_label(self, label):
        """ 该函数可以强制限定某些映射颜色 """
        if label in _COLORS:
            return _COLORS[label]

        # 原来的颜色配置代码
        if self._config["shape_color"] == "auto":
            try:
                item = self.uniqLabelList.findItemsByLabel(label)[0]
                label_id = self.uniqLabelList.indexFromItem(item).row() + 1
            except IndexError:
                label_id = 0
            label_id += self._config["shift_auto_shape_color"]
            return self.LABEL_COLORMAP[label_id % len(self.LABEL_COLORMAP)]
        elif (
                self._config["shape_color"] == "manual"
                and self._config["label_colors"]
                and label in self._config["label_colors"]
        ):
            return self._config["label_colors"][label]
        elif self._config["default_shape_color"]:
            return self._config["default_shape_color"]

    def saveLabels(self, filename):
        lf = LabelFile()

        # 1 取出核心数据进行保存
        def format_shape(s):
            data = s.other_data.copy()
            data.update(
                dict(
                    label=s.label.encode("utf-8") if PY2 else s.label,
                    points=[(round(p.x(), 2), round(p.y(), 2)) for p in s.points],  # 保存的点集数据精度不需要太高，两位小数足够了
                    group_id=s.group_id,
                    shape_type=s.shape_type,
                    flags=s.flags,
                )
            )
            return data

        # shapes标注数据，用的是labelList里存储的item.shape()
        shapes = [format_shape(item.shape()) for item in self.labelList]
        flags = {}  # 每张图分类时，每个类别的标记，True或False
        # 整张图的分类标记
        for i in range(self.flag_widget.count()):
            item = self.flag_widget.item(i)
            key = item.text()
            flag = item.checkState() == Qt.Checked
            flags[key] = flag
        try:
            imagePath = osp.relpath(self.imagePath, osp.dirname(filename))
            # 强制不保存 imageData
            imageData = self.imageData if self._config["store_data"] else None
            if osp.dirname(filename) and not osp.exists(osp.dirname(filename)):
                os.makedirs(osp.dirname(filename))
            lf.save(
                filename=filename,
                shapes=shapes,
                imagePath=imagePath,
                imageData=imageData,
                imageHeight=self.image.height(),
                imageWidth=self.image.width(),
                otherData=self.otherData,
                flags=flags,
            )

            # 2 fileList里可能原本没有标记json文件的，现在可以标记
            self.labelFile = lf
            items = self.fileListWidget.findItems(
                self.imagePath, Qt.MatchExactly
            )
            if len(items) > 0:
                if len(items) != 1:
                    raise RuntimeError("There are duplicate files.")
                items[0].setCheckState(Qt.Checked)
            # disable allows next and previous image to proceed
            # self.filename = filename
            return True
        except LabelFileError as e:
            self.errorMessage(
                self.tr("Error saving label data"), self.tr("<b>%s</b>") % e
            )
            return False

    @property
    def check_add_point_to_edge(self):
        """ 判断添加点到多边形edge上的功能是否有打开 """
        return self.add_point_to_edge_action.isChecked()

    def __get_describe(self):
        """ 各种悬停的智能提示 """

    def get_pos_desc(self, pos, brief=False):
        """ 当前光标所在位置的提示

        :param pos: 相对原图尺寸、位置的坐标点

        光标位置、所在像素rgb值信息

        因为左下角的状态栏不支持富文本格式，所以一般光标信息是加到ToolTip
        """
        if not self.imagePath:
            return ''

        # 1 坐标
        x, y = round(pos.x(), 2), round(pos.y(), 2)
        tip = f'pos(x={x}, y={y})'
        # 2 像素值
        h, w, _ = (0, 0, 0) if self.arr_image is None else self.arr_image.shape
        if 0 <= x < w - 1 and 0 <= y < h - 1:
            rgb = self.arr_image[round_int(y), round_int(x)].tolist()  # 也有可能是rgba，就会有4个值
            if brief:
                tip += f'，rgb={rgb}'
            else:
                color_dot = f'<font color="#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}">●</font>'
                tip += f'<br/>{color_dot}rgb={rgb}{color_dot}'
        return tip

    def get_image_desc(self):
        """ 鼠标停留在图片上时的提示内容，原始默认是Image

        这个一般是设置到状态栏展示
        """
        if not self.imagePath:
            return ''
        canvas = self.canvas
        pixmap = canvas.pixmap
        # files_num = len(self.fileListWidget)
        filesize = XlPath(self.imagePath).size(human_readable=True)
        shapes_num = len(self.canvas.shapes)
        tip = f'本图信息：图片文件大小={filesize}, height×width={pixmap.height()}×{pixmap.width()}，' \
              f'scale={canvas.scale:g}，shapes_num={shapes_num}'
        return tip

    def get_shape_desc(self, shape, pos):
        # 1 形状、坐标点（四舍五入保留整数值）
        tip = 'shape信息：' + shape.shape_type
        tip += ' ' + str([(round_int(p.x()), round_int(p.y())) for p in shape.points])
        # 2 如果有flags标记
        if shape.flags:
            tip += f'，{shape.flags}'
        # 3 增加个area面积信息
        if ShapelyPolygon:
            poly = ShapelyPolygon.gen([(p.x(), p.y()) for p in shape.points])
            tip += f'，area={poly.area:.0f}'
        # + 坐标信息
        tip += f'；{self.get_pos_desc(pos, True)}'
        return tip

    def showMessage(self, text):
        """ setStatusBar只是设置值，而不是显示值
        显示值得用下述方式实现~~
        """
        self.statusBar().showMessage(text)
