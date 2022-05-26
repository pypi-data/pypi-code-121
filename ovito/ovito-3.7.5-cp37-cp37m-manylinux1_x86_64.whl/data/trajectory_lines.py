from . import TrajectoryLines, PropertyContainer

TrajectoryLines.positions  = PropertyContainer._create_property_accessor("Position", "The :py:class:`~ovito.data.Property` data array storing the XYZ coordinates of the line vertices.")
TrajectoryLines.positions_ = PropertyContainer._create_property_accessor("Position_")

TrajectoryLines.time_stamps  = PropertyContainer._create_property_accessor("Time", "The :py:class:`~ovito.data.Property` data array storing the time stamps of the line vertices.")
TrajectoryLines.time_stamps_ = PropertyContainer._create_property_accessor("Time_")

TrajectoryLines.particle_ids  = PropertyContainer._create_property_accessor("Particle Identifier", "The :py:class:`~ovito.data.Property` data array storing the particle IDs of the line vertices.")
TrajectoryLines.particle_ids_ = PropertyContainer._create_property_accessor("Particle Identifier_")