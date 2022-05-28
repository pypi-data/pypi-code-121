class Evaluate:
      def __init__(self):
          pass

      def mean_absolute_error(self,true,pred):
          """
          Mean absolute error regression loss

          Parameters
          ----------
          y_true        : array-like of shape (n_samples,) or (n_samples, n_outputs)
                            Ground truth (correct) target values.

          y_pred        : array-like of shape (n_samples,) or (n_samples, n_outputs)
                            Estimated target values.

          Returns
          -------
          loss          : float or ndarray of floats
                            If multioutput is 'raw_values', then mean absolute error is returned
                            for each output separately.
                            If multioutput is 'uniform_average' or an ndarray of weights, then the
                            weighted average of all output errors is returned.

          MAE output is non-negative floating point. The best value is 0.0.

          where, ytrue is true value and ypred is predicted values.

          Examples
          --------
                    >>> y_true = [3, -0.5, 2, 7]
                    >>> y_pred = [2.5, 0.0, 2, 8]
                    >>> mean_absolute_error(y_true, y_pred)
          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)
          mae  = np.mean(np.abs(true-pred))
          return mae

      def mean_square_error(self,true,pred):
          """
            Mean squared error regression loss

            Parameters
            ----------
            y_true      : array-like of shape (n_samples,) or (n_samples, n_outputs)
                          Ground truth (correct) target values.

            y_pred      : array-like of shape (n_samples,) or (n_samples, n_outputs)
                          Estimated target values.

            Returns
            -------
            loss        : float or ndarray of floats
                          A non-negative floating point value (the best value is 0.0), or an
                          array of floating point values, one for each individual target.

            where, ytrue is true value and ypred is predicted values.

            Examples
            --------
                    >>> y_true = [3, -0.5, 2, 7]
                    >>> y_pred = [2.5, 0.0, 2, 8]
                    >>> mean_squared_error(y_true, y_pred)
          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)
          mse  = np.mean(np.square(true-pred))
          return mse
    
      def root_mean_square(self,true,pred):
          """
            Root Mean squared error regression loss

            Parameters
            ----------
            y_true      : array-like of shape (n_samples,) or (n_samples, n_outputs)
                          Ground truth (correct) target values.

            y_pred      : array-like of shape (n_samples,) or (n_samples, n_outputs)
                          Estimated target values.

            Returns
            -------
            loss        : float or ndarray of floats
                          A non-negative floating point value (the best value is 0.0), or an
                          array of floating point values, one for each individual target.

            where, ytrue is true value and ypred is predicted values.

            Examples
            --------
                    >>> y_true = [3, -0.5, 2, 7]
                    >>> y_pred = [2.5, 0.0, 2, 8]
                    >>> root_mean_squared(y_true, y_pred)
          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)
          mse  = np.mean(np.square(true-pred))
          rmse = np.sqrt(mse)  
          return rmse
        
      def mean_absolute_percentage_error(self,true,pred):
          """
            Mean absolute percentage error regression loss

            Parameters
            ----------
            y_true      : array-like of shape (n_samples,) or (n_samples, n_outputs)
                          Ground truth (correct) target values.

            y_pred      : array-like of shape (n_samples,) or (n_samples, n_outputs)
                          Estimated target values.

            Returns
            -------
            loss        : float or ndarray of floats
                          A non-negative floating point value (the best value is 0.0), or an
                          array of floating point values, one for each individual target.

            where, ytrue is true value and ypred is predicted values.

            Examples
            --------
                    >>> y_true = [3, -0.5, 2, 7]
                    >>> y_pred = [2.5, 0.0, 2, 8]
                    >>> mean_absolute_percentage_error(y_true, y_pred)
          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)          
          mape = np.mean(np.abs(true-pred)/true)*100
          return mape

      def r2_score(self,true,pred):
          """
            R^2 (coefficient of determination) regression score function.

            Best possible score is 1.0 and it can be negative (because the
            model can be arbitrarily worse). A constant model that always
            predicts the expected value of y, disregarding the input features,
            would get a R^2 score of 0.0.

            Parameters
            ----------
            y_true     : array-like of shape (n_samples,) or (n_samples, n_outputs)
                         Ground truth (correct) target values.

            y_pred     : array-like of shape (n_samples,) or (n_samples, n_outputs)
                         Estimated target values.

            Returns
            -------
            z          : float or ndarray of floats
                         The R^2 score or ndarray of scores if 'multioutput' is
                         'raw_values'.

            Notes
            -----
            This is not a symmetric function.

            Unlike most other scores, R^2 score may be negative (it need not actually
            be the square of a quantity R).

            This metric is not well-defined for single samples and will return a NaN
            value if n_samples is less than two.

            Examples
            --------
                    >>> y_true = [3, -0.5, 2, 7]
                    >>> y_pred = [2.5, 0.0, 2, 8]
                    >>> r2_score(y_true, y_pred)
          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)  
          r2   = 1-np.mean(np.square(true-pred))/np.mean(np.square(true-np.mean(true)))
          return r2

      def explained_variance_score(self,true,pred):
          """
            Return with Explained Variance Socre.

            The explained variance score explains the dispersion of errors of a given dataset,
            and the formula is written as follows: Here, and Var(y) is the variance of prediction
            errors and actual values respectively. Scores close to 1.0 are highly desired, indicating
            better squares of standard deviations of errors.

            Parameters
            ----------
            y_true    : array-like of shape (n_samples,) or (n_samples, n_outputs)
                        Ground truth (correct) target values.

            y_pred    : array-like of shape (n_samples,) or (n_samples, n_outputs)
                        Estimated target values.

            Returns
            -------
            score    : float or ndarray of floats
                    The explained variance or ndarray if 'multioutput' is 'raw_values'.

            Notes
            -----
                    This is not a symmetric function.
                    
            Examples
            --------

            >>> y_true = [3, -0.5, 2, 7]
            >>> y_pred = [2.5, 0.0, 2, 8]
            >>> explained_variance_score(y_true, y_pred)
          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)  
          score = 1-(np.var(np.array(true)-np.array(pred))/np.var(np.array(true)))
          return score

      def hamming_distance(self,true,pred):
          """
            Returns with Hamming Distance.

            Compute the Hamming distance between two 1-D arrays.
            The Hamming distance between 1-D arrays `u` and `v`, is simply the
            proportion of disagreeing components in `u` and `v`. If `u` and `v` are
            boolean vectors.

            Parameters
            ------------
            u : (N,) array_like
                Input array.
            v : (N,) array_like
                Input array.

            Returns
            -------
            hamming : double. The Hamming distance between vectors `u` and `v`.

          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)  
          hd = sum(np.abs(t1 - t2) for t1, t2 in zip(true, pred)) / len(true)
          return hd

      def euclidean_distance(self,true,pred):
          """
            Return with Euclidean Distance.

            Considering the rows of X (and Y=X) as vectors, compute the
            distance matrix between each pair of vectors.

            For efficiency reasons, the euclidean distance between a pair of row
            vector x and y is computed as::

            dist(x, y) = sqrt(dot(x, x) - 2 * dot(x, y) + dot(y, y))

            Parameters
            ----------
                X : {array-like, sparse matrix}, shape (n_samples_1, n_features)

                Y : {array-like, sparse matrix}, shape (n_samples_2, n_features)

            Returns
            ----------
                distances : array, shape (n_samples_1, n_samples_2)
          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)  
          return np.sqrt(sum((t1-t2)**2 for t1, t2 in zip(true,pred)))

      def manhattan_distance(self,true,pred):
          """
            Returns with Manhattan Distance.
            
            Manhattan distance is calculated as the sum of the absolute differences between the two vectors.
            The Manhattan distance is related to the L1 vector norm and the sum absolute error and mean absolute error metric.
            Compute the City Block (Manhattan) distance. Computes the Manhattan distance between two 1-D arrays `u` and `v`.

            Parameters
            ----------
                u : (N,) array_like
                    Input array.
                v : (N,) array_like
                    Input array.

            Returns
            ----------
                Manhattan distance : double. The Manhattan distance between vectors `u` and `v`.
          """
          import numpy as np          
          true = np.array(true).reshape(-1)
          pred = np.array(pred).reshape(-1)
          return sum(abs(t1-t2) for t1, t2 in zip(true,pred))

      def minkowski_distance(self,true,pred, p):
            """
                Return with Minkowski Distance.

                Minkowski distance calculates the distance between two real-valued vectors.
                It is a generalization of the Euclidean and Manhattan distance measures and
                adds a parameter, called the “order” or “p“, that allows different distance 
                measures to be calculated.
                
                The Minkowski distance measure is calculated as follows:

                EuclideanDistance = (sum for i to N (abs(v1[i] – v2[i]))^p)^(1/p)
                Where “p” is the order parameter.

                When p is set to 1, the calculation is the same as the Manhattan distance.
                When p is set to 2, it is the same as the Euclidean distance.

                p=1: Manhattan distance.
                p=2: Euclidean distance.

                Parameters
                ----------
                x : (M, K) array_like
                    Input array.
                y : (N, K) array_like

                Returns
                --------
                When p is set to 1, the calculation is the same as the Manhattan distance.
                When p is set to 2, it is the same as the Euclidean distance.

                p=1: Manhattan distance.
                p=2: Euclidean distance.
            """
            import numpy as np          
            true = np.array(true).reshape(-1)
            pred = np.array(pred).reshape(-1)
            return sum(np.abs(t1-t2)**p for t1, t2 in zip(true,pred))**(1/p)

      def performance_evaluation(self,true,pred):
                """
                Return with Performance Evaluation parameters with following parameters:
                        1.  mean_absolute_error
                        2.  mean_square_error
                        3.  root_mean_square_error
                        4.  mean_absolute_error
                        5.  R^2 score

                Parameters
                ----------
                y_true      : array-like of shape (n_samples,) or (n_samples, n_outputs)
                              Ground truth (correct) target values.

                y_pred      : array-like of shape (n_samples,) or (n_samples, n_outputs)
                              Estimated target values.

                Returns
                -------
                loss        : float or ndarray of floats
                              A non-negative floating point value (the best value is 0.0), or an
                              array of floating point values, one for each individual target.    
                            
                """
                import numpy as np 
                import pandas as pd

                true = np.array(true).reshape(-1)
                pred = np.array(pred).reshape(-1)

                mae  = np.mean(np.abs(true-pred))
                mse  = np.mean(np.square(true-pred))
                mape = np.mean(np.abs(true-pred)/true)*100
                rmse = np.sqrt(mse)
                r2   = 1-np.mean(np.square(true-pred))/np.mean(np.square(true-np.mean(true)))
                result = pd.DataFrame([[mae,mse,rmse,mape,r2]],columns=['mae','mse','rmse','mape','r2'])

                print("MAE: {}\nMSE: {}\nRMSE: {}\nMAPE: {}\nR^2 score: {}".format(mae,mse,rmse,mape,r2))
                return result   
Evaluate.__doc__

