depends = ('ITKPyBase', 'ITKIOMeshBase', 'ITKCommon', )
templates = (  ('SWCMeshIOEnums', 'itk::SWCMeshIOEnums', 'itkSWCMeshIOEnums', False),
  ('SWCMeshIO', 'itk::SWCMeshIO', 'itkSWCMeshIO', True),
  ('SWCMeshIOFactory', 'itk::SWCMeshIOFactory', 'itkSWCMeshIOFactory', True),
)
factories = (("MeshIO","SWC"),)
