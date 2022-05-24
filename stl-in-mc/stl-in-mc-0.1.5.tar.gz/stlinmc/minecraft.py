"""
# minecraft.py
# this module interacts with a Raspberry Juice server
"""

from multiprocessing import cpu_count

from joblib import Parallel, delayed
from mcpi import block
from mcpi.connection import Connection, RequestError
from mcpi.minecraft import Minecraft


def build_voxels(voxels, server_ip, server_port=4711, parallel=False):
    """sends build commands for voxels on a server

    Args:
        voxels (np.nDArray[int8]): a set of voxels in a 3D array,
                                   0 and 1 indicate air and block respectively
        server_ip (str): ip of minecraft server running raspberry juice (URL or IPv4)
        server_port (int, optional): server port. defaults to 4711.
    """

    # establish connection to server and get player position
    conn = Connection(server_ip, server_port)
    mc = Minecraft(conn)
    try:
        x, y, z = mc.player.getTilePos()
    except RequestError:
        print("No valid player to reference, using (0,0,0)")
        x, y, z = 0, 0, 0

    # set blocks for each voxel
    if not parallel:
        for layer_index, layer in enumerate(voxels):
            print(f"Sending layer {layer_index+1}/{len(voxels)}... ", end='')
            build_layer(mc, layer, layer_index, x, y, z)
            print("Sent!")
    else:
        num_cores = cpu_count()
        Parallel(
            n_jobs=min(num_cores, 4),
            prefer="threads"
        )(
            delayed(build_layer)
            (mc, layer, layer_index, x, y, z) for layer_index, layer in enumerate(voxels)
        )


def build_layer(mc, layer, layer_height, x, y, z):
    for row_index, row in enumerate(layer):
        for column_index, column in enumerate(row):
            xc = x + column_index
            yc = y + layer_height
            zc = z + row_index
            if column == 1:
                mc.setBlock(xc, yc, zc, block.COBBLESTONE.id)
            elif column == 0:
                mc.setBlock(xc, yc, zc, block.AIR.id)
