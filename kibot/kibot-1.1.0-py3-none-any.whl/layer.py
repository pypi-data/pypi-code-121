# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
import pcbnew
from .optionable import Optionable
from .gs import GS
from .misc import W_NOTASCII
from re import match
from .error import (PlotError, KiPlotConfigurationError)
from .macros import macros, document, output_class  # noqa: F401
from . import log

logger = log.get_logger()


LAYER_ORDER = ['F.Cu', 'F.Mask', 'F.SilkS', 'F.Paste', 'F.Adhes', 'F.CrtYd', 'F.Fab', 'Dwgs.User', 'Cmts.User', 'Eco1.User',
               'Eco2.User', 'Edge.Cuts', 'Margin', 'User.1', 'User.2', 'User.3', 'User.4', 'User.5', 'User.6', 'User.7',
               'User.8', 'User.9', 'In1.Cu', 'In2.Cu', 'In3.Cu', 'In4.Cu', 'In5.Cu', 'In6.Cu', 'In7.Cu', 'In8.Cu', 'In9.Cu',
               'In10.Cu', 'In11.Cu', 'In12.Cu', 'In13.Cu', 'In14.Cu', 'In15.Cu', 'In16.Cu', 'In17.Cu', 'In18.Cu', 'In19.Cu',
               'In20.Cu', 'In21.Cu', 'In22.Cu', 'In23.Cu', 'In24.Cu', 'In25.Cu', 'In26.Cu', 'In27.Cu', 'In28.Cu', 'In29.Cu',
               'In30.Cu', 'B.Cu', 'B.Mask', 'B.SilkS', 'B.Paste', 'B.Adhes', 'B.CrtYd', 'B.Fab']
LAYER_PRIORITY = {}


def create_print_priority(board):
    """ Fills LAYER_PRIORITY. This is used to sort layers for printing.
        It is the way KiCad sorts the layers.
        We do it as soon as we have a valid board. """
    global LAYER_PRIORITY
    if len(LAYER_PRIORITY) > 0:
        return
    LAYER_PRIORITY = {board.GetLayerID(name): c for c, name in enumerate(LAYER_ORDER)}


def get_priority(id):
    return LAYER_PRIORITY.get(id, 1e6)


class Layer(Optionable):
    """ A layer description """
    # Default names
    DEFAULT_LAYER_NAMES = {
        'F.Cu': pcbnew.F_Cu,
        'B.Cu': pcbnew.B_Cu,
        'F.Adhes': pcbnew.F_Adhes,
        'B.Adhes': pcbnew.B_Adhes,
        'F.Paste': pcbnew.F_Paste,
        'B.Paste': pcbnew.B_Paste,
        'F.SilkS': pcbnew.F_SilkS,
        'B.SilkS': pcbnew.B_SilkS,
        'F.Mask': pcbnew.F_Mask,
        'B.Mask': pcbnew.B_Mask,
        'Dwgs.User': pcbnew.Dwgs_User,
        'Cmts.User': pcbnew.Cmts_User,
        'Eco1.User': pcbnew.Eco1_User,
        'Eco2.User': pcbnew.Eco2_User,
        'Edge.Cuts': pcbnew.Edge_Cuts,
        'Margin': pcbnew.Margin,
        'F.CrtYd': pcbnew.F_CrtYd,
        'B.CrtYd': pcbnew.B_CrtYd,
        'F.Fab': pcbnew.F_Fab,
        'B.Fab': pcbnew.B_Fab,
    }
    # ID to default name table
    ID_2_DEFAULT_NAME = None
    # Default names
    DEFAULT_LAYER_DESC = {
        'F.Cu': 'Front copper',
        'B.Cu': 'Bottom copper',
        'F.Adhes': 'Front adhesive (glue)',
        'B.Adhes': 'Bottom adhesive (glue)',
        'F.Adhesive': 'Front adhesive (glue)',
        'B.Adhesive': 'Bottom adhesive (glue)',
        'F.Paste': 'Front solder paste',
        'B.Paste': 'Bottom solder paste',
        'F.SilkS': 'Front silkscreen (artwork)',
        'B.SilkS': 'Bottom silkscreen (artwork)',
        'F.Silkscreen': 'Front silkscreen (artwork)',
        'B.Silkscreen': 'Bottom silkscreen (artwork)',
        'F.Mask': 'Front soldermask (negative)',
        'B.Mask': 'Bottom soldermask (negative)',
        'Dwgs.User': 'User drawings',
        'User.Drawings': 'User drawings',
        'Cmts.User': 'User comments',
        'User.Comments': 'User comments',
        'Eco1.User': 'For user usage 1',
        'Eco2.User': 'For user usage 2',
        'User.Eco1': 'For user usage 1',
        'User.Eco2': 'For user usage 2',
        'Edge.Cuts': 'Board shape',
        'Margin': 'Margin relative to edge cut',
        'F.CrtYd': 'Front courtyard area',
        'B.CrtYd': 'Bottom courtyard area',
        'F.Courtyard': 'Front courtyard area',
        'B.Courtyard': 'Bottom courtyard area',
        'F.Fab': 'Front documentation',
        'B.Fab': 'Bottom documentation',
        'User.1': 'User layer 1',
        'User.2': 'User layer 2',
        'User.3': 'User layer 3',
        'User.4': 'User layer 4',
        'User.5': 'User layer 5',
        'User.6': 'User layer 6',
        'User.7': 'User layer 7',
        'User.8': 'User layer 8',
        'User.9': 'User layer 9',
    }
    KICAD6_RENAME = {
        'F.Adhes': 'F.Adhesive',
        'B.Adhes': 'B.Adhesive',
        'F.SilkS': 'F.Silkscreen',
        'B.SilkS': 'B.Silkscreen',
        'Dwgs.User': 'User.Drawings',
        'Cmts.User': 'User.Comments',
        'Eco1.User': 'User.Eco1',
        'Eco2.User': 'User.Eco2',
        'F.CrtYd': 'F.Courtyard',
        'B.CrtYd': 'B.Courtyard',
    }
    # Protel extensions
    PROTEL_EXTENSIONS = {
        pcbnew.F_Cu: 'gtl',
        pcbnew.B_Cu: 'gbl',
        pcbnew.F_Adhes: 'gta',
        pcbnew.B_Adhes: 'gba',
        pcbnew.F_Paste: 'gtp',
        pcbnew.B_Paste: 'gbp',
        pcbnew.F_SilkS: 'gto',
        pcbnew.B_SilkS: 'gbo',
        pcbnew.F_Mask: 'gts',
        pcbnew.B_Mask: 'gbs',
        pcbnew.Edge_Cuts: 'gm1',
    }
    # Names from the board file
    _pcb_layers = None
    _plot_layers = None

    def __init__(self):
        super().__init__()
        with document:
            self.layer = ''
            """ Name of the layer. As you see it in KiCad """
            self.suffix = ''
            """ Suffix used in file names related to this layer. Derived from the name if not specified """
            self.description = ''
            """ A description for the layer, for documentation purposes """
        self._unkown_is_error = True
        self._protel_extension = None

    def config(self, parent):
        super().config(parent)
        if not self.layer:
            raise KiPlotConfigurationError("Missing or empty `layer` attribute for layer entry ({})".format(self._tree))
        if not self.description:
            if self.layer in Layer.DEFAULT_LAYER_DESC:
                self.description = Layer.DEFAULT_LAYER_DESC[self.layer]
            else:
                self.description = 'No description'
        if not self.suffix:
            self.suffix = self.layer.replace('.', '_')
        self.clean_suffix()

    @staticmethod
    def reset():
        Layer._pcb_layers = None
        Layer._plot_layers = None

    def clean_suffix(self):
        filtered_suffix = ''.join(char for char in self.suffix if ord(char) < 128)
        if filtered_suffix != self.suffix:
            logger.warning(W_NOTASCII+'Only ASCII chars are allowed for layer suffixes ({}), using {}'.
                           format(self, filtered_suffix))
            self.suffix = filtered_suffix

    @property
    def id(self):
        return self._id

    def fix_protel_ext(self):
        """ Makes sure we have a defined Protel extension """
        if self._protel_extension is not None:
            # Already set, keep it
            return
        if self._is_inner:
            self._protel_extension = 'g'+str(self.id-pcbnew.F_Cu+1)
            return
        if self.id in Layer.PROTEL_EXTENSIONS:
            self._protel_extension = Layer.PROTEL_EXTENSIONS[self.id]
            return
        self._protel_extension = 'gbr'
        return

    @classmethod
    def solve(cls, values):
        board = GS.board
        layer_cnt = 2
        if board:
            layer_cnt = board.GetCopperLayerCount()
            create_print_priority(board)
        # Get the list of used layers from the board
        # Used for 'all' but also to validate the layer names
        if Layer._pcb_layers is None:
            Layer._pcb_layers = {}
            if board:
                Layer._set_pcb_layers()
        # Get the list of selected layers for plot operations from the board
        if Layer._plot_layers is None:
            Layer._plot_layers = {}
            if board:
                Layer._set_plot_layers()
        # Solve string
        if isinstance(values, str):
            values = [values]
        # Solve list
        if isinstance(values, list):
            new_vals = []
            for layer in values:
                if isinstance(layer, Layer):
                    layer._get_layer_id_from_name()
                    # Check if the layer is in use
                    if layer._is_inner and (layer._id < 1 or layer._id >= layer_cnt - 1):
                        raise PlotError("Inner layer `{}` is not valid for this board".format(layer))
                    layer.fix_protel_ext()
                    new_vals.append(layer)
                elif isinstance(layer, int):
                    new_vals.append(cls.create_layer(layer))
                else:  # A string
                    ext = None
                    if layer == 'all':
                        ext = Layer._get_layers(Layer._pcb_layers)
                    elif layer == 'selected':
                        ext = Layer._get_layers(Layer._plot_layers)
                    elif layer == 'copper':
                        ext = Layer._get_layers(Layer._get_copper())
                    elif layer == 'technical':
                        ext = Layer._get_layers(Layer._get_technical())
                    elif layer == 'user':
                        ext = Layer._get_layers(Layer._get_user())
                    elif layer in Layer._pcb_layers:
                        ext = [cls.create_layer(layer)]
                    # Give compatibility for the KiCad 5 default names (automagically renamed by KiCad 6)
                    elif GS.ki6() and layer in Layer.KICAD6_RENAME:
                        ext = [cls.create_layer(Layer.KICAD6_RENAME[layer])]
                    elif layer in Layer.DEFAULT_LAYER_NAMES:
                        ext = [cls.create_layer(layer)]
                    if ext is None:
                        raise KiPlotConfigurationError("Unknown layer spec: `{}`".format(layer))
                    new_vals.extend(ext)
            return new_vals
        raise AssertionError("Unimplemented layer type "+str(type(values)))

    @staticmethod
    def _get_copper():
        return {GS.board.GetLayerName(id): id for id in GS.board.GetEnabledLayers().CuStack()}

    @staticmethod
    def _get_technical():
        return {GS.board.GetLayerName(id): id for id in GS.board.GetEnabledLayers().Technicals()}

    @staticmethod
    def _get_user():
        return {GS.board.GetLayerName(id): id for id in GS.board.GetEnabledLayers().Users()}

    @staticmethod
    def _set_pcb_layers():
        Layer._pcb_layers = {GS.board.GetLayerName(id): id for id in GS.board.GetEnabledLayers().Seq()}

    @classmethod
    def create_layer(cls, name):
        layer = cls()
        if isinstance(name, str):
            layer.layer = name
            layer._get_layer_id_from_name()
        else:
            layer._id = name
            layer._is_inner = name > pcbnew.F_Cu and name < pcbnew.B_Cu
            name = GS.board.GetLayerName(name)
            layer.layer = name
        layer.suffix = name.replace('.', '_')
        layer.description = Layer.DEFAULT_LAYER_DESC.get(name, '')
        layer.fix_protel_ext()
        layer.clean_suffix()
        return layer

    @staticmethod
    def _get_layers(d_layers):
        layers = []
        for n in d_layers.keys():
            layers.append(Layer.create_layer(n))
        return layers

    @staticmethod
    def _set_plot_layers():
        board = GS.board
        enabled = board.GetEnabledLayers().Seq()
        for id in board.GetPlotOptions().GetLayerSelection().Seq():
            if id in enabled:
                Layer._plot_layers[board.GetLayerName(id)] = id

    def _get_layer_id_from_name(self):
        """ Get the pcbnew layer from the string provided in the config """
        # Priority
        # 1) Internal list
        if self.layer in Layer.DEFAULT_LAYER_NAMES:
            self._id = Layer.DEFAULT_LAYER_NAMES[self.layer]
            self._is_inner = False
        else:
            id = Layer._pcb_layers.get(self.layer)
            if id is not None:
                # 2) List from the PCB
                self._id = id
                self._is_inner = id > pcbnew.F_Cu and id < pcbnew.B_Cu
            elif self.layer.startswith("Inner"):
                # 3) Inner.N names
                m = match(r"^Inner\.([0-9]+)$", self.layer)
                if not m:
                    raise KiPlotConfigurationError("Malformed inner layer name: `{}`, use Inner.N".format(self.layer))
                self._id = int(m.group(1))
                self._is_inner = True
            else:
                raise KiPlotConfigurationError("Unknown layer name: `{}`".format(self.layer))
        return self._id

    def is_copper(self):
        return self._id >= pcbnew.F_Cu and self._id <= pcbnew.B_Cu

    def is_top(self):
        return self._id == pcbnew.F_Cu

    def is_bottom(self):
        return self._id == pcbnew.B_Cu

    def __str__(self):
        if hasattr(self, '_id'):
            return "{} ({} '{}' {})".format(self.layer, self._id, self.description, self.suffix)
        return "{} ('{}' {})".format(self.layer, self.description, self.suffix)

    @staticmethod
    def id2def_name(id):
        if GS.ki5():
            return Layer.ID_2_DEFAULT_NAME[id]
        return pcbnew.LayerName(id)


# Add all the Inner layers
for i in range(1, 30):
    name = 'In'+str(i)+'.Cu'
    Layer.DEFAULT_LAYER_NAMES[name] = pcbnew.In1_Cu+i-1
    Layer.DEFAULT_LAYER_DESC[name] = 'Inner layer '+str(i)
if GS.ki6():
    # Add all the User.N layers
    for i in range(1, 10):
        name = 'User.'+str(i)
        Layer.DEFAULT_LAYER_NAMES[name] = pcbnew.User_1+i-1
        Layer.DEFAULT_LAYER_DESC[name] = 'User layer '+str(i)
Layer.ID_2_DEFAULT_NAME = {v: k for k, v in Layer.DEFAULT_LAYER_NAMES.items()}
