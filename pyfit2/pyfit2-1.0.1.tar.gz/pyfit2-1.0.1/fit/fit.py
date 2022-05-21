
import numpy as np
import matplotlib.pyplot as plt

BIG = 16
SMALL = 8
MID = 13


def roundup(x,r=2):
        a = x*10**r
        a = np.ceil(a)
        a = a*10**(-r)

        if type(x) == float or type(x) == int or type(x) == np.float64:
            if a == 0 :
                a=10**(-r)
        else:
            try:                                           # rundet mehrdimensionale arrays
                for i,j in enumerate(a):
                    for k,l in enumerate(j):
                        if i == 0:  
                            i=10**(-r)
            except:                                        # rundet eindimensionale arrays
                for i,j in enumerate(a):
                    if i == 0:  
                        i=10**(-r)
                    
        return np.around(a,r)

class linear_fit():
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import AnchoredText
    import matplotlib as mpl


    #---nicht-beachten---------------------------------------
    style = 'default'
    plt.style.use([style])

    def change_style(self,str):
        self.plt.style.use(str)
        # plt.rc('font', size=BIG) 
        # plt.rc('legend', fontsize=BIG) 
        # plt.rc('axes', titlesize=BIG)    # fontsize of the x and y labels
        # plt.rc('xtick', labelsize=BIG)    # fontsize of the tick labels
        # plt.rc('ytick', labelsize=BIG) 
        # plt.rc('axes', titlesize=BIG)     # fontsize of the axes title
        # plt.rc('axes', labelsize=BIG)    # fontsize of the x and y labels
   
    #---auch-nicht-beachten---------------------------------------
    def varianz_xy(self,x,x_mean,y,y_mean):
        return (1/len(x))*((x-x_mean)*(y-y_mean)).sum()
    def varianz_x(self,x,x_mean):
        return (1/len(x))*((x-x_mean)**2).sum()
    def mittel_varianzgewichtet(self,val,val_err):
        return (val/(val_err**2)).sum()/(1/(val_err**2)).sum()
    
    x_mittel = 0
    m_val = 1
    n_val = 1
    x_val = 1
    y_val = 1
    n_err = 0
    m_err = 0
    Vmn = 0

    detail = True # Ausfürhlichkeit des Infos 

    #-----------------------------------------------------------------
    #least squares zur Angabe der Güte des Plots
    def chi2(self):
        self.chi = (1/len(self.x_val)*((self.f(self.x_val) - self.y_val)**2/np.asarray(self.y_err)**2).sum()).round(2)
        return self.chi


    #---WICHTIG!!!!!!!!!!!!---------------------------------------------------
    # Definiere Fehler des Scatter Plots ------------------------------------------
    # BEACHTE: falls der Fehler eine float-zahl ist, muss diese erst im [] geschrieben werden und mit der Anzahl der
    # Messwerte multiplizert werden, um eine Liste mit entsprechender Länge zu erstellen
    def set_y_error(self,yerr,var=True):
        self.y_err = yerr
        self.y_var = var

        return self.y_err

    def set_x_error(self,xerr):
        self.x_err = xerr

        return self.x_err


    #setze individuelles Runden für m und n
    r_m = 0
    r_n = 0
    def set_m_round(self,m):  
        self.r_m = m
        return

    def set_n_round(self,n):  
        self.r_n = n
        return

    #---WICHTIG!!!!!!!!!!!!--------------------------------------------------- 
    # hiermit werden alle Daten NICHT varianzgewichtet ausgewertet
    def make_fit(self,x_vals,y_vals,r=2,detail=True,str=''):
        if self.r_m == 0:                        #setze m,n nachkommastellen
            self.r_m = r   

        if self.r_n == 0:                        #setze m,n nachkommastellen
            self.r_n = r 
    
        self.x_val=x_vals
        self.y_val=y_vals

        if self.y_err[0]==0:
            print('Acthung: bitte y-Fehler setzen')
            return 0

        self.detail = detail # setzt detail boolean

        #berechne mittelwerte Varianzgewichtet
        # err ist dummy array für den error
        if self.y_var == True:
            print('VARIANZGEWICHTET')
            if len(self.y_err) == 1:
                err = self.np.zeros(len(x_vals))
                err[:] = float(self.y_err[0])
            else:
                err = self.y_err
            err = self.np.asarray(err)
            y = round(self.mittel_varianzgewichtet(y_vals,err),r)
            x = round(self.mittel_varianzgewichtet(x_vals,err),r)
            xx = round(self.mittel_varianzgewichtet(x_vals**2,err),r)
        else:
            print('NICHT VARIANZGEWICHTET')
            y = round(self.np.mean(y_vals),r)
            x = round(self.np.mean(x_vals),r)
            xx = round(self.np.mean(x_vals**2),r)

        x_arr = self.np.zeros(len(x_vals))
        x_arr[:] = x
        y_arr = self.np.zeros(len(y_vals))
        y_arr[:] = y 
        
        Vxy = self.varianz_xy(x_vals,x_arr,y_vals,y_arr)
        Vx = self.varianz_x(x_vals,x_arr)
        # Vy = self.varianz_x(y_vals,y_arr)
        if len(self.y_err) == 1:
            Vy = len(x_vals) / (1/self.np.asarray(([self.y_err]*len(x_vals)))**2).sum()
        else:
            Vy = len(x_vals) / (1/self.y_err**2).sum()    # Varianzgewichtet Varianz, da mit standardvarianz es nicht funktioniert
        Vm = Vy/(len(x_vals)*(xx-x**2))
        Vn = xx * Vm
        Vmn = - Vm * x
        #sigma = self.np.sqrt(Vy)

        m = round(Vxy/Vx,self.r_m)
        n = round(y-m*x,self.r_n)

        merr = roundup(self.np.sqrt(Vm),self.r_m)
        nerr = roundup(self.np.sqrt(Vn),self.r_n)

        self.m_err = merr
        self.n_err = nerr
        self.x_mittel = x
        self.n_val = n
        self.m_val = m
        self.Vmn = Vmn

        self.chi2()

        print('----------------------------')
        if str != '':
            print(str)
        if self.detail == True:
            print('x:', x)
            print('x^2: ', xx)
            print('y:', y)
            print('sigma^2:' , round(Vy,2))
        print('m:', m,'+-',merr)
        print('n:', n,'+-',nerr)
        print('goodness:', self.chi)     # soll minimum sein für guten Fit
        print('----------------------------')

        result = {
            'x' :x,
            'xx' :xx,
            'y' :y,
            'm' : m,
            'n' : n,
            'merr' : merr,
            'nerr' : nerr,
            'Vm' : Vm,
            'Vn' : Vn,
            'Vxy' : Vxy,
            'Vmn' : Vmn,
            'x_vals' : x_vals,
            'y_vals' : y_vals,
            'yerr' : self.y_err
        }
        
        self.change_style([self.style]) # verhindert, dass die Rädner im Plot im dark mode schlecht sichtbar sind

        return result

    def f(self,x):
        return self.n_val + self.m_val*x
        

    y_var = False
    y_err = [0]
    x_err = [0]
    def get_error(self):
        if(len(self.y_err) == 0):
            self.y_err = [self.y_err]*len(self.x_val)
        if(len(self.x_err) == 0):
            self.x_err = [self.x_err]*len(self.x_val)
        if(self.y_err[0] == 0):
            self.y_err = [0]*len(self.x_val)
        if(self.x_err[0] == 0):
            self.x_err = [0]*len(self.x_val)
        return self.y_err,self.x_err


    textloc = 'upper right'

    # Setze Platzierung vom beschreibenden Text -------------------------------
    def set_loc(self,locc):
        self.textloc = locc
        return self.textloc

    #--Wichtig---------------------------
    # erstellt optionale Fehlerkurven
    def s(self,val):
        return self.np.sqrt(self.m_err**2*val**2+self.n_err**2+2*self.Vmn*val)

    #OPTIONAL
    #ändere die Größe des ausgegebenen Plots
    plotsize = (6,4)
    def change_plotsize(self,x,y):
        self.plotsize = (x,y)
        return 

    #OPTIONAL
    #ändere das Aussehen der Errorbars
    marker = 7
    caps = 5
    eline = 1.5
    markerwidth = 1.5
    anch = 7
    def change_errorbar(self,marker=7, caps=5, eline=1.5, markerwidth=1.5,anch=8):
        self.marker = marker
        self.caps = caps
        self.eline = eline
        self.markerwidth = markerwidth
        self.anch = anch

        return

    #---WICHTIG!!!!!!!!!!!!---------------------------------------------------
    # hiermit kann ein optionaler Plot erstellt werden
    def plot(self,title='title',xlabel='x_Achse',ylabel='y_achse',err=True):
        fig, ax = self.plt.subplots(figsize=self.plotsize)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.plot(self.x_val, self.f(self.x_val),color='black')#,color='steelblue',label='Geraden-Fit')

        if self.detail == True:
            print('f(x[0]): +-', self.f(self.x_val[0]).round(2))
            print('f(x_letztes): +-', self.f(self.x_val[(len(self.x_val)-1)]).round(2))
            print('----------------------------')

        if(err==True):
            ax.plot(self.x_val, self.f(self.x_val)+self.s(self.x_val),'--',color='black',zorder=1,alpha=0.8,lw=1.3)
            ax.plot(self.x_val, self.f(self.x_val)-self.s(self.x_val),'--',color='black',zorder=1,alpha=0.8,lw=1.3)
            self.plt.gca().fill_between(self.x_val, self.f(self.x_val)+self.s(self.x_val), self.f(self.x_val)-self.s(self.x_val),alpha=0.25,color='steelblue')
            if self.detail == True:
                print('s(x[0]): +-', self.s(self.x_val[0]).round(2))
                print('s(x_mittel): +-', self.s(self.x_mittel).round(2)) 
                print('s(x_letztes): +-', self.s(self.x_val[(len(self.x_val)-1)]).round(2))

        self.get_error()
        ax.errorbar(self.x_val, self.y_val,color='tab:red',marker='s',markersize=self.marker,linestyle='',yerr=self.y_err, xerr=self.x_err,label='Daten',capsize=self.caps, elinewidth=self.eline, markeredgewidth=self.markerwidth)

        at = self.AnchoredText(f'Achsenabschnitt: {self.n_val} $\pm$ {self.n_err} \n Steigung: {self.m_val} $\pm$ {self.m_err}',
        loc=self.textloc,prop=dict(size=self.anch))
        ax.add_artist(at)
        #ax.legend()

        self.plt.show()
        return self

class multiplot():
    
    def change_fontsize(self,size):
        self.BIG = size

    m, n , x, y, xerr, yerr = 0, 0 ,0 ,0 ,0, 0
    num = 0
    color = ['tab:blue','tab:green','tab:red','tab:pruple','tab:cyan'] # standard farbe für Fehlerbalken
    label = ['label']

    def plotcount(self, num):
        self.m = np.zeros(num)
        self.n = np.zeros(num)
        self.x = [0]*num
        self.y = [0]*num
        self.xerr = [0]*num
        self.yerr = [0]*num
        self.num = num
        self.label = ['label'] * num
        
        return

    def set_result(self,result,i):
        self.m[i] = result['m']
        self.n[i] = result['n']
        self.x[i] = result['x_vals']
        self.y[i] = result['y_vals']
        self.yerr[i] = result['yerr']

        return result


    def f(self,x,m,n):
        return x*m+n

    marker = 5
    caps = 5
    eline = 1
    markerwidth = 1
    def change_errorbar(self,marker=8, caps=8, eline=2, markerwidth=2):
        self.marker = marker
        self.caps = caps
        self.eline = eline
        self.markerwidth = markerwidth

        return

    def set_color(self,str):
        self.color = str

        return str

    def set_label(self,str):
        self.label = str

        return str

    ylim = (0,0)
    xlim = (0,0)

    def set_lim(self,str,tupel,tupel2=(0,0)):
        if str == 'x':
            self.xlim = tupel
        if str == 'y':
            self.ylim = tupel
        if str == 'xy' and tupel2 != (0,0):
            self.xlim = tupel
            self.ylim = tupel2
        return tupel

    plotsize = (6,4)
    def change_plotsize(self,x,y):
        self.plotsize = (x,y)
        return 

    def plot(self,title='title',xlabel='x_Achse',ylabel='y_achse', png = False,name='name.png'):
        fig, ax = plt.subplots(figsize=self.plotsize)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        
        if self.ylim != (0,0):
            ax.set_ylim(self.ylim)
        if self.xlim != (0,0):
            ax.set_xlim(self.xlim)

        for i in range(self.num):
            ax.plot(self.x[i], self.f(self.x[i],self.m[i],self.n[i]),'--',color=self.color[i%len(self.color)], alpha=0.75)
            ax.errorbar(self.x[i], self.y[i],marker='o',ms=self.marker,ls='',color=self.color[i%len(self.color)],
            yerr=self.yerr[i],label=self.label[i],capsize=self.caps, elinewidth=self.eline,
            markeredgewidth=self.markerwidth)

        ax.legend(bbox_to_anchor=(1.01, 1),frameon=True,fontsize=12)

        if png == True:
            plt.savefig(name)

        plt.show()


        return self