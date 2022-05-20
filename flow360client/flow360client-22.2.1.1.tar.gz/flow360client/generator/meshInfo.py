import struct
import tempfile
import os
import json

import numpy

from .. import s3utils, Config, mesh

def readGLTF(meshId):
    try:
        from pygltflib import GLTF2
    except:
        print('Case Generator requires pygltflib. See\n' \
              'https://gitlab.com/dodgyville/pygltflib#install\n')
        raise
    client = s3utils.buildS3Client()
    userId = Config.user['userId']
    s3path = 'users/{0}/{1}/visualize/{1}.gltf'
    s3path = s3path.format(userId, meshId)
    with tempfile.TemporaryDirectory() as tmpDir:
        fname = os.path.join(tmpDir, 'tmp.gltf')
        client.download_file(Bucket=Config.MESH_BUCKET,
                             Filename=fname, Key=s3path)
        gltf = GLTF2().load(fname)
    return gltf

class MeshNotProcessedYetError(NotImplementedError):
    pass

def getBoundariesAndCoordinates(meshId):
    info = mesh.GetMeshInfo(meshId)
    if info['status'] != 'processed':
        print('Mesh not yet processed: ', info['status'])
        raise MeshNotProcessedYetError
    gltf = readGLTF(meshId)
    boundaries = []
    for boundary in gltf.meshes:
        vertices = []
        for primitive in boundary.primitives:
            # get the binary data for this boundary primitive from the buffer
            accessor = gltf.accessors[primitive.attributes.POSITION]
            bufferView = gltf.bufferViews[accessor.bufferView]
            buffer = gltf.buffers[bufferView.buffer]
            data = gltf.decode_data_uri(buffer.uri)
            # pull each vertex from the binary buffer and convert it into a tuple of python floats
            for i in range(accessor.count):
                # the location in the buffer of this vertex
                index = bufferView.byteOffset + accessor.byteOffset + i*12
                d = data[index:index+12]  # the vertex data
                v = struct.unpack("<fff", d)   # convert from base64 to three floats
                vertices.append(v)
        boundaries.append(numpy.array(vertices))
    boundaries = dict(zip(info['boundaries'], boundaries))
    noSlipWalls = {}
    params = json.loads(info['meshParams'])
    for name in params['boundaries']['noSlipWalls']:
        name = str(name)
        noSlipWalls[name] = boundaries[name]
        del boundaries[name]
    slidingInterfaces = params['slidingInterfaces'] if 'slidingInterfaces' in params else []
    return noSlipWalls, boundaries, slidingInterfaces

def displayWallBoundaries(walls):
    try:
        import pylab
    except ImportError:
        print('matplotlib not available. Skipping mesh visualization.')
        return
    for name, coords in walls.items():
        pylab.subplot(2,2,1)
        pylab.plot(coords[:,0], coords[:,2], '.', markersize=1)
        pylab.axis('scaled')
        pylab.subplot(2,2,2)
        pylab.plot(coords[:,1], coords[:,2], '.', markersize=1)
        pylab.axis('scaled')
        pylab.subplot(2,2,3)
        pylab.plot(coords[:,0], coords[:,1], '.', markersize=1)
        pylab.axis('scaled')
        box = tuple(list(coords.max(0) - coords.min(0)))
        print('{}: {:.4g} x {:.4g} x {:.4g}'.format(*(name,) + box))
    pylab.figlegend(list(walls.keys()), loc='lower right')

