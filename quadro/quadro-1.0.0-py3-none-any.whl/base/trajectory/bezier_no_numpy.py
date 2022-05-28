#VELOCITY AND ACELERATION PROFILE HAS NOT BEEN ADDED

def bezier(m,number_of_times=None):
	x,y,z=[],[],[]
#	v,a=[],[]
	if number_of_times==None:
		number_of_times=50
	i=0
	while i<4:
		x0,x1,x2,x3=m[0]
		y0,y1,y2,y3=m[1]
		z0,z1,z2,z3=m[2]
		
		for t in range(0,number_of_times):
			t=t/number_of_times
			x.append((1-t)**3*x0+3*(1-t)**2*t*x1+3*(1-t)*t**2*x2+t**3*x3)
			y.append((1-t)**3*y0+3*(1-t)**2*t*y1+3*(1-t)*t**2*y2+t**3*y3)
			z.append((1-t)**3*z0+3*(1-t)**2*t*z1+3*(1-t)*t**2*z2+t**3*z3)
#			v.append(6*t(1-t))
#			a.append(6-12*t)
		i+=4
	return x,y,z

def rise_phase(h,s,n=None):
	s=s/2.0
	first_four_points=[[0,-s/2,-s/2,s],[0,0,0,0],[0,h/2,h,h]]
	x1,y1,z1=bezier(first_four_points,number_of_times=n)
	return x1,y1,z1


def land_phase(h,s,n=None):
	x,y,z=[],[],[]
	s=s/2.0
	second_four_points=[[s+0,s+1.5*s,s+1.5*s,s+s],[0,0,0,0],[h,h,h/2,0]]
	x2,y2,z2=bezier(second_four_points,number_of_times=n)
	return x2,y2,z2


def fall_phase(h,s,n=None):
	x,y,z=[],[],[]
	s=s/2.0
	third_four_points=[[s+s,s+s*0.8,s+0,s+0],[0,0,0,0],[0,-h/5,-h/5,-h/5]]
	x3,y3,z3=bezier(third_four_points,number_of_times=n)
	return x3,y3,z3


def draw_phase(h,s,n=None):
	x,y,z=[],[],[]
	s=s/2.0
	fourth_four_points=[[s,s,s*0.2,0],[0,0,0,0],[-h/5,-h/5,-h/5,0]]
	x4,y4,z4=bezier(fourth_four_points,number_of_times=n)
	return x4,y4,z4

def bezier_deg(m,number_of_times=None):
	t1,t2,t3,t4,t5,t6=m
#	v,a=[],[]
	x,y,z=[],[],[]
	v=[]
	if number_of_times==None:
		number_of_times=50
	for t in range(0,number_of_times):
		t=t/number_of_times
		x.append(t1+(t4-t1)*(3*t**2-2*t**3))#(1-t)**3*x0+3*(1-t)**2*t*x1+3*(1-t)*t**2*x2+t**3*x3)
		y.append(t2+(t5-t2)*(3*t**2-2*t**3))#(1-t)**3*y0+3*(1-t)**2*t*y1+3*(1-t)*t**2*y2+t**3*y3)
		z.append(t3+(t6-t3)*(3*t**2-2*t**3))#(1-t)**3*z0+3*(1-t)**2*t*z1+3*(1-t)*t**2*z2+t**3*z3)
		v.append(6*t*(1-t))
#		a.append(6-12*t)
	return x,y,z,v
