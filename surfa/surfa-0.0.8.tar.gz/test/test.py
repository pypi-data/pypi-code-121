import numpy as np
import surfa as sa
import surfa.image
# import freesurfer as fs


# surface = fs.Surface.read('/Applications/freesurfer/dev/subjects/bert/surf/lh.white')
# image = fs.Volume.read('/Applications/freesurfer/dev/subjects/bert/mri/orig.mgz')

# affine = sa.Affine(lta.matrix, source=source, target=target, transform_space='image')



# # image
# image_moved = image.transform(affine.matrix)
# image_moved.affine = 

# # surface
# affine_surf = affine.convert(space='surface')
# surface_moved = surface.copy()
# surface_moved.vertices = affine_surf.transform(surface_moved.vertices)
# surface_moved.geom = affine.target

# # ...



# aff_sv = sa.Affine(surf2vox, transform_space='surface-to-image')

# aff_sw = aff @ aff_sv

# print(aff_sw.transform_space.name)
# print(np.allclose(aff_sw.matrix, geom.surf2ras().matrix))


geom = sa.ImageGeometry((64, 64), rotation='LIA')
print(geom.rotation)
print(geom.space_transform('image', 'world')((0, 0, 0)))

geom = sa.ImageGeometry((64, 64, 64), rotation='LIA')
print(geom.rotation)
print(geom.space_transform('image', 'world')((0, 0, 0)))



# img = surfa.image.Volume(np.random.randn(64, 64, 64))
# trf = img.geom.space_transform('world', 'surface').inverse()
# print(trf.det())
