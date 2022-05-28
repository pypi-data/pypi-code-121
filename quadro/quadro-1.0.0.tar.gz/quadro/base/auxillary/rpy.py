import numpy as np
from math import cos,sin,pi

def rotx(d,e,f,x,y,z):#roll,pitch,yaw
	p=pi/180
	d,e,f=d*p,e*p,f*p
#	return np.array([[1,0,0],[0,cos(d*p),sin(d*p)],[0,-sin(d*p),cos(d*p)]])@np.array([[cos(e*p),0,-sin(e*p)],[0,1,0],[sin(e*p),0,cos(e*p)]])@np.array([[cos(f*p),sin(f*p),0],[-sin(f*p),cos(f*p),0],[0,0,1]])@np.array([[x],[y],[z]])
	return [cos(e)*cos(f)*x+cos(e)*sin(f)*y-sin(e)*z,(-cos(d)*sin(f)+sin(d)*sin(e)*cos(f))*x+(cos(d)*cos(f)+sin(d)*sin(e)*sin(f))*y+sin(d)*cos(e)*z,(sin(d)*sin(f)+cos(d)*sin(e)*cos(f))*x+(-sin(d)*cos(f)+cos(d)*sin(e)*sin(f))*y+cos(d)*cos(e)*z]

def roll(r):
	p=pi/180
	return np.array([[1,0,0],[0,cos(r*p),-sin(r*p)],[0,sin(r*p),cos(r*p)]])

def pitch(r):
	p=pi/180
	return np.array([[cos(r*p),0,sin(r*p)],[0,1,0],[-sin(r*p),0,cos(r*p)]])

def yaw(r):
	p=pi/180
	return np.array([[cos(r*p),-sin(r*p),0],[sin(r*p),cos(r*p),0],[0,0,1]])

def rot(r1,r2,r3,l1,l2,l3):
	'''
	r1,r2,r3-roll,pitch,yaw
	l1,l2,l3-from center to hip along x,y,z
	'''
	rotation_matrix=roll(r1)@pitch(r2)@yaw(r3)@np.array([[l1],[l2],[l3]])
	return rotation_matrix
