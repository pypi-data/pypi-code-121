# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from .._constants import TransformerParams


class _OperatorNames:
    """Class storing operator names for various transformations."""

    CharGram = "CharGram"
    WordGram = "WordGram"
    Mean = "Mean"
    Mode = "Mode"
    Median = "Median"
    Constant = "Constant"
    ForwardFill = "FowardFill"
    Min = "Min"
    Max = "Max"
    DefaultValue = "DefaultValue"

    FULL_SET = {CharGram, WordGram, Mean, Mode, Median, Min, Max, Constant, DefaultValue}


class _TransformerOperatorMappings:
    Imputer = {
        TransformerParams.Imputer.Mean: _OperatorNames.Mean,
        TransformerParams.Imputer.Mode: _OperatorNames.Mode,
        TransformerParams.Imputer.Median: _OperatorNames.Median,
        TransformerParams.Imputer.Constant: _OperatorNames.Constant,
        TransformerParams.Imputer.Ffill: _OperatorNames.ForwardFill,
    }
    NimbusImputer = {
        TransformerParams.Nimbus.Mean: _OperatorNames.Mean,
        TransformerParams.Nimbus.Min: _OperatorNames.Min,
        TransformerParams.Nimbus.Max: _OperatorNames.Max,
        TransformerParams.Nimbus.DefaultValue: _OperatorNames.DefaultValue,
    }
