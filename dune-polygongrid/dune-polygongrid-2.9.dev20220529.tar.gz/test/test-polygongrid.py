from dune.grid import cartesianDomain
from dune.polygongrid import polygonGrid

grid = polygonGrid(cartesianDomain([0, 0], [1, 1], [4, 4]))
grid.writeVTK('test-polygongrid-cartesian')
