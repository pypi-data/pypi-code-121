import math,time
from math import cos,sin,tan,atan,asin,acos,pi,sqrt


def forward(t1,t2,t3):
	p=pi/180
	t1,t2,t3=t1*p,t2*p,t3*p
	c1,s1,c2,s2,c3,s3=cos(t1),sin(t1),cos(t2),sin(t2),cos(t3),sin(t3)
	c23,s23=cos(t2+t3),sin(t2+t3)
	l1,l2,l3,l4=58,105,250,250
	xyc=c23*l4+c2*l3
	x,y,z=c1*xyc+s1*l2,-s1*xyc+c1*l2,s23*l4+s2*l3+l1
#	print('theta,xyz:',t1/p,t2/p,t3/p,x,y,z)
	return x,y,z


def inverse(x,y,z,print_it=None):

	l1,l2,l3,l4=58,105,250,250
	rp,p=180/pi,pi/180
	tt1,tt2,tt3=[],[],[]
	val=(x**2+y**2+(z-l1)**2-l2**2-2*l3**2)/(2*l4**2)
	if print_it!=None:
		print('val:',val)
		print('x,y,z,l1,l2,l3,l4:',x,y,z,l1,l2,l3,l4)
	if val>1:
		theta3=acos(1)*rp#round(val))*rp
	else:
		theta3=acos(val)*rp

	tt3.append(-theta3)
	tt3.append(theta3)
	if print_it!=None:
		print("tt3:",tt3)
	for theta3 in tt3:
		c3,s3=cos(theta3*p),sin(theta3*p)
		gamma=atan(s3/(c3+1))*rp
		val=(z-l1)*cos(gamma*p)/(l3*(c3+1))

		if val>1 or val<-1:
			theta2=asin(round(val))*rp-gamma
		else:
			theta2=asin(val)*rp - gamma
		if theta2<-90:
			theta2=theta2+180
		elif theta2>90:
			theta2=180-theta2
		if theta2 not in tt2:
			tt2.append(theta2)
			tt2.append(-theta2)

	fx,fy,fz=[],[],[]
	final=[]
	miss_final=[]
	if print_it!=None:
		print("tt2:",tt2)
	for i in tt3:
		for j in tt2:
			p=pi/180
			s23,s2=sin((i+j)*p),sin(j*p)
			c23,c2=cos((i+j)*p),cos(j*p)
			xyc=c23*l4+c2*l3
			z_check=s23*l4+s2*l3+l1

			if round(z)==round(z_check) or round(x)==round(xyc):

				n_t1=0
				n_beta=atan(xyc/l2)*rp
				n_theta1=atan(x/y)*rp-n_beta

				if n_theta1<-90:
					n_theta1=n_theta1+180
				elif n_theta1>90:
					n_theta1=180-n_theta1
				if n_theta1 not in tt1:
					tt1.append(n_theta1)
					miss_final.append([int(n_theta1*1000)/1000,int(1000*j)/1000,int(1000*i)/1000])
				x1,y1,z1=forward(n_theta1,j,i)
				x2,y2,z2=forward(-n_theta1,j,i)
			

				if (round(x)==round(x1)) and (round(y)==round(y1)) and ((round(z)==round(z1)) or int(z)==int(z1)):
					'''
					if int(n_theta1*100)/100 not in fx:
						fx.append(int(n_theta1*100)/100)
					if int(100*j)/100 not in fy:
						fy.append(int(j*100)/100)
					if int(i*100)/100 not in fz:
						fz.append(int(i*100)/100)
					'''
					final.append([int(n_theta1*1000)/1000,int(1000*j)/1000,int(1000*i)/1000])

				elif ((round(x)==round(x2)) and (round(y)==round(y2)) and (round(z)==round(z2))):
					'''
					if int(-n_theta1*100)/100 not in fx:
						fx.append(int(-n_theta1*100)/100)
					if int(100*j)/100 not in fy:
						fy.append(int(j*100)/100)
					if int(i*100)/100 not in fz:
						fz.append(int(i*100)/100)
					'''
					final.append([int(-n_theta1*1000)/1000,int(1000*j)/1000,int(1000*i)/1000])
				else:
					continue
	if print_it!=None:
		print("tt1:", tt1)
	if len(final)==0:
		print("missed")
		return miss_final
	else:
		return final


