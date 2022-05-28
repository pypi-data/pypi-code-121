import numpy as np
from dplot import bezier_vis_3d
def bezier(m):
	m1=[]
	x,y,z=[],[],[]
	i=4
	while i<m.shape[1]+1:
		x0,x1,x2,x3=m[0][i-4:i]
		y0,y1,y2,y3=m[1][i-4:i]
		z0,z1,z2,z3=m[2][i-4:i]
		
		for t in range(0,100):
			t=t/100
			x.append((1-t)**3*x0+3*(1-t)**2*t*x1+3*(1-t)*t**2*x2+t**3*x3)
			y.append((1-t)**3*y0+3*(1-t)**2*t*y1+3*(1-t)*t**2*y2+t**3*y3)
			z.append((1-t)**3*z0+3*(1-t)**2*t*z1+3*(1-t)*t**2*z2+t**3*z3)
		i+=4
	x=np.array(x)
	y=np.array(y)
	z=np.array(z)
	return x,y,z

m=np.array([[0,5,10,15,15,20,25,30,30,35,40,45],[0,2,2,0,0,-2,-2,0,0,2,-2,0],[0,8,9,10,10,7,7,0,0,9,6,0]])
x,y,z=bezier(m)

bezier_vis_3d(x,y,z)
	
