"""
This module contains all modifiers available in OVITO. See the :ref:`introduction <modifiers_overview>` to learn more
about modifiers and their role in the data pipeline system. The following table lists the Python names of all modifier types that can be instantiated.
Please consult the :ref:`OVITO user manual <manual:particles.modifiers>` for a more in-depth description of what
each of these modifiers does.

============================================== =========================================
Python class name                              User interface name
============================================== =========================================
:py:class:`AcklandJonesModifier`               :guilabel:`Ackland-Jones analysis`
:py:class:`AffineTransformationModifier`       :guilabel:`Affine transformation`
:py:class:`AmbientOcclusionModifier`           :guilabel:`Ambient occlusion`
:py:class:`AssignColorModifier`                :guilabel:`Assign color`
:py:class:`AtomicStrainModifier`               :guilabel:`Atomic strain`
:py:class:`BondAnalysisModifier`               :guilabel:`Bond analysis`
:py:class:`CalculateDisplacementsModifier`     :guilabel:`Displacement vectors`
:py:class:`CentroSymmetryModifier`             :guilabel:`Centrosymmetry parameter`
:py:class:`ChillPlusModifier`                  :guilabel:`Chill+`
:py:class:`ClearSelectionModifier`             :guilabel:`Clear selection`
:py:class:`ClusterAnalysisModifier`            :guilabel:`Cluster analysis`
:py:class:`ColorByTypeModifier`                :guilabel:`Color by type`
:py:class:`ColorCodingModifier`                :guilabel:`Color coding`
:py:class:`CombineDatasetsModifier`            :guilabel:`Combine datasets`
:py:class:`CommonNeighborAnalysisModifier`     :guilabel:`Common neighbor analysis`
:py:class:`ComputePropertyModifier`            :guilabel:`Compute property`
:py:class:`ConstructSurfaceModifier`           :guilabel:`Construct surface mesh`
:py:class:`CoordinationAnalysisModifier`       :guilabel:`Coordination analysis`
:py:class:`CoordinationPolyhedraModifier`      :guilabel:`Coordination polyhedra`
:py:class:`CreateBondsModifier`                :guilabel:`Create bonds`
:py:class:`CreateIsosurfaceModifier`           :guilabel:`Create isosurface`
:py:class:`DeleteSelectedModifier`             :guilabel:`Delete selected`
:py:class:`DislocationAnalysisModifier`        :guilabel:`Dislocation analysis (DXA)`
:py:class:`ElasticStrainModifier`              :guilabel:`Elastic strain calculation`
:py:class:`ExpandSelectionModifier`            :guilabel:`Expand selection`
:py:class:`ExpressionSelectionModifier`        :guilabel:`Expression selection`
:py:class:`FreezePropertyModifier`             :guilabel:`Freeze property`
:py:class:`GenerateTrajectoryLinesModifier`    :guilabel:`Generate trajectory lines`
:py:class:`GrainSegmentationModifier`          :guilabel:`Grain segmentation`
:py:class:`HistogramModifier`                  :guilabel:`Histogram`
:py:class:`IdentifyDiamondModifier`            :guilabel:`Identify diamond structure`
:py:class:`InvertSelectionModifier`            :guilabel:`Invert selection`
:py:class:`LoadTrajectoryModifier`             :guilabel:`Load trajectory`
:py:class:`PolyhedralTemplateMatchingModifier` :guilabel:`Polyhedral template matching`
:py:class:`PythonScriptModifier`               :guilabel:`Python script`
:py:class:`ReplicateModifier`                  :guilabel:`Replicate`
:py:class:`SelectTypeModifier`                 :guilabel:`Select type`
:py:class:`SliceModifier`                      :guilabel:`Slice`
:py:class:`SmoothTrajectoryModifier`           :guilabel:`Smooth trajectory`
:py:class:`SpatialBinningModifier`             :guilabel:`Spatial binning`
:py:class:`SpatialCorrelationFunctionModifier` :guilabel:`Spatial correlation function`
:py:class:`TimeAveragingModifier`              :guilabel:`Time averaging`
:py:class:`TimeSeriesModifier`                 :guilabel:`Time series`
:py:class:`UnwrapTrajectoriesModifier`         :guilabel:`Unwrap trajectories`
:py:class:`VoronoiAnalysisModifier`            :guilabel:`Voronoi analysis`
:py:class:`VoroTopModifier`                    :guilabel:`VoroTop analysis`
:py:class:`WignerSeitzAnalysisModifier`        :guilabel:`Wigner-Seitz defect analysis`
:py:class:`WrapPeriodicImagesModifier`         :guilabel:`Wrap at periodic boundaries`
============================================== =========================================

*Note that some modifiers of the graphical version of OVITO are missing from this list and are not accessible from Python scripts.
That is because they perform simple operations that can be accomplished equally well or even easier using other means in Python.*

"""

__all__ = ['PythonScriptModifier']
