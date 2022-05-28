def bezier(m,x,y,z):

	
	i=0
	while i<4:
		x0,x1,x2,x3=m[0]
		y0,y1,y2,y3=m[1]
		z0,z1,z2,z3=m[2]
		
		for t in range(0,12):
			t=t/12
			x.append((1-t)**3*x0+3*(1-t)**2*t*x1+3*(1-t)*t**2*x2+t**3*x3)
			y.append((1-t)**3*y0+3*(1-t)**2*t*y1+3*(1-t)*t**2*y2+t**3*y3)
			z.append((1-t)**3*z0+3*(1-t)**2*t*z1+3*(1-t)*t**2*z2+t**3*z3)
		i+=4
	return x,y,z

def rise_phase_stair(h,s,sh):
	x,y,z=[],[],[]
	x.append(0)
	y.append(0)
	z.append(0)
	s=s/2.0
	first_four_points=[[0,-s/2,-s/2,s],[0,0,0,0],[0,h/2,h,h]]
	x1,y1,z1=bezier(first_four_points,x,y,z)
	return x1,y1,z1


def land_phase_stair(h,s,sh):
	x,y,z=[],[],[]
	s=s/2.0
	second_four_points=[[s+0,s+0.5*s,s+0.8*s,s+s],[0,0,0,0],[h,h,h,sh]]
	x2,y2,z2=bezier(second_four_points,x,y,z)
	return x2,y2,z2


def fall_phase_stair(h,s,sh):
	x,y,z=[],[],[]
	s=s/2.0
	third_four_points=[[s+s,s+s*0.8,s+0,s+0],[0,0,0,0],[0+sh,sh-sh/5,sh-sh/5,sh-sh/5]]
	x3,y3,z3=bezier(third_four_points,x,y,z)
	return x3,y3,z3


def draw_phase_stair(h,s,sh):
	x,y,z=[],[],[]
	s=s/2.0
	fourth_four_points=[[s,s,s*0.2,0],[0,0,0,0],[sh-sh/5,sh-sh/5,sh-sh/5,sh+0]]
	x4,y4,z4=bezier(fourth_four_points,x,y,z)
	return x4,y4,z4

