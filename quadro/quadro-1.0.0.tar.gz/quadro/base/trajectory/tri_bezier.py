#VELOCITY AND ACELERATION PROFILE HAS NOT BEEN ADDED
def tri_bezier(m,number_of_times=None):
	x,y,z=[],[],[]
	if number_of_times==None:
		number_of_times=50
	x0,x1=m[0]
	y0,y1=m[1]
	z0,z1=m[2]
	for t in range(1,number_of_times+1):
		t=t/number_of_times
		x.append((x1-x0)*t)
		y.append((y1-y0)*t)
		z.append((z1-z0)*t)
	return x,y,z

def rise(h,s,ss,n=None):
	x,y,z=[],[],[]
	two_point=[[0,s],[0,ss],[0,h]]
	x1,y1,z1=tri_bezier(two_point,number_of_times=n)
	return x1,y1,z1

def drop(h,s,ss,n=None):
	x,y,z=[],[],[]
	two_point=[[s,s],[ss,ss],[h,0]]
	x2,y2,z2=tri_bezier(two_point,number_of_times=n)
	return x2,y2,z2

def fall(h,s,ss,n=None):
	x,y,z=[],[],[]
	two_point=[[s,0],[ss,0],[0,-h*0.2]]
	x3,y3,z3=tri_bezier(two_point,number_of_times=n)
	return x3,y3,z3

def vel(number_of_times=None):
	if number_of_times==None:
		number_of_times=50
	v=[]
	for t in range(0,number_of_times):
		t=t/number_of_times
		v.append(6*t*(1-t))
	return v
