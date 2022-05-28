from mpl_toolkits import mplot3d

import numpy as np
import matplotlib.pyplot as plt
'''
x=np.array([1,2,3,4,5])
y=np.array([0,-1,-2,-3,-4])
z=np.array([[5,4,3,2,1],[3,6,9,1,0]])
fig = plt.figure()
ax = plt.axes(projection="3d")
ax.plot_wireframe(x,y,z)
plt.show()
'''
def bezier_vis_3d(x,y,z):
	z=np.array([z,z])
	fig = plt.figure()
	ax = plt.axes(projection="3d")
	ax.plot_wireframe(x,y,z)
	plt.show()
