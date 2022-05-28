class VotingEnsemble:
     def __init__(self,estimators):
         """
         It gives an classification output using Voting Ensemble Methods.
         """
         import pandas as pd
         import numpy as np  
            
         self.__estimators = estimators
         
         self.__model          = [[] for f in range(0,len(self.__estimators))]
         
         self.__model_training = [[] for f in range(0,len(self.__estimators))]
        
         self.__model_pred     = [[] for f in range(0,len(self.__estimators))]
            
         self.__model_concat   = [[] for f in range(0,len(self.__estimators))]
            
     def get_fit(self,X,y):
         """
          Fit the estimators.

          Parameters
          ------------
          X           : {array-like, sparse matrix} of shape (n_samples, n_features)
                        Training vectors, where n_samples is the number of samples and
                        n_features is the number of features.

          y           : array-like of shape (n_samples,)
                        Target values.

          Returns
          --------
          object Fitted estimator.
         """
         import pandas as pd
         import numpy as np
        
         self.__X = np.array(X)
         self.__y = np.array(y)
        
         self.__model          = [[] for f in range(0,len(self.__estimators))]
         self.__model_training = [[] for f in range(0,len(self.__estimators))]
         
            
         new = [self.__model[interation].append(self.__estimators[interation][1]) for interation in range(0,len(self.__estimators))] 
         
         model_training =[self.__model_training[interation1].append(self.__model[interation1][0].fit(self.__X,self.__y)) for interation1 in range(0,len(self.__estimators))]
         
         return print("VotingEnsemble(estimators={})".format(self.__estimators))
        
     def get_predict(self,X_test):
         """
         Predict class labels for X.

         Parameters
         ----------
         X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                       The input samples.

         Returns
         -------
         y_pred      : array-like of shape (n_samples,)
                       Predicted class labels.
         """
         import pandas as pd
         import numpy as np 
        
         self.__X_test = X_test
         
         self.__model_concat   = [[] for f in range(0,len(self.__estimators))]
         self.__model_pred     = [[] for f in range(0,len(self.__estimators))]
        
         model_pred =[self.__model_pred[interation2].append(self.__model_training[interation2][0].predict_proba(self.__X_test)) for interation2 in range(0,len(self.__estimators))]
        
         for j in range(0,len(self.__estimators)):
             self.__model_concat[j].append([np.argmax(self.__model_pred[j][0][k]) for k in range(0, self.__X_test.shape[0])]) 
         
         
         dataset = pd.concat([pd.DataFrame(self.__model_concat[n][0]) for n in range(0,len(self.__estimators))],axis=1)
         
         self.__prediction = []
         for m in range(0, self.__X_test.shape[0]):
             arr = np.array(dataset)[m]
             new = [f1 for f1 in arr] 
             count1 = [new.count(k) for k in np.unique(new)]
             pred   = np.argmax(np.bincount(np.unique(new),np.array(count1)/len(arr)))   
             self.__prediction.append(pred)
         return np.array(self.__prediction)

     def get_plot(self,true,pred,X_labels,y_labels,cmap_index=3,figsize=(10,10),title='VotingClassifier'):
            """
            It Evaluates performance of Classification models using confusion Matrix and
            classification reports and represents it in graphical format.

            Parameters
            ----------
            true         : array* with an "n_samples" that indicates actual values of target features.
                           Note: length of the true and predicted value should be same otherwise error will pop up. 

            pred         : array* with an "n_samples" that indicates an predicted value of target feature
                           which accuracy are need to be check.

            X_labels     : list of the features that assigned to the predictor sets.

            y_labels     : list of the features that assigned to the target sets.

            cmap_index   : It represents cmap values. default all values are all ready defines, it only required to access it.
                           The maximum count of the cmap feature is 175 and minimum count is 0. 
                           use value which varies between 0 and 175.

            figsize      : It adjusts size of the graph/figure by passing integer values. 
                           It required to be defines value in (row,columns) format.
                           Default: figsize = (10,10)

            title        : It define title which assigned at the top of the graph/plots.

            Returns
            -------
            It returns classification reports in graphical format.

            """
            import matplotlib.pyplot as plt
            import seaborn as sns
            import numpy as np
            from sklearn import metrics
            import matplotlib.pyplot as plt
            import seaborn as sns  
            
            self.__m,self.__n= figsize[0],figsize[1]

            self.__Xlabels = X_labels
            self.__ylabels = y_labels
            #self.__dpi     = dpi
            self.__title   = title
            #self.__savefile = savefile

            self.__true = np.array(true).reshape(-1,1)
            self.__pred = np.array(pred).reshape(-1,1)

            cmap=['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap',
                'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r',
                'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r',
                'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples',
                'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r',
                'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia',
                'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot',
                'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 
                'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'crest', 'crest_r',
                'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'flare', 'flare_r', 'gist_earth', 'gist_earth_r', 'gist_gray',
                'gist_gray_r', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r',
                'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r',
                'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'icefire', 'icefire_r', 'inferno', 'inferno_r', 'jet',
                'jet_r', 'magma', 'magma_r', 'mako', 'mako_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 
                'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'rocket', 'rocket_r', 
                'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r',
                'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r',
                'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'vlag', 'vlag_r', 'winter', 'winter_r']
            # cmap has maximum length 178.
            self.__cmap = cmap    
  
            plt.figure(figsize=(self.__m,self.__n))
            cm = metrics.confusion_matrix(self.__true,self.__pred)    

            sns.heatmap(cm,annot=True,
                               cmap=self.__cmap[cmap_index],
                               fmt='g',
                               xticklabels=self.__Xlabels,
                               yticklabels=self.__ylabels)
            plt.title(self.__title)

VotingEnsemble.__doc__

class Stack_Regression:
      def __init__(self,estimator,final_estimator,cv=10):   
            """
            Parameters
            -----------
            estimators : list of (str, estimator)
                         Base estimators which will be stacked together. Each element of the
                         list is defined as a tuple of string (i.e. name) and an estimator
                         instance. An estimator can be set to 'drop' using `set_params`.

            final_estimator : estimator, default=None
                             A regressor which will be used to combine the base estimators.
                             The default regressor is a `RidgeCV`.

            cv             : int, cross-validation generator or an iterable, default=None
                             Determines the cross-validation splitting strategy used in
                             `cross_val_predict` to train `final_estimator`.
            """         
            self.__estimator   = estimator 
            self.__final_model = final_estimator
            self.__cv = cv
            self.__list1,self.__list2,self.__list3 =[],[],[]
            self.__list11,self.__list12 =[],[] 
            
      def get_fit(self,X_train,y_train): 
            """
            Fit the estimators.

            Parameters
            ----------
            X_train      : {array-like, sparse matrix} of shape (n_samples, n_features)
                            Training vectors, where n_samples is the number of samples and
                            n_features is the number of features.

            y_train      : array-like of shape (n_samples,)
                            Target values.

            Returns
            --------
            object Fitted estimator.
            """
            import pandas as pd
            import random
            from sklearn import metrics
            import numpy as np       
            self.__X_train = X_train
            self.__y_train = y_train
            
            pred_train   = [[] for f4 in range(0,self.__cv)]
            actual_train = [[] for f4 in range(0,self.__cv)]
            

            self.__dummuy_train = [[] for f0 in range(0,self.__cv)]
            self.__dummuy_test  = [[] for f1 in range(0,self.__cv)] 
            
            dummuy1_train  = [[] for f3 in range(0,len(self.__estimator))]
            dummuy1_test   = [[] for f4 in range(0,len(self.__estimator))]

            for i in range(0,self.__cv):
                new = [f for f in self.__X_train.index.values]
                random_test = random.sample(new,int(len(self.__X_train.index.values)/10))
                random_train = self.__X_train.index[~self.__X_train.index.isin(random_test)].values
                #print(len(random_train))
                self.__dummuy_test[i].append(random_test)
                self.__dummuy_train[i].append(random_train) 

            for n_model,p in zip(self.__estimator,range(0,len(self.__estimator))):
                        
                for n in range(0,self.__cv): 
                    x_test  = self.__X_train[self.__X_train.index.isin(self.__dummuy_test[n][0])]
                    x_train = self.__X_train[self.__X_train.index.isin(self.__dummuy_train[n][0])]

                    Y_test   = self.__y_train[self.__y_train.index.isin(self.__dummuy_test[n][0])]
                    Y_train  = self.__y_train[self.__y_train.index.isin(self.__dummuy_train[n][0])]
                    
                    n_model[1].fit(x_train,Y_train)
                    
                    y_pred_train = n_model[1].predict(x_test)
                    #print(n_model[1],p,n,len(y_pred_train))
                    
                    pred_train[n].append(y_pred_train)
                    actual_train[n].append(Y_test)
                    
                    self.__list1.append(n)
                    self.__list2.append('{}'.format(n_model[1]))
                    self.__list3.append(metrics.r2_score(Y_test,y_pred_train)) 
                         
                x1 = np.concatenate([pred_train[n1][0] for n1 in range(0,self.__cv)])
                x2 = np.concatenate([actual_train[n2][0] for n2 in range(0,self.__cv)])  
                
                dummuy1_train[p].append(x1)
                dummuy1_test[p].append(x2)  
                
                pred_train   = [[] for f4 in range(0,self.__cv)]
                actual_train = [[] for f4 in range(0,self.__cv)] 


            summary_result =pd.DataFrame({"Iteration":self.__list1,
                                          "models":self.__list2,
                                          'Accuracy':self.__list3})
            
            self.__sample_train_dataset = pd.DataFrame({})             
            for iteration1, label1 in zip(range(0,len(self.__estimator)),self.__estimator):                                         
                self.__sample_train_dataset['{}'.format(label1[0])] = dummuy1_train[iteration1][0]                                         
            self.__sample_train_dataset['actual'] = dummuy1_test[0][0] 
            
            print(self.__sample_train_dataset)
            
            number_models = np.unique(summary_result.models.values)                              
            for interation2 in number_models:
                 self.__list11.append(interation2)
                 self.__list12.append(summary_result[summary_result.models=='{}'.format(interation2)].Accuracy.mean())                          
            
            self.__model_performance = pd.DataFrame({"Models":self.__list11,
                                                     "Accuracy":self.__list12})
            #return dummuy1_train,dummuy1_test

      def selected_model_performance(self): 
          """
          Return with model performance report. It explains individual model contribution
          in predicting target feature by considering model performance evaluating parameters.
          """   
          return self.__model_performance
                                           
      def get_predict(self,X_test): 
            """
            Predict class labels for X.

            Parameters
            ----------
            X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                        The input samples.

            Returns
            -------
            y_pred      : array-like of shape (n_samples,)
                        Predicted class labels.
            """
            import pandas as pd
            import numpy as np

            self.__X_test  = X_test
           
            pred_test   = [[] for f4 in range(0,len(self.__estimator))]
            actual_test = [[] for f4 in range(0,len(self.__estimator))]
                                           
            for mymodel, m in zip(self.__estimator,range(0,len(self.__estimator))):
                mymodel[1].fit(self.__X_train,self.__y_train)
                y_pred_test = mymodel[1].predict(self.__X_test)
                pred_test[m].append(list(y_pred_test))
                #actual_test[m].append(list(y_test))
            
            self.__sample_test_dataset = pd.DataFrame({}) 
            for iteration, label in zip (range(0,len(self.__estimator)),self.__estimator):                                         
                self.__sample_test_dataset['{}'.format(label[0])] = pred_test[iteration][0]                                         
            print(self.__sample_test_dataset)
                                         
            train_X = self.__sample_train_dataset.iloc[:,:-1]                                        
            train_y = self.__sample_train_dataset.iloc[:,-1]
                                         
            test_X = self.__sample_test_dataset
                                         
            self.__final_model.fit(train_X,train_y) 
            self.__final_pred = self.__final_model.predict(test_X)
                                         
            return self.__final_pred
Stack_Regression.__doc__

class blending:
      def __init__(self,estimator,final_estimator,cv=10):  
            """
            Parameters
            -----------
            estimators : list of (str, estimator)
                         Base estimators which will be stacked together. Each element of the
                         list is defined as a tuple of string (i.e. name) and an estimator
                         instance. An estimator can be set to 'drop' using `set_params`.

            final_estimator : estimator, default=None
                             A regressor which will be used to combine the base estimators.
                             The default regressor is a `RidgeCV`.

            cv             : int, cross-validation generator or an iterable, default=None
                             Determines the cross-validation splitting strategy used in
                             `cross_val_predict` to train `final_estimator`.
            """           
            self.__estimator   = estimator 
            self.__final_model = final_estimator
            self.__cv = cv
            self.__list1,self.__list2,self.__list3 =[],[],[]
            self.__list11,self.__list12 =[],[] 
            
      def get_fit(self,X_train,y_train,validation_size=0.33):
            """
            Fit the estimators.

            Parameters
            ----------
            X_train         :{array-like, sparse matrix} of shape (n_samples, n_features)
                              Training vectors, where n_samples is the number of samples and
                              n_features is the number of features.

            y_train         : array-like of shape (n_samples,)
                              Target values.

            validation_size : array-like of shape (n_samples,)
                              Target values.

            Returns
            --------
            object Fitted estimator.
            """
            import random
            import pandas as pd
            import numpy as np
            from sklearn import metrics        
            self.__X_train = X_train
            self.__y_train = y_train
            self.__validation_size = validation_size
            #print(self.__X_train)
            pred_train   = [[] for f4 in range(0,self.__cv)]
            actual_train = [[] for f4 in range(0,self.__cv)]
            

            self.__dummuy_train = [[] for f0 in range(0,self.__cv)]
            self.__dummuy_test  = [[] for f1 in range(0,self.__cv)] 
            
            dummuy1_train  = [[] for f3 in range(0,len(self.__estimator))]
            dummuy1_test   = [[] for f4 in range(0,len(self.__estimator))]

            raw_index = [f for f in self.__X_train.index]
            #print(raw_index )
            val_index = random.sample(raw_index, int(len(raw_index)*self.__validation_size))
            self.__X_val = self.__X_train[self.__X_train.index.isin(val_index)]
            self.__y_val = self.__y_train[self.__y_train.index.isin(val_index)]
            #print(self.__X_val,self.__y_val)
            
            for i in range(0,self.__cv):
                new = [f for f in self.__X_val.index.values]
                random_test = random.sample(new,int(len(self.__X_val.index.values)/10))
                random_train = self.__X_val.index[~self.__X_val.index.isin(random_test)].values
                #print(len(random_train))
                self.__dummuy_test[i].append(random_test)
                self.__dummuy_train[i].append(random_train) 

            for n_model,p in zip(self.__estimator,range(0,len(self.__estimator))):
                        
                for n in range(0,self.__cv): 
                    x_test  = self.__X_val[self.__X_val.index.isin(self.__dummuy_test[n][0])]
                    x_train = self.__X_val[self.__X_val.index.isin(self.__dummuy_train[n][0])]

                    Y_test   = self.__y_val[self.__y_val.index.isin(self.__dummuy_test[n][0])]
                    Y_train  = self.__y_val[self.__y_val.index.isin(self.__dummuy_train[n][0])]
                    
                    n_model[1].fit(x_train,Y_train)
                    
                    y_pred_train = n_model[1].predict(x_test)
                    #print(n_model[1],p,n,len(y_pred_train))
                    
                    pred_train[n].append(y_pred_train)
                    actual_train[n].append(Y_test)
                    
                    self.__list1.append(n)
                    self.__list2.append('{}'.format(n_model[1]))
                    self.__list3.append(metrics.r2_score(Y_test,y_pred_train)) 
                         
                x1 = np.concatenate([pred_train[n1][0] for n1 in range(0,self.__cv)])
                x2 = np.concatenate([actual_train[n2][0] for n2 in range(0,self.__cv)])  
                
                dummuy1_train[p].append(x1)
                dummuy1_test[p].append(x2)  
                
                pred_train   = [[] for f4 in range(0,self.__cv)]
                actual_train = [[] for f4 in range(0,self.__cv)] 


            summary_result =pd.DataFrame({"Iteration":self.__list1,
                                          "models":self.__list2,
                                          'Accuracy':self.__list3})
            
            self.__sample_train_dataset = pd.DataFrame({})             
            for iteration1, label1 in zip(range(0,len(self.__estimator)),self.__estimator):                                         
                self.__sample_train_dataset['{}'.format(label1[0])] = dummuy1_train[iteration1][0]                                         
            self.__sample_train_dataset['actual'] = dummuy1_test[0][0] 
            
            print(self.__sample_train_dataset,self.__sample_train_dataset.shape)
            
            number_models = np.unique(summary_result.models.values)                              
            for interation2 in number_models:
                 self.__list11.append(interation2)
                 self.__list12.append(summary_result[summary_result.models=='{}'.format(interation2)].Accuracy.mean())                          
            
            self.__model_performance = pd.DataFrame({"Models":self.__list11,
                                                     "Accuracy":self.__list12})
            #return dummuy1_train,dummuy1_test

      def selected_model_performance(self):
          """
          Return with model performance report. It explains individual model contribution
          in predicting target feature by considering model performance evaluating parameters.
          """       
          return self.__model_performance
                                           
      def get_predict(self,X_test): 
            """
            Predict class labels for X.

            Parameters
            ----------
            X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                        The input samples.

            Returns
            -------
            y_pred      : array-like of shape (n_samples,)
                        Predicted class labels.
            """
            import pandas as pd
            import numpy as np
            self.__X_test  = X_test
           
            pred_test   = [[] for f4 in range(0,len(self.__estimator))]
            actual_test = [[] for f4 in range(0,len(self.__estimator))]
                                           
            for mymodel, m in zip(self.__estimator,range(0,len(self.__estimator))):
                mymodel[1].fit(self.__X_train,self.__y_train)
                y_pred_test = mymodel[1].predict(self.__X_test)
                pred_test[m].append(list(y_pred_test))
                #actual_test[m].append(list(y_test))
            
            self.__sample_test_dataset = pd.DataFrame({}) 
            for iteration, label in zip (range(0,len(self.__estimator)),self.__estimator):                                         
                self.__sample_test_dataset['{}'.format(label[0])] = pred_test[iteration][0]                                         
            print(self.__sample_test_dataset)
                                         
            train_X = self.__sample_train_dataset.iloc[:,:-1]                                        
            train_y = self.__sample_train_dataset.iloc[:,-1]
                                         
            test_X = self.__sample_test_dataset
                                         
            self.__final_model.fit(train_X,train_y) 
            self.__final_pred = self.__final_model.predict(test_X)
                                         
            return self.__final_pred
blending.__doc__   

class Average_Ensemble:
      def __init__(self,estimators):
          """
          Parameters
          -----------
          estimators : list of (str, estimator)
                         Base estimators which will be stacked together. Each element of the
                         list is defined as a tuple of string (i.e. name) and an estimator
                         instance. An estimator can be set to 'drop' using `set_params`.
          """ 
          import pandas as pd
          import numpy as np
            
          self.__estimators = estimators
          self.__model,self.__name,self.__save_model,self.__y_pred =[],[],[],[]
          new1 = [self.__model.append(f[1]) for f in estimators]
          new2 = [self.__name.append(f1[0]) for f1 in estimators] 
          print(self.__model,self.__name)
        
      def get_fit(self,X_train,y_train): 
          """
          Fit the estimators.

          Parameters
          ----------
          X_train      : {array-like, sparse matrix} of shape (n_samples, n_features)
                            Training vectors, where n_samples is the number of samples and
                            n_features is the number of features.

          y_train      : array-like of shape (n_samples,)
                            Target values.

          Returns
          --------
          object Fitted estimator.
          """
          import pandas as pd
          import numpy as np
        
          self.__save_model =[]
          new3 = [self.__save_model.append(f2.fit(X_train,y_train)) for f2 in self.__model]
          print(self.__save_model)
            
      def get_predict(self,X_test):
          """
          Predict class labels for X.

          Parameters
          ----------
          X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                        The input samples.

          Returns
          -------
          y_pred      : array-like of shape (n_samples,)
                        Predicted class labels.
          """
          import pandas as pd
          import numpy as np
        
          self.__y_pred = []
          new4 = [self.__y_pred.append(f3.predict(X_test)) for f3 in self.__save_model]
          dataset = pd.DataFrame(self.__y_pred).T
          dataset.columns = self.__name
          dataset['avg'] = dataset.mean(axis=1).values
          self.__dataset = dataset
          return self.__dataset['avg']

      def get_report(self,X_test):
          """
          Predict class labels for X.

          Parameters
          ----------
          X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                        The input samples.

          Returns
          -------
          summary     : pandas.dataframe
                        It represents individual model gives prediction with final predicted output.
          """
          import pandas as pd
          import numpy as np
        
          self.__y_pred = []
          new4 = [self.__y_pred.append(f3.predict(X_test)) for f3 in self.__save_model]
          dataset = pd.DataFrame(self.__y_pred).T
          dataset.columns = self.__name
          dataset['avg'] = dataset.mean(axis=1).values
          self.__dataset = dataset
          return self.__dataset 

Average_Ensemble.__doc__ 

class Weighted_Average_Ensemble:
      def __init__(self,estimators):
          """
          Parameters
          -----------
          estimators : list of (str, estimator)
                         Base estimators which will be stacked together. Each element of the
                         list is defined as a tuple of string (i.e. name) and an estimator
                         instance. An estimator can be set to 'drop' using `set_params`.
          """ 
          import pandas as pd
          import numpy as np
            
          self.__estimators = estimators
          self.__model,self.__name,self.__save_model,self.__y_pred =[],[],[],[]
          new1 = [self.__model.append(f[1]) for f in estimators]
          new2 = [self.__name.append(f1[0]) for f1 in estimators] 
          print(self.__model,self.__name)
        
      def get_fit(self,X_train,y_train,weights): 
          """
          Fit the estimators.

          Parameters
          ----------
          X_train      : {array-like, sparse matrix} of shape (n_samples, n_features)
                            Training vectors, where n_samples is the number of samples and
                            n_features is the number of features.

          y_train      : array-like of shape (n_samples,)
                            Target values.

          weights      : list or array
                           It assigned given weights to individual modes. 

          Returns
          --------
          object Fitted estimator.
          """          
          import pandas as pd
          import numpy as np
        
          self.__save_model =[]
          self.__weights = weights
          new3 = [self.__save_model.append(f2.fit(X_train,y_train)) for f2 in self.__model]
          print(self.__save_model)
            
      def get_predict(self,X_test):
          """
          Predict class labels for X.

          Parameters
          ----------
          X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                        The input samples.

          Returns
          -------
          y_pred      : array-like of shape (n_samples,)
                        Predicted class labels.
          """
          import pandas as pd
          import numpy as np
        
          self.__y_pred = []
          new4 = [self.__y_pred.append(f3.predict(X_test)) for f3 in self.__save_model]
          dataset = pd.DataFrame(self.__y_pred).T
          dataset.columns = self.__name
          dataset.multiply(self.__weights)
          dataset['avg'] = dataset.mean(axis=1).values
          self.__dataset = dataset
          return self.__dataset['avg']

      def get_report(self,X_test):
          """
          Predict class labels for X.

          Parameters
          ----------
          X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                        The input samples.

          Returns
          -------
          summary     : pandas.dataframe
                        It represents individual model gives prediction with final predicted output.
          """
          import pandas as pd
          import numpy as np
            
          self.__y_pred = []
          new4 = [self.__y_pred.append(f3.predict(X_test)) for f3 in self.__save_model]
          dataset = pd.DataFrame(self.__y_pred).T
          dataset.columns = self.__name
          dataset.multiply(self.__weights)
          dataset['avg'] = dataset.mean(axis=1).values
          self.__dataset = dataset
          return self.__dataset 

Weighted_Average_Ensemble.__doc__ 

class Rank_Weighted_Ensemble:
      def __init__(self,estimators):
          """
          Parameters
          -----------
          estimators : list of (str, estimator)
                         Base estimators which will be stacked together. Each element of the
                         list is defined as a tuple of string (i.e. name) and an estimator
                         instance. An estimator can be set to 'drop' using `set_params`.
          """ 
          import pandas as pd
          import numpy as np
            
          self.__estimators = estimators
          self.__model,self.__name,self.__save_model,self.__y_pred =[],[],[],[]
          new1 = [self.__model.append(f[1]) for f in estimators]
          new2 = [self.__name.append(f1[0]) for f1 in estimators] 
          print(self.__model,self.__name)
        
      def get_weights(self,estimators,X_train,X_test,y_train,y_test):
          """
          Fit the estimators.

          Parameters
          ----------
          estimators   : (list of (str, estimator) tuples Invoking the fit method on the ``Rank_Weighted_Regression``) 
                           will fit clones of those original estimators that will be stored in the class attribute ``self.estimators_``

          X_train      : {array-like, sparse matrix} of shape (n_samples, n_features)
                            Training vectors, where n_samples is the number of samples and
                            n_features is the number of features.

          y_train      : array-like of shape (n_samples,)
                            Target values.
          X_train      : ({array-like, sparse matrix} of shape (n_samples, n_features)) 
                         The input samples. It is subset of main dataset which represent set of independent Features. 
                         It use for to train the model.

          X_test       : ({array-like, sparse matrix} of shape (n_samples, n_features))
                          The input samples. It is subset of main dataset which represent set of independent Features. 
                          It use for to test the model.

          y_train      : ({array-like, sparse matrix} of shape (n_samples)) 
                          The input samples. It is subset of main dataset which represent target Features. 
                          It use for to train the model.

          y_test       :({array-like, sparse matrix} of shape (n_samples)) 
                         The input samples. It is subset of main dataset which represent target Features. 
                         It use for to test the model.
          
          Returns
          --------
          object Fitted estimator.

          """
          import pandas as pd
          import numpy as np
        
          self.__save_model,self.__result  =[],[]
            
          self.__up_model,self.__up_name = [],[]
        
          new3 = [self.__save_model.append(f2.fit(X_train,y_train)) for f2 in self.__model]   
            
          self.__y_pred = []
          new4 = [self.__y_pred.append(f3.predict(X_test)) for f3 in self.__save_model]
          dataset = pd.DataFrame(self.__y_pred).T
          dataset.columns = self.__name  

          def r2_score(true,pred):
              return 1-np.mean(np.square(true-pred)) /np.mean(np.square(true-np.mean(true)))
            
          #self.__result = []
          new5 = [self.__result.append((r2_score(y_test,dataset.iloc[:,j].values),'{}'.format(k))) for j,k in zip(range(0,dataset.shape[1]),dataset.columns)]
          #print(self.__result)
          
          for p in self.__result:
              self.__up_model.append(p[0])
              self.__up_name.append(p[1])
          self.__myresult = pd.DataFrame({'model':self.__up_name,'acc':self.__up_model})
          self.__myresult = self.__myresult.sort_values('acc',ascending=False)
          rank = list(np.arange(1,dataset.shape[1]+1))
          rank.sort(reverse=True)
          self.__myresult['weights']=rank/sum(rank)
          #print(self.__myresult)
          return self.__myresult
        
      def get_fit(self,X_train,y_train,weights): 
          """
          Fit the estimators.

          Parameters
          ----------
          X_train      : {array-like, sparse matrix} of shape (n_samples, n_features)
                            Training vectors, where n_samples is the number of samples and
                            n_features is the number of features.

          y_train      : array-like of shape (n_samples,)
                            Target values.

          weights      : list or array
                           It assigned given weights to individual modes. 

          Returns
          --------
          object Fitted estimator.
          """ 
          import pandas as pd
          import numpy as np
        
          self.__save_model =[]
          self.__weights = weights
          new3 = [self.__save_model.append(f2.fit(X_train,y_train)) for f2 in self.__model]
          print(self.__save_model)
            
      def get_predict(self,X_test):
          """
          Predict class labels for X.

          Parameters
          ----------
          X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                        The input samples.

          Returns
          -------
          y_pred      : array-like of shape (n_samples,)
                        Predicted class labels.
          """
          import pandas as pd
          import numpy as np
        
          self.__y_pred = []
          new4 = [self.__y_pred.append(f3.predict(X_test)) for f3 in self.__save_model]
          dataset = pd.DataFrame(self.__y_pred).T
          dataset.columns = self.__name
          dataset.multiply(self.__weights)
          dataset['avg'] = dataset.mean(axis=1).values
          self.__dataset = dataset
          return self.__dataset['avg']

      def get_report(self,X_test):
          """
          Predict class labels for X.

          Parameters
          ----------
          X_test      : {array-like, sparse matrix} of shape (n_samples, n_features)
                        The input samples.

          Returns
          -------
          summary     : pandas.dataframe
                        It represents individual model gives prediction with final predicted output.
          """
          import pandas as pd
          import numpy as np
            
          self.__y_pred = []
          new4 = [self.__y_pred.append(f3.predict(X_test)) for f3 in self.__save_model]
          dataset = pd.DataFrame(self.__y_pred).T
          dataset.columns = self.__name
          dataset.multiply(self.__weights)
          dataset['avg'] = dataset.mean(axis=1).values
          self.__dataset = dataset
          return self.__dataset 

Rank_Weighted_Ensemble.__doc__