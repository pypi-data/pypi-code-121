import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# df=pd.DataFrame({'id': [1, 2, 3, 4],
                   # 'name': ['stream1', 'stream2', 'stream3', 'stream4'],
                   # 'Ti': [200, 50, 125, 45],
                 # 'To': [50, 250, 124, 195],
                 # 'mCp': [3, 2,300,4],
                 # 'dTmin2': [5, 5, 10, 10],
                 # 'integration': [True, True, True, True]
                 # })




def PinchCalculation(df):
    df = df[(df['integration']==True)]
    df=df.to_numpy()
 #   print("Liste des flux",df)
 #   print(type(df))
    rowCount = len(df)
   # print("rowCount=",rowCount)
# =============================================================================
# # #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# # #/////////////////////////////***************Calcul de la courbe composite************************/////////////////////////////////
    Ti = []
    Ti=df[:,2]
    To = []
    To=df[:,3]
    mCp = []
    mCp =df[:,4]
    #print("mCp=",mCp)
    dTmin2 = []
    dTmin2 = df[:,5]
    integration = []
    integration = df[:,6]
    NatureFlux = []
   # interval = df[:,6]
 
  
    for iter in range(0,rowCount ):
        NatureFlux.append(rowCount)
# //// temperature de paroi / températures corrigées
# + Delta_Tmin/2 pour un flux froid, - Delta_Tmin/2 pour un flux chaud (non corrigées par Prosim)

        if (Ti[iter] > To[iter]):
            Ti[iter] = Ti[iter]-dTmin2[iter]
            To[iter] = To[iter]-dTmin2[iter]
            NatureFlux[iter]="FC"
        else:
            Ti[iter] = Ti[iter]+dTmin2[iter]
            To[iter] = To[iter]+dTmin2[iter]
            NatureFlux[iter]="FF"
        
# } //fin test nature du flux

#    }//fin de la boucle for
   # print('temp corrigées : NatureFlux',NatureFlux,'Ti',Ti,'To', To)
        
        
# 
# 
# # **************tri de valeurs de température*******************
    GCC=[]#;//kW
    T=[]
    for value in Ti:
       T.append(value)
      
    for value in To:
       T.append(value)
      
    
#     
    T=np.sort(T)
    # ne prendre que les valeurs unique :
    T=np.unique(T)
   # print("T=",T)
    GCC=0.0*T #initialisation à la dim de T
# 
# =============================================================================

# ///////////////////////////////////////////////////////////////////////////
    ccc=[]
    ccf=[]
# //*********************calcul de DH*********************////////////
    DH=[]
    DH_prop=[]#//DH propaged
   
    DHij=np.full((rowCount, len(T)-1), 0.0)#;//i=flux=iter = rowCount-2, j=intervalle+1=len(T)
    mCpij= np.full((rowCount, len(T)-1), 0.0)#;//débit par intervalle =0 si pas de flux
    
    #print("type mCpij=",mCpij)
    

# 
# 
# 
    for j in range(0,(len(T)-1)):
        DH.append(0.0)
        DH_prop.append(0.0)
        
        ccc.append(0.0)
        ccf.append(0.0)
        
      
      #  print(DH[j])
        for i in range(0,rowCount):
         #   print(i)
            
            
         #   print(NatureFlux[i])
            if (NatureFlux[i]=="FF"):
                if ((Ti[i]<=T[j]) and (To[i]>T[j])):
                    mCpij[i,j]=mCp[i]
                    
                else:
                    mCpij[i,j]=0.0
               # print("mCpij[i,j] FF",mCpij[i,j])
 #//fin du test de la presence du flux froid dans l intervalle
                
                DHij[i,j]=-mCpij[i,j]*(T[j+1]-T[j])#;//calcul de DH pour un flux froid
              #  print("DHij[i,j] FF",DHij)
                ccf[j]=-DHij[i,j]+ccf[j]           
#  //CCchaude[0]=0;
# }
            else: #si le flux est chaud
                if ((Ti[i]>T[j]) and (To[i]<=T[j])):
                    mCpij[i,j]=mCp[i]
                   # print("mCp[i] FC",mCp[i])
                   # print("mCpij[i,j] FC",mCpij[i,j])
                else:
                    mCpij[i,j]=0.0
                    #;}//fin du test de la presence du flux chaud dans l intervalle
                
                #print("mCpij[i,j] FC",mCpij[i,j])
                DHij[i,j]=mCpij[i,j]*(T[j+1]-T[j]) #;//calcul de DH pour un flux chaud
               # print("DHij[i,j] FC",DHij)
                ccc[j]=DHij[i,j]+ccc[j]#; 
                # }//fin du test nature de flux
# 
# 
          #  print(DHij)
           
            DH[j] = DH[j]+DHij[i,j]
           # print("DH[j]",DH[j])
   # print("DHij=",DHij)
   # print("mCp;",mCpij)
  #  print("échange de chal par plage de temp DH=",DH)

#  }//fin de la boucle for ligne flux

#  }//fin de la boucle for intervalle

 
   # print(ccc)
   # print(ccf)
# //j=1;
    DH_prop[(len(T)-2)]=DH[(len(T)-2)]
    #print("DH_prop[(len(T)-2)]",DH_prop[(len(T)-2)])
   # print(DH_prop)
    for j in range((len(T)+-3),-1,-1):
       # print(j)
#  //DH[j]=0;
#  //for (var i = 0; i < rowCount-1; i++) {

        DH_prop[j]=DH_prop[j+1]+DH[j];
       # print("DH_prop[j]",DH_prop[j])
# // }//fin de la boucle for ligne flux
#  
# }//fin de la boucle for intervalle
# 

  #  print("DH_prop=",DH_prop)
#  //fonction min
    MinDH_prop=min(DH_prop)
  #  print("Min DH_prop=",MinDH_prop)

    MinDH_prop=min(MinDH_prop,0.0)
   # print("Min DH_prop=",MinDH_prop)
# ///////////////////////////calcul de la grande courbe composite//////////////////////////////
    GCC[len(T)-1]=-MinDH_prop;
    for j in range( 0,(len(T)-1)) :
       # print(j)
        GCC[j]=DH_prop[j]-MinDH_prop
        #print("GCC[j]",GCC[j])
       # print(GCC[j])

    # print('Utilité froide=',GCC[0])
    # print('Utilité chaude',GCC[(len(T)-1)])
    # print('Grande CC',GCC)
    

# ////////////////////////////////////////////////////////////////////////////////
# 
#   ////////////**************************Calcul des courbes composites****************////////////////////////////////

#   //////////////////////////////fin du calcul et affichage de la GCC////////////////////////////////////////////////////////////
# 
    ccc_prop=T*0.0      #init a la dim de T
    ccf_prop=T*0.0    #init a la dim de T
    ccc_prop[0]=0.0
    ccf_prop[0]=GCC[0]
    for j in range(0,(len(T)-1)):
         ccc_prop[j+1]=ccc[j]+ccc_prop[j]
         ccf_prop[j+1]=ccf[j]+ccf_prop[j]
    # print('ccf',ccf_prop)
    # print('ccc',ccc_prop)
    
    # plt.plot(GCC,T)
    # plt.show()

    # plt.plot(ccf_prop,T,ccc_prop,T)
    # plt.show()
    plot_GCC=np.array((GCC,T)).T
    plot_ccf=np.array((ccf_prop,T)).T
    plot_ccc=np.array((ccc_prop,T)).T
    #newarr = GCC.reshape(2, 2)

    #print(newarr)
    utilite_froide=round(GCC[0],1)
   # print("utilite_froide",GCC[0])
    utilite_chaude=round(GCC[(len(T)-1)],1)
    
    return T, plot_GCC, plot_ccf,plot_ccc,utilite_froide,utilite_chaude
        


# # =============================================================================
#PinchCalculation(df)

# a,b,c,d=PinchCalculation(df)
# print(a,b,c,d)
# =============================================================================
