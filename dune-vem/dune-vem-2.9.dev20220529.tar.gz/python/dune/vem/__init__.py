# from dune.vem._vem import *
from dune.vem.vem import *
from .voronoi import voronoiCells
# from dune.vem.voronoi import voronoiCells
registry = dict()
registry["space"] = {
        "bbdg"   : bbdgSpace,
        "vem"    : vemSpace
    }
registry["scheme"] = {
         "vem"    : vemScheme,
         "bbdg"   : bbdgScheme
    }
registry["grid"] = {
        "agglomerate" : polyGrid
   }
