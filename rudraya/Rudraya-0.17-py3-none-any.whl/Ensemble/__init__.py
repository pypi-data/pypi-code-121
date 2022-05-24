class Average_Ensemble:
      def __init__(self,estimators):
          """
            Prediction voting regressor for unfitted estimators.

            Average_Ensemble is an ensemble meta-estimator that fits several base
            regressors, each on the whole dataset. Then it averages the individual
            predictions to form a final prediction.

            Parameters
            ----------
            estimators     : list of (str, estimator) tuples
                             Invoking the ``fit`` method on the ``Average_Ensemble`` will fit clones
                             of those original estimators that will be stored in the class attribute
                             ``self.estimators_``.

            Example:
            ------------
            estimators     : [('rfr', RandomForestRegressor()),('knn', KNeighborsRegressor()),('lr', LinearRegression())]
          """
          import pandas as pd
          import numpy as np 

          self.__model, self.__y_pred_name = [],[]
        
          model_formation = [self.__model.append(f[1]) for f in estimators]
            
          self.__obj = [[] for i in range(len(self.__model))]
        
          model_name = [self.__y_pred_name.append(f[0]) for f in estimators]
            
          self.__y_pred = [[] for j in range(len(self.__model))]
          
          #return __y_pred_name,__model,__obj
     
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
          -----------
          object Fitted estimator.
          """
          model_training = [self.__obj[t].append(k.fit(X_train,y_train)) for t,k in zip(range(len(self.__model)),self.__model)]  
        
      def get_predict(self,X_test):
          """
          Predict regression target for X.

          The predicted regression target of an input sample is computed as the
          mean predicted regression targets of the estimators in the ensemble.

          Parameters
          ----------
          X_test       : {array-like, sparse matrix} of shape (n_samples, n_features)
                          The input samples.

          Returns
          ---------
          y_pred       : ndarray of shape (n_samples,)
                          The predicted values.
          """
          import pandas as pd
          model_prediction = [self.__y_pred[l].append(k[0].predict(X_test)) for l,k in zip(range(len(self.__model)),self.__obj)]
          columns_data = [m[0] for m in self.__y_pred]
          dataset = pd.DataFrame(columns_data).T
          dataset.columns = self.__y_pred_name
          dataset['Avg']=(dataset.sum(axis=1)/dataset.shape[1])
          return dataset['Avg'].values,dataset
    
Average_Ensemble.__doc__

class Weighted_Average_Ensemble:
      def __init__(self,estimators,weights):
          """
          Prediction Weighted_Average_Ensemble for unfitted estimators.

          A Weighted_Average_Ensemble is an ensemble meta-estimator that fits several base
          regressors, each on the whole dataset. Then it averages the individual
          predictions to form a final prediction.

          Parameters
          ----------
          estimators   : list of (str, estimator) tuples
                          Invoking the ``fit`` method on the ``Weighted_Average_Ensemble`` will fit clones
                          of those original estimators that will be stored in the class attribute
                          ``self.estimators_``.

          weights      : array-like of shape (n_regressors,), default=None
                          Sequence of weights (`float` or `int`) to weight the occurrences of
                          predicted values before averaging. Uses uniform weights if `None`.

          Returns      :
                         Returns with estimators.

          Example:
          ------------
          >>> estimators = [('rfr', RandomForestRegressor()),('knn', KNeighborsRegressor()),('lr', LinearRegression())]
          """
          import pandas as pd
          import numpy as np 

          self.__model, self.__y_pred_name = [],[]
        
          model_formation = [self.__model.append(f[1]) for f in estimators]
            
          self.__obj = [[] for i in range(len(self.__model))]
        
          model_name = [self.__y_pred_name.append(f[0]) for f in estimators]
            
          self.__y_pred = [[] for j in range(len(self.__model))]
        
          self.__weights = weights
          
          #return __y_pred_name,__model,__obj
     
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
          ---------
          object Fitted estimator.
          """
          model_training = [self.__obj[t].append(k.fit(X_train,y_train)) for t,k in zip(range(len(self.__model)),self.__model)]  
        
      def get_predict(self,X_test):
          """
          Predict regression target for X.

          The predicted regression target of an input sample is computed as the
          mean predicted regression targets of the estimators in the ensemble.

          Parameters
          ----------
          X_test       : {array-like, sparse matrix} of shape (n_samples, n_features)
                          The input samples.

          Returns
          ---------
          y_pred       : ndarray of shape (n_samples,)
                         The predicted values.
          """
          import pandas as pd
          model_prediction = [self.__y_pred[l].append((k[0].predict(X_test))*n) for l,k,n in zip(range(len(self.__model)),self.__obj,self.__weights)]
            
          columns_data = [m[0] for m in self.__y_pred]
          dataset = pd.DataFrame(columns_data).T
          dataset.columns = self.__y_pred_name
          dataset['Avg']=(dataset.sum(axis=1))
          return dataset['Avg'].values,dataset
    
Weighted_Average_Ensemble.__doc__

class Rank_Weighted_Ensemble:
      def __init__(self,estimators):
          """
          Prediction Rank_Weighted_Ensemble for unfitted estimators.

          A Rank_Weighted_Ensemble is an ensemble meta-estimator that fits several base
          regressors, each on the whole dataset. Then it averages the individual
          predictions to form a final prediction.

          Parameters
          ----------
          estimators     : list of (str, estimator) tuples
                            Invoking the ``fit`` method on the ``Rank_Weighted_Ensemble`` will fit clones
                            of those original estimators that will be stored in the class attribute
                            ``self.estimators_``.
          Returns
          ------------
          estimators   = [('rfr', RandomForestRegressor()),('knn', KNeighborsRegressor()),('lr', LinearRegression())]
          """
          import pandas as pd
          import numpy as np 
          
          self.__model, self.__y_pred_name = [],[]
        
          model_formation = [self.__model.append(f[1]) for f in estimators]
            
          self.__obj = [[] for i in range(len(self.__model))]
        
          model_name = [self.__y_pred_name.append(f[0]) for f in estimators]
            
          self.__y_pred = [[] for j in range(len(self.__model))]
        
          
          
          #return __y_pred_name,__model,__obj
     
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
          -------
          object Fitted estimator.
          """
          model_training = [self.__obj[t].append(k.fit(X_train,y_train)) for t,k in zip(range(len(self.__model)),self.__model)]  
        
      def get_predict(self,X_test,weights):
          """
          Predict regression target for X.

          The predicted regression target of an input sample is computed as the
          mean predicted regression targets of the estimators in the ensemble.

          Parameters
          ----------
          X            : {array-like, sparse matrix} of shape (n_samples, n_features)
                          The input samples.

          weights      : array-like of shape (n_regressors,), default=None
                          Sequence of weights (`float` or `int`) to weight the occurrences of
                          predicted values before averaging. Uses uniform weights if `None`.

          Returns
          -------
          y_pred       : ndarray of shape (n_samples,)
                         The output predicted by enstimators.
                
          """
          import pandas as pd
          self.__weights = weights
          model_prediction = [self.__y_pred[l].append((k[0].predict(X_test))*n) for l,k,n in zip(range(len(self.__model)),self.__obj,self.__weights)]
            
          columns_data = [m[0] for m in self.__y_pred]
          dataset = pd.DataFrame(columns_data).T
          dataset.columns = self.__y_pred_name
          dataset['Avg']=(dataset.sum(axis=1))
          return dataset['Avg'].values,dataset
    
      def get_weights(self,estimators,X_train,X_test,y_train,y_test,threshold=0.5):
            """
            It assigne Weights to individual models of the estimators and Enhanced 
            perforance of the Rank_Weighted_Regression.

            Parameters
            ----------
            estimators     : list of (str, estimator) tuples Invoking the ``fit`` method on the ``Rank_Weighted_Regression`` 
                                 will fit clones of those original estimators that will be stored in the class attribute
                                 ``self.estimators_``.
           
            X_train        : {array-like, sparse matrix} of shape (n_samples, n_features)
                                 The input samples. It is subset of main dataset which represent set of independent Features.
                                 It use for to train the model.

            X_test         :{array-like, sparse matrix} of shape (n_samples, n_features)
                                 The input samples. It is subset of main dataset which represent set of independent Features.
                                 It use for to test the model.
       
            y_train        :{array-like, sparse matrix} of shape (n_samples)
                                 The input samples. It is subset of main dataset which represent target Features.
                                 It use for to train the model.

            y_test         :{array-like, sparse matrix} of shape (n_samples)
                                 The input samples. It is subset of main dataset which represent target Features.
                                 It use for to test the model.

            threshold      : int or float 
                                 default value is 0.5. Its range varies from 0 to 1. It allow model which accuracy > threshold value
                                 to form composite model.

            Returns
            -------
            Modified_weights, Modified_estimators 

            """
            import pandas as pd
            import numpy as np
            list1,list2,list3=[],[],[]
 
            for n in estimators:
                model = n[1]
                print(model)
                model.fit(X_train,y_train)
                pred_y  = model.predict(X_test)
                
                acc  = 1-np.mean(np.square(y_test-pred_y)) /np.mean(np.square(y_test-np.mean(y_test)))
                if acc > threshold:
                
                   list1.append(n[0])
                   list2.append(acc)
                   
            results = pd.DataFrame({"model_name":list1,'accuracy':list2})
            results = results.sort_values("accuracy",ascending=False)
            new     = [f for f in np.arange(1,results.shape[0]+1)]
            new.sort(reverse=True) 

            results['weights'] = new /np.sum(new)

            results.index=results.model_name

            modified_estimators =[]
            for i in results.model_name:
            #print(i)
                for j in range(0,len(estimators)):
                    #print(j)
                    if '{}'.format(i) in estimators[j][0]:
                        #print(estimators[j])
                        modified_estimators.append(estimators[j])
            return results.weights, modified_estimators

Rank_Weighted_Ensemble.__doc__

class VotingEnsemble:
     def __init__(self,estimators):
         """
         Return with classification output using Voting Ensemble Methods.

         Parameters
         -------------

         estimators    : list of (str, estimator) tuples
                         Invoking the ``fit`` method on the ``VotingClassifier`` will fit clones
                         of those original estimators that will be stored in the class attribute
                         ``self.estimators_``. An estimator can be set to ``'drop'`` using ``set_params``.
        
         voting        : {'hard', 'soft'}, default='hard'
                          If 'hard', uses predicted class labels for majority rule voting.
                          Else if 'soft', predicts the class label based on the argmax of
                          the sums of the predicted probabilities, which is recommended for
                          an ensemble of well-calibrated classifiers.
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
            -------
            result       : pandas.DataFrame
                             It returns with table which carry measuring parameters like accuracy, models types.
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
   