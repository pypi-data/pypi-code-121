import numpy as np
import matplotlib.pyplot as plt
import math
import mpmath
class G_xy:
    def __init__(self,v,G):
        '''
        function \n
        xy() ,xt() ,yt() ,vxt() ,vyt() ,listxt() ,listyt() ,listvxt() ,listvyt() \n
        กราฟ 1 \n
        V_initial = 5.7 ,g = 9.8\n
        กราฟ 2 \n
        V_initial1 = 5.7 ,g = 9.8 \n
        กราฟ 3 \n
        V_initial2 = 5.7 ,g = 9.8\n
        กราฟ 4 \n
        V_initial3 = 5.7 ,g = 9.8 \n
        ปรับเวลา \n
        plt.pause(t) ,t=0.01
        '''
        self.t = 0.1
        self.V_initial = v
        self.theta = (np.pi)/4
        self.v_x = self.V_initial * np.cos(self.theta)
        self.g = G
        self.lr_x = []
        self.lr_y = []

        
        self.V_initial1 = v
        self.theta1 = (np.pi)/4
        self.v_y1 = self.V_initial1 * np.sin(self.theta1)
        self.lr_x1 = []
        self.lr_y1 = []
        
        self.V_initial2 = v
        self.theta2 = (np.pi) / 4
        self.v_x2 = self.V_initial2 * np.cos(self.theta2)
        self.lr_x2 = []
        self.lr_y2 = []

        
        self.V_initial3 = v
        self.theta3 = (np.pi) / 4
        self.v_y3 = self.V_initial3 * np.sin(self.theta3)
        self.time3 = np.linspace(0, 100, 10000)
        self.lr_x3 = []
        self.lr_y3 = []
    def graph_g_xy(self):
        # plt.figure(figsize=[35,6],dpi=40)
        for t3 in self.time3:
            r_x = self.v_x * t3
            
            r_y1 = (self.v_y1 * t3) - 1/2 * self.g * (t3 ** 2) + 0.326
            
            r_y3 = (self.v_y3 * t3) - 1 / 2 * self.g * (t3 ** 2) + 0.326
            
            abv3 = self.v_y3 - self.g * t3
            if r_y3 >= 0:
                self.lr_x.append(t3)
                self.lr_y.append(r_x)
                
                self.lr_x1.append(t3)
                self.lr_y1.append(r_y1)
                
                self.lr_x2.append(t3)
                self.lr_y2.append(self.v_x2)
                
                self.lr_x3.append(t3)
                self.lr_y3.append(abv3)
            else:
                break
            plt.subplot(1, 4, 1)
            plt.title("xt")
            plt.plot(self.lr_x, self.lr_y, color='red')
            plt.subplot(1, 4, 2)
            plt.title("yt")
            plt.plot(self.lr_x1, self.lr_y1, color='green')
            
            plt.subplot(1, 4, 3)
            plt.title("vxt")
            plt.plot(self.lr_x2, self.lr_y2, color='blue')
            
            plt.subplot(1, 4, 4)
            plt.title("vyt")
            plt.plot(self.lr_x3, self.lr_y3, color='yellow')
            plt.pause(self.t)
        plt.show()
    def __str__(self):
        return 'x = G_xy()\nx.g = 9\nx.t = 0.01\nx.V_initial3 = 6\nx.xy()'


class graphyt:#todo เสร็จเเล้ว
    def __init__(self,v,G):
        self.time3 = np.linspace(0, 100, 10000)
        self.V_initial1 = v #!------ทำเป็นตัวเเปร
        self.theta1 = (np.pi)/4
        self.v_y1 = self.V_initial1 * np.sin(self.theta1)
        self.r_y1 = 0
        self.lr_x1 = []
        self.lr_y1 = []
        self.Lr_x1 = []
        self.Lr_y1 = []
        self.g = G
    def graph_yt(self):
        '''
        V_initial1 = 5.7 \n
        g = 9.8
        '''
        for t in self.time3:
            r_y = (self.v_y1 * t) - 1/2 * self.g * (t ** 2) + 0.326
            if r_y >= 0:
                self.lr_x1.append(t)
                self.lr_y1.append(r_y)
            else:
                break
            plt.plot(self.lr_x1, self.lr_y1, color='b')
            plt.pause(0.1)
        plt.show()
        
    def list_graph_yt(self):
        '''
        V_initial1 = 5.7 \n
        g = 9.8
        '''
        #!----------- เเก้
        self.lr_x1 = []
        self.lr_y1 = []
        #!-----------
        for t in self.time3:
            r_y = (self.v_y1 * t) - 1/2 * self.g * (t ** 2) + 0.326
            if r_y >= 0:
                self.lr_x1.append(t)
                self.lr_y1.append(r_y)
            else:
                break
        return self.lr_x1, self.lr_y1

class graphxt: #todo เสร็จเเล้ว
    def __init__(self,v,G):
        self.time3 = np.linspace(0, 100, 10000)
        self.V_initial = v #!---------ทำเป็นตัวเเปร
        self.theta = (np.pi)/4
        self.v_x = self.V_initial * np.cos(self.theta)
        self.v_y = self.V_initial * np.sin(self.theta)
        self.r_x = 0
        self.g = G
        self.lr_x = []
        self.lr_y = []
        self.Lr_x = []
        self.Lr_y = []
    def graph_xt(self):
        '''
        V_initial = 5.7 \n
        g = 9.8
        '''
        for t in self.time3:
            r_x = self.v_x * t #!--------------เเปะในกราฟ x
            r_y = (self.v_y * t) - 1/2 * self.g * (t ** 2) + 0.326
            if r_y >= 0:
                self.lr_x.append(t)
                self.lr_y.append(r_x)
            else:
                break
            plt.plot(self.lr_x, self.lr_y, color='b')
            plt.pause(0.1)
        plt.show()
    def list_graph_xt(self):
        '''
        V_initial = 5.7 \n
        g = 9.8
        '''
        for t in self.time3:
            r_x = self.v_x * t
            r_y = (self.v_y * t) - 1/2 * self.g * (t ** 2) + 0.326
            if r_y >= 0:
                self.lr_x.append(t)
                self.lr_y.append(r_x)
            else:
                break
        return self.lr_x, self.lr_y

class graphvxt: #todo เสร็จเเล้ว
    def __init__(self,v,G):
        self.V_initial2 = v #!---ทำเป็นตัวเเปร
        self.theta2 = (np.pi) / 4
        self.v_x2 = self.V_initial2 * np.cos(self.theta2)
        self.v_y2 = self.V_initial2 * np.sin(self.theta2)
        self.lr_x2 = []
        self.lr_y2 = []
        self.Lr_x2 = []
        self.Lr_y2 = []
        self.time3 = np.linspace(0, 100, 10000)
        self.g = G 
    def graph_vxt(self):
        '''
        V_initial2 = 5.7 \n
        g = 9.8
        '''
        for t in self.time3:
            r_y = (self.v_y2 * t) - 1 / 2 * self.g * (t ** 2) + 0.326
            if r_y >= 0:
                self.lr_x2.append(t)
                self.lr_y2.append(self.v_x2)
            else:
                break
            plt.plot(self.lr_x2, self.lr_y2, color='b')
            plt.pause(0.1)
        plt.show()
    def list_graph_vxt(self):
        '''
        V_initial2 = 5.7 \n
        g = 9.8
        '''
        for t in self.time3:
            r_y = (self.v_y2 * t) - 1 / 2 * self.g * (t ** 2) + 0.6
            if r_y >= 0:
                self.lr_x2.append(t)
                self.lr_y2.append(self.v_x2)
            else:
                break
        return self.lr_x2, self.lr_y2

class graphvyt:
    def __init__(self,v,G):
        self.V_initial3 = v
        self.theta3 = (np.pi) / 4
        self.v_y3 = self.V_initial3 * np.sin(self.theta3)
        self.time3 = np.linspace(0, 100, 10000)
        self.r_y3 = 0
        self.lr_x3 = []
        self.lr_y3 = []
        self.Lr_x3 = []
        self.Lr_y3 = []
        self.g = G
        self.R_Y = []
    def graph_vyt(self):
        '''
        V_initial3 = 5.7 \n
        g = 9.8
        '''
        for t in self.time3:
            r_y = (self.v_y3 * t) - 1 / 2 * self.g * (t ** 2) + 0.6
            abv = self.v_y3 - self.g * t
            if r_y >= 0:
                self.lr_x3.append(t)
                self.lr_y3.append(abv)
            else:
                break
            plt.plot(self.lr_x3, self.lr_y3, color='b')
            plt.pause(0.1)
        plt.show()
    def list_graph_vyt(self):
        '''
        V_initial3 = 5.7 \n
        g = 9.8
        '''
        for t in self.time3:
            r_y = (self.v_y3 * t) - 1 / 2 * self.g * (t ** 2) + 0.6
            abv = self.v_y3 - self.g * t
            if r_y >= 0:
                self.R_Y.append(r_y)
                self.lr_x3.append(t)
                self.lr_y3.append(abv)
            else:
                break
        return self.lr_x3, self.lr_y3,self.R_Y
    
class graphxy:
    def __init__(self,v,G):
        self.g = G
        self.V_initial4 = v #!----- เปลี่ยนตัวเเปร
        self.theta4 = (np.pi)/4
        self.v_x4 = self.V_initial4 * np.cos(self.theta4)
        self.v_y4 = self.V_initial4 * np.sin(self.theta4)
        self.time4 = np.linspace(0,100,10000)
        self.lr_x4 = []
        self.lr_y4 = []
    def graph_xy(self):
        '''
        V_initial3 = 5.7 \n
        g = 9.8
        '''
        for t in self.time4:
            r_x = self.v_x4 * t
            r_y = (self.v_y4 * t) - 1/2 * self.g * (t ** 2)
            if r_y >= 0:
                self.lr_x4.append(r_x)
                self.lr_y4.append(r_y)
            else:
                break
            plt.plot(self.lr_x4, self.lr_y4, color='b')
            plt.pause(0.1)
        plt.show()
    def list_graph_vyt(self):
        '''
        V_initial3 = 5.7 \n
        g = 9.8
        '''
        for t in self.time4:
            r_x = self.v_x4 * t
            r_y = (self.v_y4 * t) - 1/2 * self.g * (t ** 2)
            if r_y >= 0:
                self.lr_x4.append(r_x)
                self.lr_y4.append(r_y)
            else:
                break
        return self.lr_x4, self.lr_y4
#!สูตรเเรงต้านอากาศ
class D_xVelocity:#todo เสร็จเเล้ว
    def __init__(self,k_cons=1500,x=0.1632,m=0.025,g=9.78,p=1.225):
        #todo (สปริงง,ระยะหด,มวลของลูก,ค่าg,ความหนาเเน่นอากาศ)
        self.k_cons = k_cons #!สปริง
        self.x = x  #! ระยะหด
        self.M = 0.179 
        self.m = m #! มวลลูกยิง set 
        self.g = g #! เปลี่ยนได้
        self.eff = 1 #! สามารถเปลี่ยนได้เเต่ไม่เกิน 1
        self.theta = (np.pi/4)
        self.u = np.sqrt((self.eff * (self.k_cons * self.x**2)) - (2 * (self.M + self.m) * self.g * self.x * (np.sin(self.theta))) / self.m)
        self.p = p #! เปลี่ยนได้ความหนาเเน่นอากาศ
        self.Area = 1.257 * 10**-3 
        self.c = 0.47
        self.K = 1/2*(self.p*self.c*self.Area) 
        self.ux = self.u * np.cos(self.theta) 
        self.uy = self.u * np.sin(self.theta)
        self.s = self.a = np.sqrt((self.m*self.g)/self.K)
        self.l = 0.3 
        self.time_ypeak = (self.s/self.g) * (math.atan(self.uy/self.s)) 
        self.y_max  = -((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s)-((self.g * self.time_ypeak)/self.s))) + ((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s))) + self.l
        self.y_down = self.y_max - 0.3 
        self.time_down = (self.a/self.g)* math.acosh(math.e ** ((self.g * self.y_down)/(self.a**2))) 
        self.time = self.time_ypeak + self.time_down 
        self.runtime = np.linspace(0,self.time,10000) 

    def xVelocity(self):
        fig = plt.figure()
        ax = plt.axes(xlim=(0,self.time + 0.1),ylim = (0,self.ux+1))
        keepVx = []
        keeptime = []
        for t in self.runtime:
            Vx = (self.m * self.ux) / (self.m + (self.ux * self.K * t))
            if t <= self.time:
                keepVx.append(Vx)
                keeptime.append(t)
        plt.plot(keeptime,keepVx)
        plt.show()
        
    def list_xVelocity(self):
        '''
        V_initial1 = 5.7 \n
        g = 9.8
        '''
        keepVx = []
        keeptime = []
        for t in self.runtime:
            Vx = (self.m * self.ux) / (self.m + (self.ux * self.K * t))
            if t <= self.time:
                keepVx.append(Vx)
                keeptime.append(t)
        return keeptime,keepVx
    
class D_yVelocity:#todo เสร็จเเล้ว
    def __init__(self,k_cons=1500,x=0.1632,m=0.025,g=9.78,p=1.225):
        self.k_cons = k_cons #!สปริง
        self.x = x  #! ระยะหด
        self.M = 0.179 
        self.m = m #! มวลลูกยิง set 
        self.g = g #! เปลี่ยนได้
        self.eff = 1 #! สามารถเปลี่ยนได้เเต่ไม่เกิน 1
        self.theta = (np.pi/4)
        self.u = np.sqrt((self.eff * (self.k_cons * self.x**2)) - (2 * (self.M + self.m) * self.g * self.x * (np.sin(self.theta))) / self.m)
        self.p = p #! เปลี่ยนได้ความหนาเเน่นอากาศ
        self.Area = 1.257 * 10**-3 
        self.c = 0.47
        self.K = 1/2*(self.p*self.c*self.Area) 
        self.ux = self.u * np.cos(self.theta) 
        self.uy = self.u * np.sin(self.theta)
        self.s = self.a = np.sqrt((self.m*self.g)/self.K)
        self.l = 0.3 
        self.time_ypeak = (self.s/self.g) * (math.atan(self.uy/self.s)) 
        self.y_max  = -((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s)-((self.g * self.time_ypeak)/self.s))) + ((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s))) + self.l
        self.y_down = self.y_max - 0.3 
        self.time_down = (self.a/self.g)* math.acosh(math.e ** ((self.g * self.y_down)/(self.a**2))) 
        self.time = self.time_ypeak + self.time_down 
        self.runtime = np.linspace(0,self.time,10000) 

    def yVelocity(self):
        fig = plt.figure()
        ax = plt.axes(xlim=(0, self.time+ 0.1), ylim=(-(self.uy+1), self.uy+1))
        keepVy = []
        keeptime = []
        for t in self.runtime:
            if t <= self.time_ypeak:
                Vy_upward = self.s * math.tan(math.atan(self.uy/self.s) - (self.g*t/self.s))
                keepVy.append(Vy_upward)
                keeptime.append(t)
            if self.time_ypeak <= t <= self.time:
                Vy_downward = -(self.a * math.atan((self.g*t/self.a) - ((self.g*self.time_ypeak)/self.a)))
                keepVy.append(Vy_downward)
                keeptime.append(t)
        plt.plot(keeptime,keepVy)
        plt.show()
        
    def list_yVelocity(self):
        '''
        V_initial1 = 5.7 \n
        g = 9.8
        '''
        keepVy = []
        keeptime = []
        for t in self.runtime:
            if t <= self.time_ypeak:
                Vy_upward = self.s * math.tan(math.atan(self.uy/self.s) - (self.g*t/self.s))
                keepVy.append(Vy_upward)
                keeptime.append(t)
            if self.time_ypeak <= t <= self.time:
                Vy_downward = -(self.a * math.atan((self.g*t/self.a) - ((self.g*self.time_ypeak)/self.a)))
                keepVy.append(Vy_downward)
                keeptime.append(t)
        return keeptime,keepVy


class D_X_trajectory:#todo เสร็จเเล้ว
    def __init__(self,k_cons=1500,x=0.1632,m=0.025,g=9.78,p=1.225):
        self.k_cons = k_cons #!สปริง
        self.x = x  #! ระยะหด
        self.M = 0.179 
        self.m = m #! มวลลูกยิง set 
        self.g = g #! เปลี่ยนได้
        self.eff = 1 #! สามารถเปลี่ยนได้เเต่ไม่เกิน 1
        self.theta = (np.pi/4)
        self.u = np.sqrt((self.eff * (self.k_cons * self.x**2)) - (2 * (self.M + self.m) * self.g * self.x * (np.sin(self.theta))) / self.m)
        self.p = p #! เปลี่ยนได้ความหนาเเน่นอากาศ
        self.Area = 1.257 * 10**-3 
        self.c = 0.47
        self.K = 1/2*(self.p*self.c*self.Area) 
        self.ux = self.u * np.cos(self.theta) 
        self.uy = self.u * np.sin(self.theta)
        self.s = self.a = np.sqrt((self.m*self.g)/self.K)
        self.l = 0.3 
        self.time_ypeak = (self.s/self.g) * (math.atan(self.uy/self.s)) 
        self.y_max  = -((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s)-((self.g * self.time_ypeak)/self.s))) + ((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s))) + self.l
        self.y_down = self.y_max - 0.3 
        self.time_down = (self.a/self.g)* math.acosh(math.e ** ((self.g * self.y_down)/(self.a**2))) 
        self.time = self.time_ypeak + self.time_down 
        self.runtime = np.linspace(0,self.time,10000) 

    def X_trajectory(self):
        fig = plt.figure()
        ax = plt.axes(xlim=(0, self.time + 0.1), ylim=(0 , self.uy + 1))
        keepposition_x = []
        keeptime = []
        for t in self.runtime:
            if t <= self.time:
                x_position = self.m/self.K * math.log(1+((self.ux * self.K * t)/self.m),math.e)
                keepposition_x.append(x_position)
                keeptime.append(t)
        plt.plot(keeptime,keepposition_x)
        plt.show()
        
    def list_X_trajectory(self):
        '''
        V_initial1 = 5.7 \n
        g = 9.8
        '''
        keepposition_x = []
        keeptime = []
        for t in self.runtime:
            if t <= self.time:
                x_position = self.m/self.K * math.log(1+((self.ux * self.K * t)/self.m),math.e)
                keepposition_x.append(x_position)
                keeptime.append(t)
        return keeptime,keepposition_x
    
class D_Y_trajectory:#todo เสร็จเเล้ว
    def __init__(self,k_cons=1500,x=0.1632,m=0.025,g=9.78,p=1.225):
        self.k_cons = k_cons #!สปริง
        self.x = x  #! ระยะหด
        self.M = 0.179 
        self.m = m #! มวลลูกยิง set 
        self.g = g #! เปลี่ยนได้
        self.eff = 1 #! สามารถเปลี่ยนได้เเต่ไม่เกิน 1
        self.theta = (np.pi/4)
        self.u = np.sqrt((self.eff * (self.k_cons * self.x**2)) - (2 * (self.M + self.m) * self.g * self.x * (np.sin(self.theta))) / self.m)
        self.p = p #! เปลี่ยนได้ความหนาเเน่นอากาศ
        self.Area = 1.257 * 10**-3 
        self.c = 0.47
        self.K = 1/2*(self.p*self.c*self.Area) 
        self.ux = self.u * np.cos(self.theta) 
        self.uy = self.u * np.sin(self.theta)
        self.s = self.a = np.sqrt((self.m*self.g)/self.K)
        self.l = 0.3 
        self.time_ypeak = (self.s/self.g) * (math.atan(self.uy/self.s)) 
        self.y_max  = -((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s)-((self.g * self.time_ypeak)/self.s))) + ((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s))) + self.l
        self.y_down = self.y_max - 0.3 
        self.time_down = (self.a/self.g)* math.acosh(math.e ** ((self.g * self.y_down)/(self.a**2))) 
        self.time = self.time_ypeak + self.time_down 
        self.runtime = np.linspace(0,self.time,10000) 

    def Y_trajectory(self):
        fig = plt.figure()
        ax = plt.axes(xlim=(0, self.time + 0.1), ylim=(0, self.y_max + 0.1))
        keeppossition_y = []
        keeptime = []
        for t in self.runtime:
            if t <= self.time_ypeak:
                if math.atan(self.uy/self.s)-((self.g * t)/self.s) >= 0:
                    y_position = -((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s)-((self.g * t)/self.s))) + ((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s))) + self.l
                    keeppossition_y.append(y_position)
                    keeptime.append(t)
                elif math.atan(self.uy/self.s)-((self.g * t)/self.s) < 0:
                    y_position = -((self.s**2)/self.g) * math.log(mpmath.sec(-(math.atan(self.uy/self.s)-((self.g * t)/self.s))),math.e) + ((self.s**2)/self.g) * math.log(mpmath.sec(-(math.atan(self.uy/self.s))),math.e) + self.l
                    keeppossition_y.append(y_position)
                    keeptime.append(t)
            if self.time_ypeak < t <= self.time:
                y_position = -(self.a**2/self.g) * math.log(math.cosh(self.g*((t-self.time_ypeak)/self.a)),math.e) + self.y_max
                keeppossition_y.append(y_position)
                keeptime.append(t)
        plt.plot(keeptime,keeppossition_y)
        plt.show()
        
    def list_Y_trajectory(self):
        '''
        V_initial1 = 5.7 \n
        g = 9.8
        '''
        keeppossition_y = []
        keeptime = []
        for t in self.runtime:
            if t <= self.time_ypeak:
                if math.atan(self.uy/self.s)-((self.g * t)/self.s) >= 0:
                    y_position = -((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s)-((self.g * t)/self.s))) + ((self.s**2)/self.g) * math.log(mpmath.sec(math.atan(self.uy/self.s))) + self.l
                    keeppossition_y.append(y_position)
                    keeptime.append(t)
                elif math.atan(self.uy/self.s)-((self.g * t)/self.s) < 0:
                    y_position = -((self.s**2)/self.g) * math.log(mpmath.sec(-(math.atan(self.uy/self.s)-((self.g * t)/self.s))),math.e) + ((self.s**2)/self.g) * math.log(mpmath.sec(-(math.atan(self.uy/self.s))),math.e) + self.l
                    keeppossition_y.append(y_position)
                    keeptime.append(t)
            if self.time_ypeak < t <= self.time:
                y_position = -(self.a**2/self.g) * math.log(math.cosh(self.g*((t-self.time_ypeak)/self.a)),math.e) + self.y_max
                keeppossition_y.append(y_position)
                keeptime.append(t)
        return keeptime,keeppossition_y
    
if __name__ == '__main__':
    # print(G_xy())
    # x = G_xy(5)
    # x1 = graphxt(5,9.8)
    # y1 = graphyt(5,9.8)
    # vxt1 = graphvxt(5)
    # vyt1 = graphvyt(5)
    # xy = graphxy(5)
    # x.graph_g_xy()
    # y1.graph_yt()
    x = D_xVelocity(1500,0.2,0.025,9.78,1.225)
    y = D_yVelocity(1500,0.2,0.025,9.78,1.225)
    x.xVelocity()
    y.yVelocity()
    # print(p)
    
    #y1.graph_yt()
    # x1.V_initial = 100
    # x1.graph_xt()
    # y1.V_initial1 = 100
    # y1.graph_yt()
    # vyt1.graph_vyt()
    # vxt1.graph_vxt()
    # x1.graph_xt()
    # y1.graph_yt()
    # vxt1.graph_vxt()
    # vyt1.graph_vyt()
    
    
    # print(x1.listxt())
    
    # print(x1.listxt())
    # y1.yt()
    # print(y1.listyt())
    # print(vxt1.listvxt())
    # print(vyt1.listvyt())
    # x = xt()
    # x1,x2 = x.listxt()
    # print(max(x2))
    # x.xt()
    # x.xy()
    # x.xy()
    # x1 , y1 = x.listvyt()
    # plt.plot(x1,y1)
    # plt.show()
    # x.g = 8
    # x.vyt()
    # x.g1 = 9
    # x.t = 0.01
    # x.V_initial3 = 6
    # x.xy()
