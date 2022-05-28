from test_no_numpy import *

f=open('./deepl_kin.csv','w')
f.write('t1,t2,t3,x,y,z\n')
f1=open('./deepl_kin.txt','w')
xmin,xmax,ymin,ymax,zmin,zmax=0,0,0,0,0,0
for i in range(-90,91):
	for j in range(-90,91):
		for k in range(-90,91):
			z,y,x=newrot(i,j,k)
			if x>xmax:
				xmax=x
			elif x<xmin:
				xmin=x
			if y>ymax:
				ymax=y
			elif y<ymin:
				ymin=y
			if z>zmax:
				zmax=z
			elif z<zmin:
				zmin=z
			f.write('{},{},{},{},{},{}\n'.format(str(i),str(j),str(k),str(x),str(y),str(z)))


f1.write('xmax:{} ,xmin:{} \n'.format(str(xmax),str(xmin)))
f1.write('ymax:{} ,ymin:{} \n'.format(str(ymax),str(ymin)))
f1.write('zmax:{} ,zmin:{} \n'.format(str(zmax),str(zmin)))
