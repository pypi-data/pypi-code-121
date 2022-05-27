import types
from . import ElasticStrainModifier, DislocationAnalysisModifier

# Copy enum list.
ElasticStrainModifier.Lattice = types.SimpleNamespace()
ElasticStrainModifier.Lattice.Other = DislocationAnalysisModifier.Lattice.Other
ElasticStrainModifier.Lattice.FCC = DislocationAnalysisModifier.Lattice.FCC
ElasticStrainModifier.Lattice.HCP = DislocationAnalysisModifier.Lattice.HCP
ElasticStrainModifier.Lattice.BCC = DislocationAnalysisModifier.Lattice.BCC
ElasticStrainModifier.Lattice.CubicDiamond = DislocationAnalysisModifier.Lattice.CubicDiamond
ElasticStrainModifier.Lattice.HexagonalDiamond = DislocationAnalysisModifier.Lattice.HexagonalDiamond