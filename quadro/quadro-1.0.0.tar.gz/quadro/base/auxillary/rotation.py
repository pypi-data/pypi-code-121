import numpy as np
import math

def rotationx(deg1,xyz,invert=False):
	x,y,z=xyz
	d=deg1*math.pi/180
	if invert==True:
		d=-d
	c,s=math.cos(d),math.sin(d)
	return np.array([[1,0,0],[0,c,s],[0,-s,c]])@np.array([[x],[y],[z]])

def rotationy(deg1,xyz,invert=False):
	x,y,z=xyz
	d=deg1*math.pi/180
	if invert==True:
		d=-d
	c,s=math.cos(d),math.sin(d)
	return np.array([[c,0,-s],[0,1,0],[s,0,c]])@np.array([[x],[y],[z]])

def rotationz(deg1,xyz,invert=False):
	x,y,z=xyz
	d=deg1*math.pi/180
	if invert==True:
		d=-d
	c,s=math.cos(d),math.sin(d)
	return np.array([[c,s,0],[-s,c,0],[0,0,1]])@np.array([[x],[y],[z]])
