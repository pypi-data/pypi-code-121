from __future__ import absolute_import, division, print_function, unicode_literals

from dune.common.checkconfiguration import assertHave, ConfigurationError
from dune.generator import Constructor, Method

from .blossoms import blossomDomain
from .voronoi import voronoiDomain

def polygonGrid(domain, ctype="double", dualGrid=False ):
    from ..grid.grid_generator import module, getDimgrid

    typeName = "Dune::PolygonGrid< " + ctype + " >"
    includes = ["dune/polygongrid/grid.hh", "dune/polygongrid/dgf.hh"]

    dualGridMethod = Method('dualGrid', '''[]( DuneType &self ) { return self.dualGrid(); }''' )
    cachingStorage = Method('cachingStorage', '''[]( DuneType &self ) { return false; }''' )
    gridModule = module(includes, typeName, dualGridMethod, cachingStorage)

    grid = gridModule.LeafGrid(gridModule.reader(domain))
    if dualGrid:
        grid = grid.hierarchicalGrid.dualGrid()
        grid = grid.leafView
    return grid


registry = {}
registry["grid"] = {
        "Polygon": polygonGrid
    }


if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
