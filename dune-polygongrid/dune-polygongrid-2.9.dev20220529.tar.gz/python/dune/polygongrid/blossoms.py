import numpy
import dune.geometry

def blossomDomain(nx, ny):
    Nx, Ny = 3*nx+1, 3*ny+1
    x = numpy.repeat(numpy.linspace(0.0, 1.0, Nx)[numpy.newaxis, :], Ny, axis=0).flatten()
    y = numpy.repeat(numpy.linspace(0.0, 1.0, Ny)[:, numpy.newaxis], Nx, axis=1).flatten()
    vertices = numpy.stack((x, y), axis=-1)

    gt = dune.geometry.none(2)
    elements = []
    for j in range(0, 3*Nx*ny, 3*Nx):
        for k in range(j, j+3*nx, 3):
            elements += [
                    (gt, [k, k+1, k+2, k+Nx+2, k+Nx+1, k+Nx]),
                    (gt, [k+2, k+3, k+Nx+3, k+2*Nx+3, k+2*Nx+2, k+Nx+2]),
                    (gt, [k+Nx, k+Nx+1, k+2*Nx+1, k+3*Nx+1, k+3*Nx, k+2*Nx]),
                    (gt, [k+Nx+1, k+Nx+2, k+2*Nx+2, k+2*Nx+1]),
                    (gt, [k+2*Nx+1, k+2*Nx+2, k+2*Nx+3, k+3*Nx+3, k+3*Nx+2, k+3*Nx+1])
                ]

    return {"vertices": vertices, "elements": elements}
