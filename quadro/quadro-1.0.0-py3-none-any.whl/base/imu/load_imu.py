from base.auxillary.rpy import rotx,rot
from base.kinematics.kinematics import forward,inverse
def imu(s1,s2,s3,s4,rpy):
	roll,pitch,yaw=rpy
	pitch=-pitch
	center_to_leg2=rotx(roll,pitch,yaw,216.5,100,0)
	center_to_leg1=rotx(roll,pitch,yaw,216.5,-100,0)
	center_to_leg3=rotx(roll,pitch,yaw,-216.5,-100,0)
	center_to_leg4=rotx(roll,pitch,yaw,-216.5,100,0)
	s1=forward(s1[0],s1[1],s1[2])
	s2=forward(s2[0],s2[1],s2[2])
	s3=forward(s3[0],s3[1],s3[2])
	s4=forward(s4[0],s4[1],s4[2])
	
	print('\nlegs:',center_to_leg1,center_to_leg2,center_to_leg3,center_to_leg4)
	print('new_legs:',rot(roll,pitch,yaw,216.5,-100,0),rot(roll,pitch,yaw,216.5,100,0),
rot(roll,pitch,yaw,-216.5,-100,0),rot(roll,pitch,yaw,-216.5,100,0))
	print('s:',s1,s2,s3,s4)
	input('stopped')
	print('\nverify:',(s1[0]+center_to_leg2[2],s1[1]+center_to_leg2[1]-100,s1[2]+center_to_leg2[0]-216.5),(s2[0]+center_to_leg1[2],s2[1]+center_to_leg1[1]+100,s2[2]+center_to_leg1[0]-216.5),
(s3[0]+center_to_leg4[2],s3[1]+center_to_leg4[1]-100,s3[2]+center_to_leg4[0]+216.5),(s4[0]+center_to_leg3[2],s4[1]+center_to_leg3[1]+100,s4[2]+center_to_leg3[0]+216.5))

	print('\nverify new:',(s1[0]+center_to_leg1[2],s1[1]+center_to_leg1[1]+100,s1[2]+center_to_leg1[0]-216.5),(s2[0]+center_to_leg2[2],s2[1]+center_to_leg2[1]-100,s2[2]+center_to_leg2[0]-216.5),
(s3[0]+center_to_leg3[2],s3[1]+center_to_leg3[1]+100,s3[2]+center_to_leg3[0]+216.5),(s4[0]+center_to_leg4[2],s4[1]+center_to_leg4[1]-100,s4[2]+center_to_leg4[0]+216.5))
	
	s1=inverse(s1[0]+center_to_leg1[2],s1[1]+center_to_leg1[1]+100,s1[2]+center_to_leg1[0]-216.5)
	s2=inverse(s2[0]+center_to_leg2[2],s2[1]+center_to_leg2[1]-100,s2[2]+center_to_leg2[0]-216.5)
	s3=inverse(s3[0]+center_to_leg3[2],s3[1]+center_to_leg3[1]+100,s3[2]+center_to_leg3[0]+216.5)
	s4=inverse(s4[0]+center_to_leg4[2],s4[1]+center_to_leg4[1]-100,s4[2]+center_to_leg4[0]+216.5)
#	print('\ns:',s1,s2,s3,s4)
	for t1,t2,t3 in s1:
		if t3>t2:
			s1=t1,t2,t3
	for t1,t2,t3 in s2:
		if t3>t2:
			s2=t1,t2,t3
	for t1,t2,t3 in s3:
		if t3>t2:
			s3=t1,t2,t3
	for t1,t2,t3 in s4:
		if t3>t2:
			s4=t1,t2,t3
	return s1,s2,s3,s4


#print(imu([0,-40,80],[0,-40,80],[0,-40,80],[0,-40,80],[30,0,0]))

