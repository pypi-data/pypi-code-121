import types
from . import GrainSegmentationModifier, PolyhedralTemplateMatchingModifier

# Copy enum list.
GrainSegmentationModifier.Type = types.SimpleNamespace()
GrainSegmentationModifier.Type.OTHER = PolyhedralTemplateMatchingModifier.Type.OTHER
GrainSegmentationModifier.Type.FCC = PolyhedralTemplateMatchingModifier.Type.FCC
GrainSegmentationModifier.Type.HCP = PolyhedralTemplateMatchingModifier.Type.HCP
GrainSegmentationModifier.Type.BCC = PolyhedralTemplateMatchingModifier.Type.BCC
GrainSegmentationModifier.Type.ICO = PolyhedralTemplateMatchingModifier.Type.ICO
GrainSegmentationModifier.Type.SC = PolyhedralTemplateMatchingModifier.Type.SC
GrainSegmentationModifier.Type.CUBIC_DIAMOND = PolyhedralTemplateMatchingModifier.Type.CUBIC_DIAMOND
GrainSegmentationModifier.Type.HEX_DIAMOND = PolyhedralTemplateMatchingModifier.Type.HEX_DIAMOND
GrainSegmentationModifier.Type.GRAPHENE = PolyhedralTemplateMatchingModifier.Type.GRAPHENE