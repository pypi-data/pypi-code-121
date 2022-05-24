from os import mkdir
import shutil
from Disys_DL import Utils as dy
import numpy as np
import halcon as ha
import logging
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pyrenn as prn
from PIL import Image
import sys
from os import listdir
from os.path import isfile, join
from sklearn.neural_network import MLPRegressor

log = logging.getLogger("Disys Calib")


class Disys_Calib:
    # logging.basicConfig()
    # log.setLevel(logging.DEBUG)
    # main_path   = []
    # col_cog     = []
    # row_cog     = []
    # X_Tool      = []
    # Y_Tool      = []
    # Z_Tool      = []

    def __init__(self,path_to_data : str):
        """ Path to halcon tuples : tuples files are Col_Cog, Row_Cog, X_Tool, Y_Tool, Z_Tool, output will be saved in path_to_data path."""
        self.main_path = path_to_data
        try :         
            self.Col_Cog =       np.array(ha.read_tuple(self.main_path+R"\Col_Cog.tup"))
            self.Row_Cog =       np.array(ha.read_tuple(self.main_path+R"\Row_Cog.tup"))
            self.X_Tool  =       np.array(ha.read_tuple(self.main_path+R"\X_Tool.tup"))
            self.Y_Tool  =       np.array(ha.read_tuple(self.main_path+R"\Y_Tool.tup"))
            self.Z_Tool  =       np.array(ha.read_tuple(self.main_path+R"\Z_Tool.tup"))
        except:
            log.error("Error : files not found. Input path may be not correct.")
            return 
        
        self.df = pd.DataFrame({'col_cog' :self.col_cog,'row_cog' : self.row_cog,
                'X' : self.X_Tool,'Y' : self.Y_Tool,'Z' :self.Z_Tool})

        Data = self.df.values
        n = Data.shape[0]
        self.X = Data[:n,0:2]
        self.Y = Data[:n,2:]
        X_feature_names = self.df.columns[0:2]
        Y_feature_names = self.df.columns[2:]

        print("Disys_Calib initialized : Amount of data {}.".format(n))
        print("Data features {}, labels features {}".format(X_feature_names.values,Y_feature_names.values))

    def __init__(self,df_input : pd.DataFrame, mainpath ):
        """ Pandas dataframe with columns : Col_Cog, Row_Cog, X_Tool, Y_Tool, Z_Tool, optional mainpath to save output. """
        self.main_path = []
        try :    
            self.df = pd.DataFrame({'col_cog' :df_input.Col_Cog,'row_cog' : df_input.Row_Cog,
                'X' : df_input.X_Tool,'Y' : df_input.Y_Tool,'Z' :df_input.Z_Tool})

            self.df = self.df[self.df.row_cog.isin([0.0,-1.0]) == False ]
            self.df = self.df[self.df.col_cog.isin([0.0,-1.0]) == False ]    
            self.Col_Cog =   self.df.col_cog 
            self.Row_Cog =   self.df.row_cog 
            self.X_Tool  =   self.df.X
            self.Y_Tool  =   self.df.Y
            self.Z_Tool  =   self.df.Z
            self.main_path = mainpath

        except:
            log.error("Error : data not found. Check the names!")
            return 
        
        Data = self.df.values
        n = Data.shape[0]
        self.X = Data[:n,0:2]
        self.Y = Data[:n,2:]
        X_feature_names = self.df.columns[0:2]
        Y_feature_names = self.df.columns[2:]

        print("Disys_Calib initialized : Amount of data {}.".format(n))
        print("Data features {}, labels features {}".format(X_feature_names.values,Y_feature_names.values))

    def CreateNN(self,width:int,height:int):
        """ Pandas dataframe with columns : Col_Cog, Row_Cog, X_Tool, Y_Tool, Z_Tool, optional mainpath to save output. """
        try:
            mkdir(self.main_path+R"\dati calibrazione")
        except:
            pass
        self._scalerX = MinMaxScaler((-1,1)).fit(self.X) 
        self._scalerY = MinMaxScaler((-1,1)).fit(self.Y)
        X_norm = self._scalerX.transform(self.X)
        Y_norm = self._scalerY.transform(self.Y)

        n = self.X.shape[0]
        n_train = int(6./7.*n)
        n_val = int((n-n_train)/3.)
        n_test = n - n_train - n_val
        Xtrain_and_val, Xtest, Ytrain_and_val, Ytest = train_test_split(X_norm, Y_norm, test_size=n_test/n)

        print("Amount of data for training: {}".format(n_train))
        print("Amount of data for test: {}".format(n_test))
        print("\n********** Start training **********")
        performance_best = 1e3
        net = prn.CreateNN([2,100,3])
        step = 5
        for i in range(step):
            net = prn.train_LM(np.transpose(Xtrain_and_val),np.transpose(Ytrain_and_val),net,verbose=False,k_max=200,E_stop=1e-9) 
            ytest_pred = prn.NNOut(np.transpose(Xtest),net)
            pred_it = self._scalerY.inverse_transform(np.transpose(ytest_pred))
            delta = abs(self._scalerY.inverse_transform(Ytest)-pred_it)
            err = np.sqrt(np.power(delta[:,0],2)+np.power(delta[:,1],2)+np.power(delta[:,2],2))
            print("ERRORE RETE step {}/{}: Y_test ->  min {:.4f} , mean {:.4f} , max {:.4f} ".format((i+1),step,np.min(err),np.mean(err),np.max(err)) )
            if (np.mean(err) < performance_best):
                best_net = net
                performance_best = np.mean(err)
        print("************************************")
        

        #OUTPUT
       
        prn.saveNN(best_net,self.main_path+R"\dati calibrazione\best_net.csv")


        ## Conversion to scikit learn mlp
        with open(self.main_path+R"\dati calibrazione\best_net.csv") as file:
            lines = [line.rstrip() for line in file]
        lines[0:13] = []
        data_lines = np.array(lines,dtype=np.double)

        num_neurons = 100
        num_layers = 1
        num_input = 3

        Wh = []
        Ls = []#np.array([])
        Whb = []
        listaValori=data_lines
        k = 0

        for i in range(num_input-1):
            Wh.append(np.array((listaValori[k:k+num_neurons])))
            k += num_neurons
        Whb=np.array((listaValori[k:k+num_neurons].tolist()))
        k += num_neurons
        for i in range(num_neurons):
            if Ls:#.size == 0:
                Ls.append(listaValori[k:k+num_input].tolist())
            else:
                Ls.append((listaValori[k:k+num_input].tolist()))
            k += num_input

        #bias
        Lsb=((listaValori[k:k+num_input].tolist()))

        coeff = [np.ndarray(shape=(1+num_layers,num_neurons),buffer=np.array(Wh)),np.array(Ls)]
        interc = [Whb,np.array(Lsb)]

        self.mlp = MLPRegressor(hidden_layer_sizes=100,activation="tanh",solver='lbfgs',max_iter =10e4,tol = 1e-9,verbose=False).fit(Xtrain_and_val,Ytrain_and_val)
        self.mlp.coefs_ = coeff
        self.mlp.intercepts_ = interc

        y_all_pred = self.mlp.predict(X_norm)
        pred_it = self._scalerY.inverse_transform(y_all_pred)
        delta = abs(self.Y-pred_it)
        self.err = np.sqrt(np.power(delta[:,0],2)+np.power(delta[:,1],2)+np.power(delta[:,2],2))
        print("\nERRORE RETE finale: min {:.5f} , mean {:.5f} , max {:.5f} ".format(np.min(err),np.mean(err),np.max(err)) )
        with open(self.main_path+R"\dati calibrazione\Report_Rete.txt",'w') as f:
            f.write("---   Final network    ---\nmin error  {:.5f}mm,\nmean error {:.5f}mm,\nmax error  {:.5f}mm. "
                .format(np.min(err),np.mean(err),np.max(err)) )
        try:
            self.plotError(width,height).savefig(self.main_path+R"\dati calibrazione\ErrorPlot.tif")
            self.plotErrorXZ(width,height).savefig(self.main_path+R"\dati calibrazione\ErrorPlotXZ.tif")
        except Exception as err:
            log.error("Eccezione : %S",err)

        return self.mlp,best_net



    def DoinferenceMLP(self, input_data : pd.DataFrame, input_net_mlp):
        data_norm = self._scalerX.transform(input_data.values)
        pred_norm = input_net_mlp.predict(data_norm)
        out_data = self._scalerY.inverse_transform(pred_norm)
        return out_data

    def DoinferenceMLP(self, input_data : np.array, input_net_mlp):
        data_norm = self._scalerX.transform(input_data)
        pred_norm = input_net_mlp.predict(data_norm)
        out_data = self._scalerY.inverse_transform(pred_norm)
        return out_data

    def DoInference(self, input_data : pd.DataFrame, input_net):
        data_norm = self._scalerX.transform(input_data.values)
        pred_norm = prn.NNOut(np.transpose(data_norm),input_net)
        out_data = self._scalerY.inverse_transform(np.transpose(pred_norm))
        return out_data
    def DoInference(self, input_data : np.ndarray, input_net):
        data_norm = self._scalerX.transform(input_data)
        pred_norm = prn.NNOut(np.transpose(data_norm),input_net)
        out_data = self._scalerY.inverse_transform(np.transpose(pred_norm))
        return out_data

    def plotError(self,w,h):
        fig = plt.figure(figsize=(30,30) )
        p = plt.scatter(self.X[:,0], self.X[:,1],
                linewidths=1, alpha=.7,
                edgecolor='k',
                s = 150,
                c=self.err)
        plt.title("Calibration error",fontsize=150)
        plt.xlabel("Columns [px]",fontsize=30)
        plt.ylabel("Rows [px]",fontsize=30)
        plt.xlim(0, w)
        plt.ylim(h, 0)
        plt.gca().set_aspect('equal', adjustable='box')
        cb = fig.colorbar(p)
        cb.ax.tick_params(labelsize=30) # ?? ----------
        cb.set_label("Error [mm]",fontsize=30)
        #plt.show(block = False)
        return fig

    def plotErrorXZ(self,w,h):
        fig = plt.figure(figsize=(30,30))
        p = plt.scatter(self.Y[:,0], self.Y[:,2],
                linewidths=1, alpha=.7,
                edgecolor='k',
                s = 150,
                c=self.err)
        plt.title("Calibration error",fontsize=150)
        plt.xlabel("X [mm]",fontsize=30)
        plt.ylabel("Z [mm]",fontsize=30)
        plt.xlim(min(self.Y[:,0])*1.05, max(self.Y[:,0])*0.95)
        #plt.ylim(0, h)
        plt.gca().set_aspect('equal', adjustable='box')
        cb = fig.colorbar(p)
        cb.ax.tick_params(labelsize=30) # ?? ----------
        cb.set_label("Error [mm]",fontsize=30)
        #plt.show(block = False)
        return fig

    def CreateLuts(self,net_mlp,width:int,height:int):
        """ Input neural network (from CreateNN), width , height of the camera """
        rows = []
        cols = []
        for i in range(height):
            for j in range(width):
                rows.append(i)
                cols.append(j)
        ds = self._scalerX.transform(np.array((cols,rows)).transpose())
        p = net_mlp.predict(ds)
        p_it = self._scalerY.inverse_transform(p)
        #LUTS
        X_im = np.reshape(p_it[:,0],(height,width))
        Y_im = np.reshape(p_it[:,1],(height,width))
        Z_im = np.reshape(p_it[:,2],(height,width))

        Image.fromarray(X_im).save(self.main_path+R"\X.tiff")
        Image.fromarray(Y_im).save(self.main_path+R"\Y.tiff")
        Image.fromarray(Z_im).save(self.main_path+R"\Z.tiff")

        #MASK
        maschera = np.zeros((height,width),np.int8)
        linearInd= np.ravel_multi_index([np.array(self.Row_Cog,np.int64),np.array(self.Col_Cog,np.int64)], (height,width))
        m = np.ravel(maschera)
        m[np.array(linearInd,np.int64)] = 255
        maschera = np.resize(m,(height,width))
        himage = dy.nparray2HImage(maschera)
        region = ha.threshold(himage,1,1e9)
        cvhull = ha.get_region_convex(region)
        region_c = ha.gen_region_polygon(cvhull[0],cvhull[1])
        region_c = ha.fill_up(region_c)
        ha.overpaint_region(himage,region_c,255,'fill')
        ha.write_image(himage,'png',0,self.main_path+R'\Mask.png')

    def MoveFilesToFolders(self):
        onlyfiles = [f for f in listdir(self.main_path) if isfile(join(self.main_path, f))]
        for f in onlyfiles:
            if (not (f.endswith(".tiff")) and not (f.endswith(".csv")) and not (f.endswith("mask.png"))):
                shutil.move(self.main_path+"/"+f,self.main_path+R"\dati calibrazione")

