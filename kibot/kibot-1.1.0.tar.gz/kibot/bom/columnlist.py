# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# Copyright (c) 2016-2020 Oliver Henry Walters (@SchrodingersGat)
# License: MIT
# Project: KiBot (formerly KiPlot)
# Adapted from: https://github.com/SchrodingersGat/KiBoM
"""
ColumnList

This is a class to hold the names of the fields and columns of the BoM.
In KiBoM it has some logic, here is just a collection of constants.
We also declare the BoMError here.
"""


class BoMError(Exception):
    pass


class ColumnList:
    """ A list of columns for the BoM """
    # Default columns (immutable)
    COL_REFERENCE = 'References'
    COL_REFERENCE_L = COL_REFERENCE.lower()
    COL_DESCRIPTION = 'Description'
    COL_DESCRIPTION_L = COL_DESCRIPTION.lower()
    COL_VALUE = 'Value'
    COL_VALUE_L = COL_VALUE.lower()
    COL_FP = 'Footprint'
    COL_FP_L = COL_FP.lower()
    COL_FP_LIB = 'Footprint Lib'
    COL_FP_LIB_L = COL_FP_LIB.lower()
    COL_FP_X = 'Footprint X'
    COL_FP_X_L = COL_FP_X.lower()
    COL_FP_Y = 'Footprint Y'
    COL_FP_Y_L = COL_FP_Y.lower()
    COL_FP_ROT = 'Footprint Rot'
    COL_FP_ROT_L = COL_FP_ROT.lower()
    COL_FP_SIDE = 'Footprint Side'
    COL_FP_SIDE_L = COL_FP_SIDE.lower()
    COL_FP_TYPE = 'Footprint Type'
    COL_FP_TYPE_L = COL_FP_TYPE.lower()
    COL_FP_FIT = 'Footprint Populate'
    COL_FP_FIT_L = COL_FP_FIT.lower()
    COL_FP_XS = 'Footprint X-Size'
    COL_FP_XS_L = COL_FP_XS.lower()
    COL_FP_YS = 'Footprint Y-Size'
    COL_FP_YS_L = COL_FP_YS.lower()
    COL_PART = 'Part'
    COL_PART_L = COL_PART.lower()
    COL_PART_LIB = 'Part Lib'
    COL_PART_LIB_L = COL_PART_LIB.lower()
    COL_DATASHEET = 'Datasheet'
    COL_DATASHEET_L = COL_DATASHEET.lower()
    COL_SHEETPATH = 'Sheetpath'
    COL_SHEETPATH_L = COL_SHEETPATH.lower()
    COL_ROW_NUMBER = 'Row'
    COL_ROW_NUMBER_L = COL_ROW_NUMBER.lower()
    COL_STATUS = 'Status'
    COL_STATUS_L = COL_STATUS.lower()

    # Default columns for groups
    COL_GRP_QUANTITY = 'Quantity Per PCB'
    COL_GRP_QUANTITY_L = COL_GRP_QUANTITY.lower()
    COL_GRP_BUILD_QUANTITY = 'Build Quantity'
    COL_GRP_BUILD_QUANTITY_L = COL_GRP_BUILD_QUANTITY.lower()
    COL_SOURCE_BOM = 'Source BoM'
    COL_SOURCE_BOM_L = COL_SOURCE_BOM.lower()

    # Generated columns
    COLUMNS_GEN_L = {
        COL_GRP_QUANTITY_L: 1,
        COL_GRP_BUILD_QUANTITY_L: 1,
        COL_ROW_NUMBER_L: 1,
        COL_STATUS_L: 1,
        COL_SOURCE_BOM_L: 1,
    }

    # Default columns
    COLUMNS_DEFAULT = [
        COL_ROW_NUMBER,
        COL_DESCRIPTION,
        COL_PART,
        COL_PART_LIB,
        COL_REFERENCE,
        COL_VALUE,
        COL_FP,
        COL_FP_LIB,
        COL_GRP_QUANTITY,
        COL_GRP_BUILD_QUANTITY,
        COL_STATUS,
        COL_DATASHEET,
        COL_SHEETPATH,
        COL_SOURCE_BOM,
    ]

    # Not included by default
    COLUMNS_EXTRA = [
        COL_FP_X,
        COL_FP_Y,
        COL_FP_ROT,
        COL_FP_SIDE,
        COL_FP_TYPE,
        COL_FP_FIT,
        COL_FP_XS,
        COL_FP_YS,
    ]

    # Default columns
    # These columns are 'immutable'
    COLUMNS_PROTECTED_L = {
        COL_REFERENCE_L[:-1],  # The column is References and the field Reference
        COL_REFERENCE_L,  # The column is References and the field Reference
        COL_GRP_QUANTITY_L,
        COL_VALUE_L,
        COL_PART_L,
        COL_PART_LIB_L,
        # COL_DESCRIPTION_L: 1,
        COL_DATASHEET_L,
        COL_SHEETPATH_L,
        COL_FP_L,
        COL_FP_X_L,
        COL_FP_Y_L,
        COL_FP_ROT_L,
        COL_FP_SIDE_L,
        COL_FP_TYPE_L,
        COL_FP_FIT_L,
        COL_FP_XS_L,
        COL_FP_YS_L,
        COL_FP_LIB_L
    }

    # Default fields used to group components
    DEFAULT_GROUPING = [
        COL_PART_L,
        COL_PART_LIB_L,
        COL_VALUE_L,
        COL_FP_L,
        COL_FP_LIB_L,
    ]
