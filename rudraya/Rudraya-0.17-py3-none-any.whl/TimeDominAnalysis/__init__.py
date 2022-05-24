class time_features:
      
       def __init__(self,sig):
           
            """
            Summary:
            ---------- 
            A time-domain graph shows how a signal changes with time, whereas a frequency-domain graph shows how much of the signal lies
            within each given frequency band over a range of frequencies.

            It consists of statistical dimensional and non-dimensional time-domain features such as Peak Amplitude, Mean Amplitude, 
            root mean square (RMS), Skewness, Kurtosis, Peak-to-Peak,Crest Factor, Variance, Standard Deviation, Impulse Factor,
            Margin factor, shape factor,Clearance Factor of the raw or pre-processed signals.

            References: 
            1.	Hosameldin and N. Asoke, Condition Monitoring with Vibration Signals. Wiley-IEEE Press, 2020.
            2.	L. Wang and R. Gao, Condition Monitoring and Control for Intelligent Manufacturing. Springer, 2006.

            Parameters:
            ------------
                         sig         : pandas.core.frame.DataFrame
                         Description : sig is an pandas dataframe which carry group of predictor feature either sound,vibration,current,
                                       temp signal which used here to perform time domain analysis.
            Return:
            ------------
                         output      : int/float
                         Description : It returns time-domain features such as Peak Amplitude, Mean Amplitude, 
                                       root mean square (RMS), Skewness, Kurtosis, Peak-to-Peak,Crest Factor, Variance,
                                       Standard Deviation, Impulse Factor,Margin factor, shape factor,Clearance Factor,etc.
            """
            import numpy as np            
            self.signal = sig
            self.signal = np.array(self.signal).reshape(-1)
            
       def peak_amplitude(self):
           """
           Peak Amplitude:
           -----------------

           The peak amplitude, xp, is the maximum positive amplitude of the signal; it
           can also be defined as half the difference between the maximum and minimum
           amplitude, i.e. the maximum positive peak amplitude and the maximum negative peak
           amplitude.

           Example:
           -------------
           >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
           >>> tx = time_features(array1)
           >>> xp = tx.peak_amplitude()                 
           >>> print(xp)
 
           """
           import numpy as np
           xp = 0.5*(np.max(self.signal)-np.min(self.signal))
           return xp
        
       def mean_amplitude(self):
            """
            Mean_Amplitude:
            -----------------

            The mean amplitude (x), is the average of the signal over a sampled interval.

            Example:
            -----------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)
            >>> xm = tx.mean_amplitude()                  
            >>> print(xm)

            """
            import numpy as np
            xm = np.mean(self.signal)
            return xm
        
       def rms(self):
            """
            Root Mean Square:
            -----------------------

            The root mean square (RMS) amplitude, xRMS, is the variance of the signal
            magnitude.

            Example:
            -----------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)      
            >>> xrms = tx.rms()      
            >>> print(xrms)

            """
            import numpy as np
            rmse = np.sqrt(np.mean(np.square(np.abs(self.signal))))
            return rmse
        
       def p2p_amplitude(self):
            """
            Peak-to-Peak Amplitude:
            -----------------------

            The peak-to-peak amplitude, also called the range, xp−p, is the range of the
            signal, xmax(t)-xmin(t), which denotes the difference between the maximum positive
            peak amplitude and the maximum negative peak amplitude.
                                  
            Example:
            -------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)        
            >>> xp2p = tx.p2p_amplitude()      
            >>> print(xp2p)

            """
            import numpy as np
            p2p = np.max(self.signal)-np.min(self.signal)
            return p2p
        
       def crest_factor(self):
            """
            Crest_Factor:
            -------------

            The crest factor (CF), xCF , is defined as the ratio of the peak amplitude value, xp, and the
            RMS amplitude, xRMS, of the signal.
                                    
            Example:
            -------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)                   
            >>> xCF = tx.crest_factor()        
            >>> print(xCF)

            """
            import numpy as np
            xCF = self.peak_amplitude() / self.rms()
            return xCF
       
       def variance(self):
            """
            Variance:
            -----------

            The variance (σ2), defines deviations of the signal energy from the mean value.
            
            Example:
            ------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)                    
            >>> var = tx.variance()                  
            >>> print(var)
  
            """
            import numpy as np
            variance =  np.sum(np.square(self.signal-self.mean_amplitude()))/(len(self.signal)-1)
            return variance

       def standard_deviation(self):
            """
            Standard_Deviation:
            -------------------

            The square root of the variance, i.e. σx, is called the standard deviation of the signal x.

            Example:
            ------------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)       
            >>> std = tx.standard_deviation()     
            >>> print(std)
     
            """
            import numpy as np
            std = np.sqrt(self.variance())
            return std
         
       def impulse_factor(self):
            """
            Impulse Factor:
            ---------------

            The impulse factor, xIF , is defined as the ratio of the peak value to the average of the
            the absolute value of the signal.
            
            Example:
            --------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)                  
            >>> xIF = tx.impulse_factor()        
            >>> print(xIF)
     
            """
            import numpy as np
            xIF = self.peak_amplitude() / np.mean(np.abs(self.signal))
            return xIF
         
       def margin_factor(self):
            """
            Margin Factor:
            ---------------
            
            The margin factor value changes significantly with changes in the peak value, which
            makes it very sensitive to impulse faults in particular.
            
            Example:
            ----------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)        
            >>> xMF = tx.margin_factor()    
            >>> print(xMF)
    
            """
            import numpy as np
            xMF = self.peak_amplitude() / np.square(np.mean(np.sqrt(np.abs(self.signal))))
            return xMF
         
       def shape_factor(self):
            """
            Shape Factor:
            -------------
            The shape factor, xSF , is defined as the ratio of the RMS value to the average of the absolute
            value of the signal.
            
            Example:
            -------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)       
            >>> xSF = tx.shape_factor()       
            >>> print(xSF)
           
            """
            import numpy as np
            xSF  = self.rms() / np.mean(np.abs(self.signal))
            return xSF
         
       def clearance_factor(self):
            """
            Clearance Factor:
            -----------------
            The clearance factor, xCLF , is defined as the ratio of the maximum value of the input signal
            to the mean square root of the absolute value of the input signal.
                                    
            Example:
            -----------------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)       
            >>> xCF = tx.clearance_factor()      
            >>> print(xCF)

            """
            import numpy as np
            xCF  = np.max(self.signal) / np.square(np.mean(np.sqrt(np.abs(self.signal))))
            return xCF
        
       def skewness(self):
            """
            Skewness:
            ---------
            The skewness, also called the third normalised central statistical moment, xSK ,
            is a measure of the asymmetrical behaviour of the signal through its probability density
            function (PDF): i.e. it measures whether the signal is skewed to the left or right
            side of the distribution of the normal state of the signal. 

            Example:
            --------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)       
            >>> xsk = tx.skewness()
            >>> print(xsk)

            """
            import numpy as np
            xskew  =  np.mean((self.signal - self.mean_amplitude())**3) / (self.standard_deviation()**3)
            return xskew
        
       def kurtosis(self):
            """
            Kurtosis:
            ----------

            The kurtosis, also called the fourth normalised central statistical moment,  is a
            the measure of the peak value of the input signal through its PDF: i.e. it measures
            whether the peak is higher or lower than the peak of the distribution corresponding to
            a normal condition of the signal.

            Example:
            --------
            >>> array1 =np.array([0.078125, 0.08544922, 0.078125, 0.07324219, 0.08300781, 0.083007])
            >>> tx = time_features(array1)       
            >>> xkur = tx.kurtosis()     
            >>> print(xkur)
                 
            """
            import numpy as np
            xkurt = np.mean((self.signal - self.mean_amplitude())**4) / (self.standard_deviation()**4)
            return xkurt
        
time_features.__doc__