# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.stdobj

# Load the C extension module.
import ovito.plugins.StdModPython

# Load class add-ons.
import ovito.modifiers.select_type_modifier

# Publish classes.
ovito.modifiers.__all__ += ['SliceModifier', 'AffineTransformationModifier',
            'ClearSelectionModifier', 'InvertSelectionModifier', 'ColorCodingModifier',
            'AssignColorModifier', 'DeleteSelectedModifier', 'SelectTypeModifier', 'HistogramModifier',
            'ScatterPlotModifier', 'ReplicateModifier', 'ExpressionSelectionModifier',
            'FreezePropertyModifier', 'ManualSelectionModifier', 'ComputePropertyModifier',
            'CombineDatasetsModifier', 'ColorByTypeModifier']
ovito.vis.__all__ += ['ColorLegendOverlay']
