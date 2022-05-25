"""
Author Babak.EA


"""

import pandas as pd
import numpy as np
import sklearn
from sklearn.decomposition import TruncatedSVD # popularity based recommender system
from sklearn.neighbors import NearestNeighbors # User similarity recommender model 
from collections import Counter
import pickle
import json
import pprint
import warnings
warnings.filterwarnings("ignore")
import os    
from sklearn.preprocessing import MinMaxScaler  
from random import random,choice
import matplotlib.pyplot as plt

    
def Path(path):
    if path[-1]=="/":
        return path
    else:
        return path+"/"
    
def folder_inspect(path):
    path=path.replace("./","")
    path=path.replace("/","")
    if not os.path.exists(path):
            os.makedirs(path)
    return "./"+path+"/"

    

    
def Scor_calcualt(x):
    if x<=6 and x!=0:
        return -1
    elif x>6 and x<=8 or x==0:
        return 0
    else:
        return 1
class Model_Generator:
    def __init__(self,df_C_Per_Product,df_C_NPS_Product,df_C_NPS_Extend,ProductCode="ProductCode",
                 Customer_ID="CustomerCIF",CustomerCount="CustomerCount",pr_category="SalesCategoryCornerstoneID",ResponseDate="ResponseDate",
                 StatedIncome="StatedIncome",CustomerScore="CustomerScore",
                 path="./model/",limit=0.79,knn_neighbors=100,Evaluate=True,Sample_size=0.03):
        """
        Model_Generator(
        "df_C_Per_Product=Dataset including Product information like Id, name, domain, popularity, count",
        "df_C_NPS_Extend: dataset including user raw's information, user ID, product ID",
 |      "df_C_NPS_Products: user info , Income, and rating"
 |      ProductCode, Customer_ID are columns name to help the AI to read the dataset,
 |      CustomerCount: count product, group by customer ID,
 |      pr_category: what category products belong like small business, daytoday, ..., 
 |      limit=0.8: the ratio for the similarity between products 
 |      ,knn_neighbors=100: number of similar users based on products and activities)
        """
        print("Initial ......")
        if not os.path.exists('model'):
            os.makedirs('model')
        if not os.path.exists('report'):
            os.makedirs('report')
            
        

        self.report=dict()
        self.path=Path(path)
        #print(self.path)
        self.Pr_dict=dict()
        self.Limit=limit
        self.knn_neighbors=knn_neighbors
        self.ProductCode=ProductCode
        self.Customer_ID=Customer_ID
        self.CustomerCIF=Customer_ID
        self.CustomerCount=CustomerCount
        self.pr_category=pr_category
        self.ResponseDate=ResponseDate
        self.StatedIncome=StatedIncome
        self.CustomerScore=CustomerScore
        
        self.df_C_Per_Product=df_C_Per_Product
        self.df_C_NPS_Product=df_C_NPS_Product
        self.df_C_NPS_Extend=df_C_NPS_Extend
        self.Sample_size=Sample_size

        self.df_C_NPS_Product=df_C_NPS_Product.drop_duplicates(subset=[self.Customer_ID,self.ProductCode])# drope duplicates records

        self.df_C_NPS_Product["PR"]=1 # add a counter 

        self.product_dict() # product dict : Pr info and definition

        self.Product_matrix()# prodcut Hist ( binary matrix user and product), 

        self.SVD_model()# matrix factorization products using SVD

        self.User_info()
        #print("ML ......")
        self.ML_model()
        self.ML_product_neighbors()
        if Evaluate==True:
            self.Evaluate()
    

        
    def product_dict(self):
        """
        Input:  "df_C_Per_Product=Dataset including Product information like Id, name, domain, popularity, count",
        Out put: Dictionary  
        "{00001000 ": {
            "ProductCode": "00001000",
            "ProductName": "Test Product",
            "SalesCategoryCornerstoneID": "Test PR",
            "CustomerCount": 9
        },
        {00002000 ": {
            "ProductCode": "00002000",
            "ProductName": "Test_2 Product",
            "SalesCategoryCornerstoneID": "Test_2 PR",
            "CustomerCount": 10
        },
        
        the dict will be recorded as a PKL file in a Data folder(path) Pr_dict.pkl
        """
        
        #df_C_Per_Product
        self.Pr_dict=dict()
        self.Pr_dict=self.df_C_Per_Product.groupby(by=self.ProductCode, sort=True).apply(lambda x: x.to_dict(orient='records')).to_dict()

        with open(self.path+'Pr_dict.json', 'w') as fp:
            json.dump(self.Pr_dict, fp)
        pickle.dump(self.Pr_dict, open(self.path+'Pr_dict.pkl','wb'))

    def Product_matrix(self):
        """
        Input: "df_C_NPS_Products: user info , Income, and rating"
        Output:
        Product_hist.pkl: 
        User Product Utility Matrix: its a sparce Product matrix
        
        Product_popularity.pkl:
        User Product Binary Matrix 
       
        """
        
        
        self.Product_hist = self.df_C_NPS_Product.pivot(index=self.Customer_ID,
                                                        columns=self.ProductCode,
                                                        values=self.ProductCode).fillna(0)
        self.Product_popularity = self.df_C_NPS_Product.pivot_table(values='PR', index=self.Customer_ID,
                                                                    columns=self.ProductCode, fill_value=0)
        pickle.dump(self.Product_hist, open(self.path+'Product_hist.pkl','wb'))
        pickle.dump(self.Product_popularity, open(self.path+'Product_popularity.pkl','wb'))


    def SVD_model(self):
        """
        Input: Product_popularity, the  User Product Binary Matrix which has been created through the (Product_matrix function)
        output correlation matrix using PCA (SVD) with 50 Components
        corr_mat.pkl 
        """
        
        
        
        X=self.Product_popularity.T
        SVD = TruncatedSVD(n_components=50, random_state=0) # the matrix will have 12 dimantion , dimandion reduction from 943 to 12 
        resultant_matrix = SVD.fit_transform(X)
        self.corr_mat = np.corrcoef(resultant_matrix)
        self.Product_list=self.Product_popularity.columns
        pickle.dump(self.corr_mat, open(self.path+'corr_mat.pkl','wb'))
        pickle.dump(self.Product_list, open(self.path+'Product_list.pkl','wb'))
    def ML_model(self):
        """
        Input : Product_popularity Matrix which has been created through the (Product_matrix function)
        Train the KNN Model using KNN user limit ( defaut =100) 
        save the traing model as a KNN.pkl
       
        
        """
        
        
        df=pd.merge(self.Product_popularity.reset_index(),self.df_C_NPS_Extend , on=self.CustomerCIF, how="left").fillna(0)

        df=df.set_index(self.CustomerCIF)
        X=df.iloc[:,:].values
        nbrs = NearestNeighbors(n_neighbors=self.knn_neighbors).fit(X)
        pickle.dump(nbrs, open(self.path+'KNN.pkl','wb'))
        pickle.dump(df, open(self.path+'df_product_user.pkl','wb'))

        #return nbrs
    def ML_product_neighbors(self):
        """
        Input : df_C_Per_Product​:Dataset including Product information like Id, name, domain, popularity, count" 
        Train the KNN Model using KNN user limit ( defaut =100) 
        save the traing model as a PR_KNN.pkl
        """
        
        scaler = MinMaxScaler()
        Product_matrix =self.df_C_Per_Product.pivot_table(values=self.CustomerCount, index=self.ProductCode,
                                                                            columns=self.pr_category, fill_value=0)
        scaler.fit(Product_matrix[Product_matrix.columns.tolist()])
        self.product_df=pd.DataFrame(columns=Product_matrix.columns.tolist(),
                                   index=Product_matrix.index,
                                   data=scaler.transform(Product_matrix[Product_matrix.columns.tolist()]))
        
        
        X = self.product_df.iloc[:,:].values
        nbrs = NearestNeighbors(n_neighbors=2).fit(X)
        pickle.dump(nbrs, open(self.path+'PR_KNN.pkl','wb'))
        pickle.dump(self.product_df, open(self.path+'product_df.pkl','wb'))

    def User_info(self):

        self.df_C_NPS_Extend[[self.ResponseDate]] = self.df_C_NPS_Extend[[self.ResponseDate]].apply(pd.to_datetime)

        self.df_C_NPS_Extend["year"]=self.df_C_NPS_Extend[self.ResponseDate].dt.year

        b=self.df_C_NPS_Extend.groupby([self.CustomerCIF,"year"]).aggregate({self.StatedIncome:'mean', self.CustomerScore:'mean'}).groupby(self.CustomerCIF).aggregate({self.StatedIncome:'mean', self.CustomerScore:'mean'})
        b[self.CustomerScore]=b[self.CustomerScore].apply(lambda x: Scor_calcualt(x))
        b[self.StatedIncome].mask(b[self.StatedIncome] >= 250000, 250000, inplace=True)#Income adjustment 

        self.df_C_NPS_Extend=b

        self.df_C_NPS_Extend=self.df_C_NPS_Extend.reset_index()
        incom_scaler=MinMaxScaler()
        incom_scaler.fit(self.df_C_NPS_Extend[[self.StatedIncome]])
        #self.df_C_NPS_Extend=self.df_C_NPS_Extend.reset_index()
        ### remove index column
        self.df_C_NPS_Extend[[self.StatedIncome]]=incom_scaler.transform(self.df_C_NPS_Extend[[self.StatedIncome]])
        
        pickle.dump(self.df_C_NPS_Extend, open(self.path+'df_C_NPS_Extend.pkl','wb'))
        pickle.dump(incom_scaler, open(self.path+'incom_scaler.pkl','wb'))
        
        del b
        


    def Evaluate(self):

        Income=[110000]
        NPS=[0]
        Sample = self.Product_hist.sample(frac=self.Sample_size)
        Tem= {y:{"Product":{x for x in Sample.loc[y].tolist() if x !=0 } } for y in Sample.index.tolist() }#ok
        #print(Tem)

        del Sample
        Acc_rep=dict()
        Accuracy_rep=pd.DataFrame(columns=["Product","Product_count","USER","Popularity_based_suggestion",
                                                         "User_similar","Products_neighbors","Flag"])

        counter=0
        for key in Tem.keys():
            #print(key)
            #print(Tem[key]["Product"])
            pr_list=list(Tem[key]["Product"])
            if len(pr_list) >=4:

                Missing=choice(pr_list)                                

                pr_list.remove(Missing)  
                products=Product_Recommender("test",NEW_USER="True",USER_feature=pr_list+Income+NPS)
                Reprt_list=[Missing]
                #Peprt_list +=[test.Pr_dict[Missing][0]["CustomerCount"]]
                Reprt_list +=[self.Pr_dict[Missing][0]["CustomerCount"]]
                Reprt_list +=[(1 if Missing in y else 0) for y in [list(products.report[KEY].keys()) for KEY in list(products.report.keys())]]
                Reprt_list+=[sum(Reprt_list[2:])] 

                #print(Reprt_list)
                Accuracy_rep.loc[counter]=Reprt_list
                Reprt_list+=[1 if Missing in list(products.report["Popularity_based_suggestion"].keys()) else 0]

                Popularity_based_suggestion=list(products.report["Popularity_based_suggestion"].keys())                 
                User_similar=list(products.report["User_similar"].keys())                                                                   
                #products_neighbors=list(products.report["products_neighbors"].keys())
                counter +=1
            else:
                pass


        Total_ACC=Accuracy_rep["Flag"].value_counts().to_dict()
        PBS_ACC=Accuracy_rep["Popularity_based_suggestion"].value_counts().to_dict()
        U_S_ACC=Accuracy_rep["User_similar"].value_counts().to_dict()
        P_N_ACC=Accuracy_rep["Products_neighbors"].value_counts().to_dict()

        Acc=pd.DataFrame(index=["Popularity_based_suggestion","User_similar","Products_neighbors","Total"],
                                 columns=["Fail","Pass"],
                         data=[
                                [PBS_ACC[0],PBS_ACC[1]],
                                  [U_S_ACC[0],U_S_ACC[1]],
                                   [P_N_ACC[0],P_N_ACC[1]],
                            [Total_ACC[0],Total_ACC[1]+Total_ACC[2]+Total_ACC[3]]])
        print(Acc)
        #Acc.plot.bar(stacked=True)

        Totol_rec=len(Accuracy_rep)


        def Totol_Acc():
            #explode = (0, 0.0, 0.0,0.5)
            Totoal_D={0:.5,1:0.0,2:0.0,3:0}
            explode=[Totoal_D[x] for x in list(Total_ACC)]
            #Totol+ACC_X=[Total_ACC[x]]
            colors = ['darkorange', 'sandybrown', 'darksalmon', 'orangered','chocolate']
            plt.pie(
                list(Total_ACC.values()), 
                labels=list(Total_ACC),
                autopct='%.2f',
                colors=colors,
                explode=explode)


            #plt.axis('equal')
            plt.axis()
        def Model_Acc(df):
            display(df.plot.bar(stacked=True))




        Totol_Acc()

        Model_Acc(Acc)

        self.model_report=Accuracy_rep
        self.ACC_report=Acc
        del Acc
        del Accuracy_rep



        
        
        

#################################



class Product_Recommender:
    def __init__(self,USER_ID,Customer_ID="CustomerCIF",Model_path="./model/",Report_path="./report/",Limit=0.79,
                 Local="True",
                 NEW_USER="False",USER_feature=[]):
        
        if Report_path !="./report/" and Local=="True":
            self.Report_path=folder_inspect(Report_path)
        else:
            self.Report_path=Report_path      
        """
        Product_Recommender( User_ID= User CIF ID. 
        imit=0.8 : the ratio for similarity between products )
        """
        self.UEW_USER=NEW_USER
        self.USER_feature=USER_feature
        self.corr_mat=pickle.load(open(Model_path+'corr_mat.pkl', 'rb'))#matrix
        self.df_C_NPS_Extend=pickle.load(open(Model_path+'df_C_NPS_Extend.pkl', 'rb'))#tabel
        self.df_product_user=pickle.load(open(Model_path+'df_product_user.pkl', 'rb'))
        
        self.KNN=pickle.load(open(Model_path+'KNN.pkl', 'rb'))#model
        self.Pr_dict=pickle.load(open(Model_path+'Pr_dict.pkl', 'rb'))
        self.PR_KNN=pickle.load(open(Model_path+'PR_KNN.pkl', 'rb'))#model
        self.product_df=pickle.load(open(Model_path+'product_df.pkl', 'rb'))#tabel

        
        self.Product_hist=pickle.load(open(Model_path+'Product_hist.pkl', 'rb')) 
        self.Product_list=pickle.load(open(Model_path+'Product_list.pkl', 'rb'))
        self.Product_popularity=pickle.load(open(Model_path+'Product_popularity.pkl', 'rb'))
        self.incom_scaler=pickle.load(open(Model_path+'incom_scaler.pkl', 'rb'))

        self.USER_ID=USER_ID
        self.Limit=Limit
        self.CustomerCIF=Customer_ID
        self.PR_list=[]
        ####### initial #######
        
        self.Product_recommender()
        
    def Product_similarity(self,product):
        """
        input : product cod
        Product_features: will get a row list of product feature, like [Product cod, product class, user count ,...] 
        N_product_index: will retrive the most closet product to the select product using KNN algorithm
        tem =[self.product_df.index.tolist()[y] for y in N_product_index]: 
        will retun the explored Product cod 
        """
        Product_features=self.product_df.loc[product].tolist()# user product info for pr_KNN 
        N_product_index=self.PR_KNN.kneighbors([Product_features])[1][0].tolist()# list of nearast products

        tem =[self.product_df.index.tolist()[y] for y in N_product_index]
        #return N_product_index
        return tem


        

    
    
    def popularity_pr_recommender(self,Product_name):
        """
        corr_Product: claculate the corrolation of the product with all other products
        PR_list: will extract the most related items to the chosen product
        
        
        """
        
        
        
        #print(Product_name)
        Product_l=list(self.Product_list)
        #print(Product_l)
        PR_list=[]
        try:
            Product=Product_l.index(Product_name)
            corr_Product = self.corr_mat[Product]

            #self.PR_list+=list(self.Product_list[(corr_Product < 0.9999) & (corr_Product >= self.Limit)])
            PR_list=list(self.Product_list[(corr_Product < 0.9999) & (corr_Product >= self.Limit)])
            ##########################################33


            #print("pr_list :",PR_list)

        #print(self.PR_list)
        
            return PR_list
        except:
            return PR_list
 
    #def Product_recommender(USER_NAME,Product_popularity,Product_hist):
    
    def USER_info(self):
        print("user_INFO")
        #UEW_USER=="False",USER_feature=[]
    
    def Product_recommender(self):
        """
        Product_features: get a list of user's features 
        user_product: get a list of user's product name 
        
        
        
        
        """        
        self.report=dict() # create the report dict 
        user_product=[]
        if self.UEW_USER=="False":
            Product_features=self.df_product_user.loc[self.USER_ID].tolist()# user data to a list for KNN
            #print(Product_features)
            user_product=[x for x in self.Product_hist.loc[self.USER_ID].tolist() if x !=0]# user product to a list for compare a product

            #print(user_product)
            #self.report["user_product"]=[self.Pr_dict[x][0] for x in user_product]

            self.report["user_product"]={}
            for x in  user_product:
                self.report["user_product"][x]=self.Pr_dict[x][0]   
        else:
            #print("New=============")
            #PR_tem=[1 for x in self.Product_list if x in self.USER_feature[:-2] else 0]
            PR_tem=[1 if x in self.USER_feature[:-2] else 0 for x in self.Product_list]
            #tem=pd.DataFrame(columns=["Incom"],data=[200000])
            tem=pd.DataFrame(columns=["Income"],data=[self.USER_feature[-2]])
            Incom=self.incom_scaler.transform(tem[["Income"]])[0].tolist()
            Product_features=PR_tem+Incom+[0]
            #print("Product_features   ",Product_features)

            
            user_product=self.USER_feature[:-2]
            #print("user_product    ",user_product)
            
            #self.report["user_product"]=[self.Pr_dict[x][0] for x in user_product]

            self.report["user_product"]={}
            for x in  user_product:
                self.report["user_product"][x]=self.Pr_dict[x][0]   
        ######## product similarity:#########################33 NEW #############
     
        self.product_neighbors=Counter([val for sublist in [self.Product_similarity(product) for product in user_product] for val in sublist if val !=0 
                                  and val not in user_product])

                
        #self.report["products_neighbors"]=[self.Pr_dict[x][0] for x in self.product_neighbors.keys()]
        self.report["products_neighbors"]={}
        for x in  self.product_neighbors.keys():
            self.report["products_neighbors"][x]=self.Pr_dict[x][0] 

        N_user_index=self.KNN.kneighbors([Product_features])[1][0].tolist()



        #get the common product 
    
        similar_product= Counter([val for sublist in [self.Product_hist.iloc[y].tolist() for y in N_user_index ] for val in sublist if val !=0 
                                  and val not in user_product])
        #test= Counter([val for sublist in [self.Product_hist.iloc[y].tolist() for y in N_user_index ] for val in sublist if val !=0])
        #print(test)
        #print(user_product)
        #print(int(len(N_user_index)*.30))

        #print( "uesr similarity :",similar_product)
        try:
            max_value=similar_product[max(similar_product, key=similar_product.get)]
        


            similar_product={key:val for key, val in similar_product.items() if val >= int(max_value*0.40)}
        except:
            similar_product={key:val for key, val in similar_product.items()}
        #print(similar_product)

        #Report["User_similar"]=similar_product
        #self.report["User_similar"]=[self.Pr_dict[x][0] for x in similar_product.keys()]

        self.report["User_similar"]={}
        for x in similar_product.keys():
            self.report["User_similar"][x]=self.Pr_dict[x][0]         
        #product_list=user_product+list(similar_product.keys())

        self.suggestion=Counter([val for sublist in [self.popularity_pr_recommender(y) for y in user_product] for val in sublist if 
                              val not in user_product])
        #print(self.suggestion)

        self.suggestion={key:val for key, val in self.suggestion.items() if val >=round(len(user_product)/8) }
        #Report["Popularity_based_suggestion"]=suggestion
        self.tem=[self.Pr_dict[x][0] for x in self.suggestion.keys()]
        
        for i in self.tem:
            self.suggestion[i["ProductCode"]]=i["CustomerCount"]
            
        self.suggestion={k:v for k, v in self.suggestion.items() if v>=self.suggestion[max(self.suggestion, key=self.suggestion.get)]* 0.40}
    
        #self.report["Popularity_based_suggestion"]=[self.Pr_dict[x][0] for x in self.suggestion.keys()]

        self.report["Popularity_based_suggestion"]={}
        for x in self.suggestion.keys():
            self.report["Popularity_based_suggestion"][x]=self.Pr_dict[x][0]
            
        #suggestion
        #pickle.dump(self.df_C_NPS_Extend, open(self.path+'df_C_NPS_Extend.pkl','wb'))
        """with open(self.Report_path+str(self.self.USER_ID)+'_Report.json', 'w') as fp:
            json.dump(self.report, fp)"""
        #return self.report
        #US=self.USER_ID
        with open(self.Report_path+"Report.json", 'w') as fp:
                json.dump(self.report, fp, indent=4)
        
        #return self.report
    






        
