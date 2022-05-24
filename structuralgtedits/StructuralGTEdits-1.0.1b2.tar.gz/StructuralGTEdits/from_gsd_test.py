from StructuralGT import network, base

"""
#Write network
N = network.ResistiveNetwork('TestData/AgNWN_iso/Single')
N.binarize()
N.stack_to_gsd(crop=[0,500,0,500])
N.potential_distribution(0,[0,20],[480,500])
N.Node_labelling(N.P,'P','wL.gsd')

M = base.from_gsd('TestData/AgNWN_iso/Single/Binarized/wL.gsd')

print(M.Gr.vs[5])
"""
