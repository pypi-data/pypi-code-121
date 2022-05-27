# -*- coding: utf-8 -*-
"""
The module provides a class for finite discrete distributions which are utilized for discrete-time analysis.
For example, discrete-time GI/GI/1 systems can be analyzed with functions of the module.

(c) Tobias Hossfeld  (Aug 2021)

This module is part of the following book. The book is to be cited whenever the script is used (copyright CC BY-SA 4.0):

>Tran-Gia, P. & Hossfeld, T. (2021). 
>Performance Modeling and Analysis of Communication Networks - A Lecture Note.
>Würzburg University Press. <br>
>https://doi.org/10.25972/WUP-978-3-95826-153-2


Example
-------
We can easily define some discrete distribution and do computations with the corresponding random variables.
In the example, we consider the sum of two random variables, which requires the convolution of the corresponding probability mass functions.
The r.v. A follows a discrete uniform distribution in the range [0;10], while the r.v. B follows a negative binomial distribution,
which is defined through the mean and the coefficient of variation.

>>> import discreteTimeAnalysis as dt
>>> A = dt.DU(a=0, b=10) % A ~ DU(0,10)
>>> EX, cX = 2.0, 1.5   % mean EX and coefficient of variation cX
>>> B = dt.NEGBIN(EX, cX) % negative binomial distribution
>>> C = A + B % sum of random variables requires convolution of PMFs
>>> C.plotCDF(label='A+B') % plot the CDF of the sum of A+B


Operators
---------
The module overloads the following operators, which make it convenient to implement comprehensive and well understandable code.

`+` operator: The sum of two random variables means the convolution of their probability mass functions. 
`A+B` calls the method `DiscreteDistribution.conv` and is identical to `A.conv(B)`, see the example above.
It is also possible to add an integer value (i.e. convolution with a deterministic distribution).

`-` operator: The difference of two random variables means the convolution of their probability mass functions. 
`A-B` calls the method `DiscreteDistribution.convNeg` and is identical to `A.convNeg(B)`.
It is also possible to subtract an integer value (i.e. negative convolution with a deterministic distribution).

`-` operator: The unary minus operator is overloaded. `B=-A` returns a `DiscreteDistribution` with `B.pk = - A.pk`. 
The two statements are identical: `-A+B` and `B-A`, if both are discrete distributions.

`<` operator: The comparison is done based on means. Returns true if `A.mean() < B.mean()`

`<=` operator: The comparison is done based on means. Returns true if `A.mean() <= B.mean()`

`>` operator: The comparison is done based on means. Returns true if `A.mean() > B.mean()`

`>=` operator: The comparison is done based on means. Returns true if `A.mean() >= B.mean()`

`==` operator: The comparison is done based on means. For the equality comparison, the
threshold value `discreteTimeAnalysis.comparisonEQ_eps` is used for numerical reasons. 
Returns true if `abs( A.mean() - B.mean() ) <= comparisonEQ_eps`. This allows a compact
implementation of the power method.

`!=` operator: The comparison is done based on means. For the equality comparison, the
threshold value `discreteTimeAnalysis.comparisonEQ_eps` is used for numerical reasons. 
Returns true if `abs( A.mean() - B.mean() ) > comparisonEQ_eps`. This allows a compact
implementation of the power method.

`|` operator: This operator is used as a shortcut for `DiscreteDistribution.conditionalRV` which returns a conditional random variable.

`[]` operator: This provides the pmf on the passed argument. `A[x]` is a shortcut for `A.pmf(x)`. 

Overloaded functions
--------------------
`len(A)`: returns the length of the support of this distribution, i.e. the number of positive probabilities.

`abs(A)`: returns a discrete distribution considering the absolute value of the distribution and summing up the probabilities (for negative and positive values).

`max(**args)`: returns the maximum of random variables for variable number of input distributions, e.g. max(A1,A2,A3). See `max()`.

`min(**args)`: returns the minimum of random variables for variable number of input distributions, e.g. min(A1,A2,A3). See `min()`.

Distance metrics
----------------
The distance between two discrete distributions is available: Jensen-Shannon distance `DiscreteDistribution.jsd`;
total variation distance `DiscreteDistribution.tvd`; earth mover's distance `DiscreteDistribution.emd`.
 
Notes
-----
The theory behind the module is described in the book in Chapter 6. 
The text book is published as open access book and can be downloaded at
<https://modeling.systems>


"""

import numpy as np
import matplotlib.pyplot as plt
import math
import time
import numbers

comparisonEQ_eps = 1e-6
"""The variable is used for the numerical comparison of two random variables `A`and `B`. 
The comparison `A==B` returns true if `abs( A.mean() - B.mean() ) <= comparisonEQ_eps`. Default value is 1e-6.

"""

#%%    
class DiscreteDistribution:
    r"""The class implements finite discrete distributions representing discrete random variables.

    A discrete distribution reflects a random variable \( X \) and is defined 
    by its probability mass function (PMF). The random variable can take discrete values
    which are defined by the numpy array `xk` (sample space). The probability that the random variable
    takes a certain value is \( P(X=k)=p_k \). The probabilities are stored in the
    numpy array `pk`.
    

    Attributes
    ----------
    xk : numpy array
        Values of the distribution (sample space).
    pk : numpy array
        Probabilities corresponding to the sample space.
    name : string
        Arbitrary name of that distribution. 

    """    
    
    def __init__(self, xk, pk, name='discrete distr.'):         
        r"""A discrete distribution is initialized with value range `xk`and probabilities `pk`.
        
        For the initialization of a discrete random variable, the sample space `xk` and the corresponding
        probabilities `pk` are required. Both parameters are then stored as class attributes in form
        of numpy array (one-dimensional). In addition, an arbitrary `name` can be passed to the
        distribution which is used when printing an instance of the class, see e.g. 
        `DiscreteDistribution.describe`.

        Parameters
        ----------
        xk : numpy array or list
            Values of the distribution.
        pk : numpy array or list
            Probabilities corresponding to the values: \( P(X=xk)=pk \).
        name : string, optional (default 'discrete distr.')
            Name of the distribution for string representation.

        """        
        assert len(xk)==len(pk) # same length        
        
        self.xmin = np.min(xk)
        self.xmax = np.max(xk)
        
        # adjust to vector xk without gaps
        self.xk = np.arange(self.xmin, self.xmax+1, dtype='int')
        self.pk = np.zeros( len(self.xk) )
        self.pk[xk-self.xmin] = pk
        self.name = name
        
    def mean(self):
        r"""Returns the mean value of the distribution \( E[X] \).
    
    
        Returns
        -------
        float
            Mean value.
            
        """        
        return np.sum(self.xk*self.pk)
    
    def var(self):
        r"""Returns the variance of the distribution \( VAR[X] \).
    
    
        Returns
        -------
        float
            Variance of the distribution.
            
        """                
        return np.sum(self.xk**2*self.pk)-self.mean()**2
    
    def std(self):
        r"""Returns the standard deviation of the distribution \( {STD}[X]=\sqrt{VAR[X]} \).
    
    
        Returns
        -------
        float
            Standard deviation of the distribution.
            
        """                
        return math.sqrt(self.var())
    
    def cx(self):
        r"""Returns the coefficient of the variation of the distribution \( c_X = STD[X]/E[X] \).
    
    
        Returns
        -------
        float
            Coefficient of variation of the distribution.
            
        """               
        return self.std()/self.mean()
    
    def skewness(self):
        r"""Returns the skewness of the distribution.
    
    
        Returns
        -------
        float
            Skewness of the distribution.
            
        """               
        EX3 = (self.xk**3)@self.pk
        mu = self.mean()
        sigma = self.std()
        return (EX3-3*mu*sigma**2-mu**3)/(sigma**3)

    def entropy(self, base=2):
        r"""Returns the entropy of the distribution.
    
        Parameters
        ----------
        base : float (default 2)
            Base of the logartihm. 
            Base 2 gives the unit of bits (Shannon entropy).
            
        Returns
        -------
        float
            Entropy of the distribution.
            
        """               
        i = self.pk>0        
        return -(self.pk[i] @ np.log2(self.pk[i])) / np.log2(base)

    def mode(self):
        r"""Returns the mode of the distribution.
    
    
        Returns
        -------
        float
            Mode of the distribution.
            
        """                
        return self.xk[np.argmax(self.pk)]
    
    def quantile(self, q=0.95):
        r"""Returns the q-quantile of the distribution.
    
        Parameters
        ----------
        q : float, optional (default 0.95)
            The parameter indicates that the q-quantile is derived. The default value is `q=0.95`
            for the 95%-quantile. It must be ensured that \( 0< q < 1\).
    
        Returns
        -------
        float
            q-Quantile (default 95%) of the distribution.
            
        """                
        return self.xk[np.argmax(self.pk.cumsum()>q)]
    
    def describe(self):
        r"""Prints basic characteristics of the distribution.        
        
        This method prints basic characteristics of the distribution.
        
        Example
        -------
        >>> A.describe()
            interarrival_time: EX=5.5000, cX=0.5222, mode=1 
                        
        """               
        print(f'{self.name}: EX={self.mean():.4f}, cX={self.cx():.4f}, mode={self.mode()}, support={self.xmin},...,{self.xmax} ')

    def checkDistribution(self):
        r"""Returns if the distribution is valid.         
    
        Returns
        -------
        bool
            Return true if the distribution is valid. 
            Returns false if e.g. the values of `xk` are not increasing or the sum of probabilities `pk` is less than 1.
            
        """                
        increasing = np.all(np.diff(self.xk) > 0) # xk: strictly monotonic increasing
        sumOne = abs(np.sum(self.pk)-1)<1e-8 # xk: error
        return increasing and sumOne
            
    def conv(self, other,name=None):
        r"""Returns the sum of this distributions and another distribution.
        
        Returns the sum of this distribution and the other distribution. Note that \( A+B=B+A \).
        The operator `+` is overloaded for that class, such that `A+B` is an abbreviation for `A.conv(B)`.
        
        
        Parameters
        ----------
        other : DiscreteDistribution
            The other distribution of the sum.
        name : string, optional (default 'self.name+other.name')
            Name of the distribution for string representation.
            
        Example
        -------
        >>> A = DU()
        >>> A.conv(A) # returns A+A
        >>> DiscreteDistribution.conv(A,A) # returns A+A
        >>> A+A # returns A+A
    
        Returns
        -------
        DiscreteDistribution
            Sum of the distributions: `self+other`.
                    
        """                
        s = f'{self.name}+{other.name}' if name is None else name     
        pk = np.convolve(self.pk, other.pk)
        xk = np.arange(self.xmin+other.xmin, self.xmax+other.xmax+1)
        return DiscreteDistribution(xk,pk,name=s)    
    
    def convNeg(self, other, name=None):
        r"""Returns the difference of two distributions.
        
        Returns the difference of this distribution and the other distribution. 
        The operator `-` is overloaded for that class, such that `A-B` is an abbreviation for `A.convNeg(B)`.
        
        
        Parameters
        ----------
        B : DiscreteDistribution
            The other distribution to be substracted from this distribution.
        name : string, optional (default 'A.name-B.name')
            Name of the distribution for string representation.
            
        Example
        -------
        >>> A = DU()
        >>> A.convNeg(A) # returns A-A
        >>> DiscreteDistribution.convNeg(A,A) # returns A-A
        >>> A-A # returns A-A
    
        Returns
        -------
        DiscreteDistribution
            Difference of the distributions: `self-other`.
                    
        """
        s = f'{self.name}-{other.name}' if name is None else name     
        pk = np.convolve(self.pk, other.pk[::-1])
        xk = np.arange(self.xmin-other.xmax, self.xmax-other.xmin+1)
        return DiscreteDistribution(xk,pk,name=s)
        
    def pi_op(self, m=0, name=None):        
        r"""Applies the pi-operator (summing up probabilities to m) and returns the resulting distribution.
        
        The pi-operator truncates a distribution at the point \(X=m\) and sums up the probabilities. 
        The probability mass \( P(X\leq m) \) is assigned
        to the point \(X=m\), while all other probabilities are set to zero for \(X<m\). The default operation is 
        to delete all negative values and assigning the probability mass of negative values to \(X=0\). 
        Hence, the default value is \(m=0\) and in this case \(P(X'=0 ) = \sum_{i=-\infty}^0 P(X=i)\), while the probabilites for all negative values 
        are set to zero \(P(X'= i ) = 0, \forall i<0\) for the resulting distribution \(X'\). The rest of the distribution \(i>0 \) is not changed.
                                              
        In general: \(P(X'=0 ) = \sum_{i=-\infty}^m P(X=i)\). Hence, for a distribution \(x(k)=P(X=k) \), 
        the pi-operator works as follows:

        $$
        \pi_m \Big(x(k)\Big)  =  \begin{cases}
                0 & k < m \\
                \sum\limits_{i = - \infty}^m
                   x(i) & k= m \\
                x(k) & k > m \\
        \end{cases} 
        $$                              
        
        Parameters
        ----------
        m : integer
            The truncation point at which probabilities are summed up.
        name : string, optional (default 'pi_m(self.name)')
            Name of the distribution for string representation.
            
        Returns
        -------
        DiscreteDistribution
            Truncated distribution.
                    
        """
        s = f'pi_{m}({self.name})' if name is None else name     
        if m <= self.xmin:
            self.name = s
            return self
        elif m >= self.xmax:
            return  DiscreteDistribution([m],[1],name=s)
        else:
            #s = f'pi_{m}({A.name})' if name is None else name        
            k = np.searchsorted(self.xk,m)
            xk = np.arange(m, self.xmax+1)
            pk = np.zeros(len(xk))
            pk[0] = np.sum(self.pk[0:k+1])
            pk[1:] = self.pk[k+1:]
            return DiscreteDistribution(xk,pk,name=s)
            
    def pi0(self, name=None):
        r"""Applies the pi-operator (truncation of negative values, summing up probabilities ) and returns the resulting distribution.
        
        The pi0-operator truncates the distribution at 0 and sums up the probabilities.  The probability mass of negative values is assigned to 0. 
        For the resulting distribution \(X'\), it is \(P(X'=0 ) = \sum_{i=-\infty}^0 P(X=i)\), while the probabilites for all negative values 
        are set to zero \(P(X'= i ) = 0, \forall i<0\). The rest of the distribution \(i>0 \) is not changed.
                            
        $$
        \pi_0 \Big(x(k)\Big)  =  \begin{cases}
                0 & k < 0 \\
                \sum\limits_{i = - \infty}^0
                   x(i) & k= 0 \\
                x(k) & k > 0 \\
        \end{cases} 
        $$
                                              
        Parameters
        ----------
        name : string, optional (default 'pi0(self.name)')
            Name of the distribution for string representation.
            
        Returns
        -------
        DiscreteDistribution
            Truncated distribution.

        See also
        -------
        Generalized truncation `DiscreteDistribution.pi_op`
        """

        s = f'pi0({self.name})' if name is None else name
        return self.pi_op(m=0, name=s)
    
    def jsd(self, other ):
        r"""Returns the  Jensen-Shannon distance of the two distributions.
        
        Returns the Jensen-Shannon distance which is the square root of the Jensen-Shannon divergence:
        [Wikipedia: Jensen-Shannon distance](https://en.wikipedia.org/wiki/Jensen%E2%80%93Shannon_divergence)
                
        Parameters
        ----------
        other : DiscreteDistribution
            The other distribution.
    
        Returns
        -------
        float
            Jensen-Shannon distance.
        
                    
        """                
        xmin = min(self.xmin, other.xmin)
        xmax = max(self.xmax, other.xmax)
        x = np.arange(xmin, xmax+1, dtype=int)
        M = (self.pmf(x)+other.pmf(x))/2
        # Kullback-Leibler divergence D(P||M)        
        Px = self.pmf(x)
        i = (M>0) & (Px>0)
        DPM = np.sum(Px[i]*np.log2(Px[i]/M[i]))
        
        Qx = other.pmf(x)
        i = (M>0) & (Qx>0)
        DQM = np.sum(Qx[i]*np.log2(Qx[i]/M[i]))
        
        return np.sqrt(DPM/2+DQM/2)
    
    # total variation distance
    def tvd(self, other ):
        r"""Returns the total variation distance of the two distributions.
        
        Computes the total variation distance: [Wikipedia: Total variation distance](https://en.wikipedia.org/wiki/Total_variation_distance_of_probability_measures)
                
        Parameters
        ----------
        other : DiscreteDistribution
            The other distribution.
    
        Returns
        -------
        float
            Total variation distance.
                    
        """                
        xmin = min(self.xmin, other.xmin)
        xmax = max(self.xmax, other.xmax)
        x = np.arange(xmin, xmax+1, dtype=int)
                        
        return np.sum(np.abs(self.pmf(x)-other.pmf(x)))/2
        
    # EMD
    def emd(self, other ):
        r"""Returns the earth mover's distance of the two distributions.
        
        Implements the earth mover's distance: [Wikipedia: Total variation distance](https://en.wikipedia.org/wiki/Total_variation_distance_of_probability_measures)
                
        Parameters
        ----------
        other : DiscreteDistribution
            The other distribution.
    
        Returns
        -------
        float
            Earth mover's distance.
              
                    
        """                
        xmin = min(self.xmin, other.xmin)
        xmax = max(self.xmax, other.xmax)
        x = np.arange(xmin, xmax+1, dtype=int)
                        
        return np.sum(np.abs(self.cdf(x)-other.cdf(x)))    
    
    def _trim(self, m, normalize=True):
        r"""Truncates the distribution from left and right side. 
        
        The operation uses the minimum and maximum of the values m and truncates the distribution to 
        this range. It changes the value range `xk` and the corresponding probabilities `pk`.

        Parameters
        ----------
        m : numpy array of boolean values
            The first and the last True value in the array are used to truncate the distribution.
        normalize : bool
            If True, the distribution is renormalized. If False, the distribution is truncated.
            
        Returns
        -------
        None
        """                      
        kmin = m.argmax()
        kmax = m.size - m[::-1].argmax()-1
        
        #A.xmin = np.min(xk)
        #A.xmax = np.max(xk)        
        
        self.xk = self.xk[kmin:kmax+1]
        self.pk = self.pk[kmin:kmax+1]
        
        self.xmin = self.xk[0]
        self.xmax = self.xk[-1]
        
        if normalize:
            self.pk /= self.pk.sum()
        return
    
    def trim(self, normalize=True):
        r"""Remove trailing and leading diminishing probabilities. 
        
        The trim-operation changes the value range `xk` and the corresponding probabilities `pk` by removing
        any leading and any trailing diminishing probabilities. This distribution object is therefore changed.
        
        Parameters
        ----------        
        normalize : bool
            If True, the distribution is renormalized. If False, the distribution is truncated.

        Returns
        -------
        None
        """                
        m = self.pk!=0        
        self._trim(m, normalize)
        return 
    
    def trimPMF(self, eps=1e-8, normalize=True):
        r"""Remove trailing and leading diminishing probabilities below a certain threshold. 
        
        The trimPMF-operation changes the value range `xk` and the corresponding probabilities `pk` by removing
        any leading and any trailing diminishing probabilities which are less than `eps`. 
        This distribution object is therefore changed.

        Parameters
        ----------
        eps : float
            Threshold which leading or trailing probabilities are to be removed.
        normalize : bool
            If True, the distribution is renormalized. If False, the distribution is truncated.
            
        Returns
        -------
        None        

        """                
        m = self.pk>eps #!=0        
        self._trim(m, normalize)
        return
    
    def trimCDF(self, eps=1e-8, normalize=True):
        r"""Remove trailing and leading diminishing cumulative probabilities below a certain threshold. 
        
        The trimCDF-operation changes the value range `xk` and the corresponding probabilities `pk` 
        by removing any leading and any trailing diminishing cumulative probabilities which are less than `eps`. 
        This distribution object is therefore changed.

        Parameters
        ----------
        eps : float
            Threshold which leading or trailing cumulative probabilities are to be removed.
        normalize : bool
            If True, the distribution is renormalized. If False, the distribution is truncated.
            
        Returns
        -------
        None        
        """                
        m = self.pk.cumsum()>eps #!=0        
        self._trim(m, normalize)
        return    
    
    
    # this is an unnormalized distribution: 
    # conditional distribution if normalized
    # sigmaLT = sigma^m: takes the lower part ( k < m ) of a distribution
    def sigmaTakeLT(self, m=0, name=None, normalized=True):        
        r"""Applies the sigma-operator and returns the result.
        
        The sigma-operator returns the lower or the upper part of the distribution. 
        `sigmaTakeLT` implements the \(\sigma^m\)-operator which sweeps away the upper part \(k\geq m\) 
        and takes the lower part \(k < m \). The distribution is therefore truncated. 
        The results of these operations are unnormalized distributions where the sum of the probabilities
        is less than one:
        $$\sigma^m[x(k)] = 
		\begin{cases}
		x(k) & k<m \\
		0 & k \geq m 
        \end{cases}
        $$

        The parameter `normalized` (default True) indicates that a normalized distribution
        (conditional random variable) is returned, such that the sum of probabilities is one.
        The parameter `m` indicates at which point the distribution is truncated.
        
        Parameters
        ----------
        m : integer
            Truncation point. The lower part \(k < m \) of the distribution is taken.        
        name : string, optional (default 'sigma^{m}({self.name})')
            Name of the distribution for string representation.
        normalized : bool
            If true returns a normalized distribution. If false the original probabilities for the 
            truncated range are returned. 
            
        Returns
        -------
        DiscreteDistribution
            Returns normalized or unnormalized truncated distribution taking probabilities for \(k < m \).            

        Raises
        ------
        ValueError
            If m is less than the smallest value xmin of this distribution. 
            
        """                
        #assert m<xk[-1]
        s = f'sigma^{m}({self.name})' if name is None else name     
                
        if m<=self.xk[0]:
            if normalized: 
                raise ValueError('sigmaLT: m < min(xk)')
            else:
                return DiscreteDistribution([m], [0], name=s)
        if m>self.xk[-1]:
            return DiscreteDistribution(self.xk, self.pk, name=s)
            
        last = np.searchsorted(self.xk, m, side='right')-1        
        
        xk=self.xk[:last]
        if normalized:
            prob_Dist_U_lt_m = self.pk[:last].sum() 
            pk=self.pk[:last] / prob_Dist_U_lt_m
        else:
            pk=self.pk[:last]                
        return DiscreteDistribution(xk, pk, name=s)
    
    # this is an unnormalized distribution: 
    # conditional distribution if normalized
    def sigmaTakeGEQ(self, m=0, name=None, normalized=True):
        r"""Applies the sigma-operator and returns the result.
        
        The sigma-operator returns the lower or the upper part of the distribution. 
        `sigmaTakeGEQ` implements the \(\sigma_m\)-operator which sweeps away the lower part \(k < m \) 
        and takes the upper part \( k \geq m \). The distribution is therefore truncated. 
        The results of these operations are unnormalized distributions where the sum of the probabilities
        is less than one:
        $$    
        \sigma_m[x(k)] = 
		\begin{cases}
		0 & k<m \\
		x(k) & k \geq m
		\end{cases} 
        $$

        The parameter `normalized` (default True) indicates that a normalized distribution
        (conditional random variable) is returned, such that the sum of probabilities is one.
        The parameter `m` indicates at which point the distribution is truncated.
        
        Parameters
        ----------
        m : integer
            Truncation point. The upper part \(k\geq m\) of the distribution is taken.        
        name : string, optional (default 'sigma_{m}({self.name})')
            Name of the distribution for string representation.
        normalized : bool
            If true returns a normalized distribution. If false the original probabilities for the 
            truncated range are returned. 
            
        Returns
        -------
        DiscreteDistribution
            Returns normalized or unnormalized truncated distribution taking probabilities for \(k \geq m \).

        """
        s = f'sigma_{m}({self.name})' if name is None else name     
        #assert m>=self.xk[0]
        if m>self.xk[-1]:
            if normalized: 
                raise ValueError('sigmaGEQ: m > max(xk)')
            else:
                return DiscreteDistribution([m], [0], name=s)                    
        
        first = np.searchsorted(self.xk, m, side='left')
        
        xk=self.xk[first:]
        if normalized:
            prob_Dist_U_geq_m = self.pk[first:].sum() 
            pk=self.pk[first:] / prob_Dist_U_geq_m
        else:
            pk=self.pk[first:]                
        return DiscreteDistribution(xk, pk, name=s)
    
    def pmf(self, xi):
        r"""Probability mass function at xi of the given distribution.

        Parameters
        ----------
        xi : numpy array or integer
            Quantiles.
            
        Returns
        -------
        numpy array of float
            Probability mass function evaluated at xi.
        """                
        #myxk = np.arange(self.xmin-1, self.xmax+2)
        #mypk = np.hstack((0, self.pk, 0))
        if type(xi) is not np.ndarray:
            if type(xi) is list:
                xi = np.array(xi)
            else:
                xi = np.array([xi])
        
        i = np.where( (xi>=self.xmin) & (xi<=self.xmax) )[0]
        mypk = np.zeros(len(xi))
        
        if len(i)>0:            
            mypk[i] = self.pk[np.searchsorted(self.xk, xi[i], side='left')]
        return mypk
    
    def cdf(self, xi):
        r"""Cumulative distribution function at xi of the given distribution.

        Parameters
        ----------
        xi : numpy array or integer
            Quantiles.
            
        Returns
        -------
        numpy array of float
            Cumulative distribution function evaluated at xi.
        """                
        #myxk = np.arange(self.xmin-1, self.xmax+2)
        #mypk = np.hstack((0, self.pk, 0))
        PK = self.pk.cumsum()
        if type(xi) is not np.ndarray:
            if type(xi) is list:
                xi = np.array(xi)
            else:
                xi = np.array([xi])
        
        i = np.where( (xi>=self.xmin) & (xi<=self.xmax) )[0]
        mypk = np.zeros(len(xi))
        mypk[xi>=self.xmax] = 1
        if len(i)>0:            
            mypk[i] = PK[np.searchsorted(self.xk, xi[i], side='left')]
        return mypk
    
    def plotCDF(self,  addZero=True, **kwargs):
        r"""Plots the cumulative distribution function of this distrribution.

        Parameters
        ----------
        addZero : bool (default True)
            If true the zero point will be explicitly plotted, otherwise not.
        **kwargs: 
            Arbitrary keyword arguments are passed to `Matplotlib.pyplot.step`.
            
        Returns
        -------
        None
        """                
        if addZero and self.xk[0]>=0:
            x = np.insert(self.xk,0,0)
            y = np.insert(self.pk,0,0)
        else:
            x, y = self.xk, self.pk
        
        x = np.append(x, x[-1]+1)
        Y = np.append(y.cumsum(), 1)
        
        plt.step(x, Y, '.-', where='post', **kwargs)
        
    def plotPMF(self,  **kwargs):
        r"""Plots the probability mass function of this distrribution.

        Parameters
        ----------        
        **kwargs: 
            Arbitrary keyword arguments are passed to `Matplotlib.pyplot.plot`.
            
        Returns
        -------
        None
        """                
        plt.plot(self.xk, self.pk, '.-', **kwargs)        
        
    def conditionalRV(self, condition, name=None, normalized=True):
        r"""Returns the normalized or unnormalized conditional random variable.

        Parameters
        ----------
        condition : function
            Applies the function `condition` to match the corresponding values of the distribution.        
        name : string, optional (default '{self.name}')
            Name of the distribution for string representation.
        normalized : bool (default True)
            If true returns a normalized distribution. If false returns the original probabilities for the 
            range where the condition is true. 
            
        Returns
        -------
        DiscreteDistribution
            Returns the conditional distribution for which the condition (applied to `xk`) is true. 
            The resulting distribution is normalized if the paraemter `normalized` is true.
            
            
        Raises
        ------
        ValueError
            If the condition is not fulfilled for any value `xk`
            
        """     
        s = f'{self.name}|condition' if name is None else name     
        which = condition(self.xk)
        
        Apk = self.pk[which] 
        Axk = self.xk[which] 
        if normalized:            
            if Apk.sum()==0:
                raise ValueError('conditionalRV: condition is not possible!')
            return DiscreteDistribution(Axk, Apk/Apk.sum(), name=s)   
        else:
            return DiscreteDistribution(Axk, Apk, name=s)   
        
    def normalize(self):
        r"""Normalizes this random variable.

        This method changes this discrete distribution and ensures that the sum of probabilities equals to one.
            
        Returns
        -------
        None            
        """     
        self.pk = self.pk.clip(0,1,self.pk)
        self.pk = self.pk/self.pk.sum()


    def rvs(self, size=1, seed=None):
        r"""Returns random values of this distribution. 

        Parameters
        ----------
        size : int (default 1)
            Number of random values to generate.        
        seed : int (default None)
            Random number generator seed. The default value is None to generate a random seed.        
            
        Returns
        -------
        Numpy array
            Returns numpy array of random values of this distribution.                         
        """     
        if seed is None: seed = int(time.time())
        np.random.seed(seed)
        return np.random.choice(self.xk, size=size, replace=True, p=self.pk)
        
    # A+B
    def __add__(self, other):       
        if isinstance(other,int):
            return DiscreteDistribution(self.xk+other,self.pk,name=f'{self.name}+{other}')
        elif isinstance(other, DiscreteDistribution):            
            return DiscreteDistribution.conv(self,other,name=f'{self.name}+{other.name}')
        else:
            raise NotImplementedError       
            
        # A+B
    def __radd__(self, other):       
        if isinstance(other,int):
            return DiscreteDistribution(self.xk+other,self.pk,name=f'{other}+{self.name}')
        elif isinstance(other, DiscreteDistribution):            
            return DiscreteDistribution.conv(self,other,name=f'{self.name}+{other.name}')
        else:
            raise NotImplementedError
    
    # A-C
    def __sub__(self, other):   
        if isinstance(other,int):
            return DiscreteDistribution(self.xk-other,self.pk,name=f'{self.name}-{other}')
        elif isinstance(other, DiscreteDistribution):              
            return DiscreteDistribution.convNeg(self,other,name=f'{self.name}-{other.name}')
        else:
            raise NotImplementedError
            
    # A-C
    def __rsub__(self, other):   
        if isinstance(other,int):
            return DiscreteDistribution(self.xk-other,self.pk,name=f'{other}-{self.name}')
        elif isinstance(other, DiscreteDistribution):              
            return DiscreteDistribution.convNeg(self,other,name=f'{self.name}-{other.name}')
        else:
            raise NotImplementedError
    
    # -A: unary minus
    def __neg__(self):
        return DiscreteDistribution(-self.xk,self.pk,name=f'-{self.name}')
    
    # +A: unary plus
    def __pos__(self):
        return DiscreteDistribution(self.xk,self.pk,name=f'+{self.name}')
    
    # A*b
    def __mul__(self, b):                 
        if isinstance(b,int):
            return DiscreteDistribution(self.xk*b,self.pk,name=f'{self.name}*{b}')
        else:
            raise NotImplementedError 
    
    # b*A
    def __rmul__(self, b):                 
        if isinstance(b,int):
            return DiscreteDistribution(self.xk*b,self.pk,name=f'{b}*{self.name}')
        else:
            raise NotImplementedError
            
    # A<B: based on means
    def __lt__(self, other):        
        return self.mean() < other.mean()        
    
    # A<=B: based on means
    def __le__(self, other):                        
        return self.mean() <= other.mean()
    
    # A>B: based on means
    def __gt__(self, other):  
        return self.mean() > other.mean()
                    
    # A>=B: based on means
    def __ge__(self, other):                        
        return self.mean() >= other.mean()
    
    # A==B: based on means and threshold comparisonEQ_eps
    def __eq__(self, other):                        
        #if len(self.xk) != len(other.xk): return False
        #return np.all(self.xk==other.xk) and np.all(self.pk==other.pk)
        return abs(self.mean()-other.mean())<=comparisonEQ_eps
    
    # A!=B: based on means and threshold comparisonEQ_eps
    def __ne__(self, other):                        
        return abs(self.mean()-other.mean())>comparisonEQ_eps
    
    # returns the number of positive numbers
    def __len__(self):
        return len(self.pk>0)
    
    # A**k
    def __pow__(self, other):
        if isinstance(other, numbers.Number):
            return DiscreteDistribution(self.xk**other, self.pk)
        else:
            raise NotImplementedError
    
    # A[x] == A.pmf(x)
    def __getitem__(self, key):
        if isinstance(key, tuple):
            return self.pmf(np.array(key))
        elif isinstance(key, int):
            return self.pmf(key)[0]
        else:
            return self.pmf(key)
        
    # abs(A)
    def __abs__(self):
        pk = np.bincount(abs(self.xk), weights=self.pk)
        return DiscreteDistribution(np.arange(len(pk)),pk)
            
    def __getExtendedRangeDist(self, xmin, xmax):
        end = np.zeros(xmax-self.xmax) if self.xmax < xmax else []
        start = np.zeros(self.xmin-xmin) if self.xmin > xmin else []    
        return np.concatenate((start, self.pk, end))
                    
    # A|condition
    def __or__(self, other):
        if callable(other):  # A|condition
            return self.conditionalRV(other)
    
    def __repr__(self):                
        return self.__str__()

    def __str__(self):
        if len(self.xk)<10:
            return f'{self.name}: xk={np.array2string(self.xk,separator=",")}, pk={np.array2string(self.pk,precision=3, separator=",")}'
        else:
            return f'{self.name}: xk={self.xmin},...,{self.xmax}, pk={self.pk[0]:g},...,{self.pk[-1]:g}'



#%%    
def pi_op(A, m=0, name=None):    
    r"""Returns the pi-operator applied to A.
    
    See also
    ----------
    `DiscreteDistribution.pi_op`
    """ 
    return A.pi_op(m, name)        

def pi0(A, name=None):
    r"""Returns the pi0-operator applied to A.
    
    See also
    ----------
    `DiscreteDistribution.pi0`
    """ 
    return A.pi0(name=name)    

__oldmax = max    
def max(*args):    
    r"""Returns the maximum of the random variables. 
        
    The maximum function is overloaded, such that the maximum of random variables can be directly computed and is returned.
    
    In case, the first argument is a `DiscreteDistribution` and the second argument is an integer, the maximum between the random variable and 
    a deterministic random variable is computed. This corresponds to the application of the pi-operator.
    The pi-operator means the maximum of the random variable and the value m. 
    The random variable A is passed as first parameter `A=args[0]` and m is passed as second parameter `m=args[1]`.
    The following two expressions are identical: `max` and `pi_op`.
    
    Parameters
    ----------
    *args: 
        Variable length argument list. If all variables are `DiscreteDistribution`, then the maximum of the 
        random variables is returned. 
        
        If two arguments are passed (first: DiscreteDistribution; second: int), then the pi-operator is applied.
        The pi-operator means the maximum of the random variable and the value m. 
        The random variable A is passed as first parameter `A=args[0]` and m is passed as second parameter `m=args[1]`.
        The following two expressions are identical: `max` and `pi_op`.
        The random variable is passed as first parameter and m is passed as second parameter.
    
    
    Returns
    -------
    DiscreteDistribution
        Returns the maximum of the random variables. 

    Example
    -------    
    >>> A = DU(0,4)
    >>> max(A, DET(3))
    discrete distr.: xk=[0,1,2,3,4], pk=[0. ,0. ,0. ,0.8,0.2]
        
    
    Example
    -------    
    >>> A = DU(0,4)
    >>> B = max(A,3)
    pi_3(DU(0,4)): xk=[3,4], pk=[0.8,0.2]
    
    See also
    ----------
    `DiscreteDistribution.pi_op`
    """ 
    bools = [isinstance(Ai, DiscreteDistribution) for Ai in args]
    if all(bools):
        xmax = max([Ai.xmax for Ai in args])
        xmin = min([Ai.xmin for Ai in args])
        x = np.arange(xmin, xmax+1, dtype=int)
        cdfs = np.zeros( (len(args),len(x)) )
        for i,Ai in enumerate(args):
            cdfs[i,:] = Ai.cdf(x)
        
        mycdf = np.prod( cdfs, axis=0)
        mypmf = np.diff(np.insert(mycdf,0,0))
        return DiscreteDistribution(x,mypmf.clip(0,1))
    elif len(args) == 2 and isinstance(args[0],DiscreteDistribution) and isinstance(args[1], int):
        return pi_op(args[0], args[1])
    else:
        return __oldmax(*args)
    

__oldmin = min
def min(*args):    
    r"""Returns the minimum of the random variables. 
        
    The minimum function is overloaded, such that the minimum of random variables can be directly computed and a `DiscreteDistribution` is returned.
        
    
    Parameters
    ----------
    *args: 
        Variable length argument list. If all variables are `DiscreteDistribution`, then the minimum of the 
        random variables is returned.                 
    
    Returns
    -------
    DiscreteDistribution
        Returns the minimum of the random variables. 

    Example
    -------    
    >>> A = DU(0,4)
    >>> B = DET(2)
    >>> min(A,B)
    discrete distr.: xk=[0,1,2,3,4], pk=[0.2,0.2,0.6,0. ,0. ]    
    """ 
    bools = [isinstance(Ai, DiscreteDistribution) for Ai in args]
    if all(bools):
        xmax = max([Ai.xmax for Ai in args])
        xmin = min([Ai.xmin for Ai in args])
        x = np.arange(xmin, xmax+1, dtype=int)
        ccdfs = np.zeros( (len(args),len(x)) )
        for i,Ai in enumerate(args):
            ccdfs[i,:] = 1-Ai.cdf(x)
        
        myccdf = np.prod( ccdfs, axis=0)
        mycdf = 1-myccdf
        mypmf = np.diff(np.insert(mycdf,0,0))
        return DiscreteDistribution(x,mypmf.clip(0,1))
    else:
        return __oldmin(*args)


def E(A):
    r"""Returns the expected value of the random variables A.
    
    Example
    -------
    We can compute the variance: \(VAR[A]=E[A^2]-E[A]^2\) with the following syntax:
        
    >>> A = DU(1,5)
    >>> E(A**2)-E(A)**2
    2.0
    >>> A.var()
    2.0
    
    See also
    ----------
    `DiscreteDistribution.mean`
    """        
    return A.mean()

def conv(A,B,name=None):
    r"""Returns the sum of the random variables A+B using convolution operator.
    
    See also
    ----------
    `DiscreteDistribution.conv`
    """        
    return A.conv(B, name=name)


def plotCDF(A, addZero=True, **kwargs):
    r"""Plots the CDF of the distribution `A`. 
    
    See also
    ----------
    `DiscreteDistribution.plotCDF`
    """      
    A.plotCDF(addZero, **kwargs)
    
def plotPMF(A, addZero=True, **kwargs):
    r"""Plots the PMF of the distribution `A`. 
    
    See also
    ----------
    `DiscreteDistribution.plotPMF`
    """      
    A.plotPMF(addZero, **kwargs)    
    

def lindley_equation(W0, C, epsProb=1e-16):
    r"""Implements the Lindley equation.

    Solves the discrete-time Lindley equation which is used for the analysis of the waiting time
    in a GI/GI/1 system. 
    
    $$
    w(k)  =   \pi_0 \Big(w(k) * c(k)\Big) 
    $$
    
    The solution is derived by iteration for a given starting distribution `W0` until the difference \(W_{n+1}-W_{n} \) between
    subsequent distributions is below the treshold `discreteTimeAnalysis.comparisonEQ_eps`.
    
    $$ 
    W_{n+1} = \max(0, W_n+B-A) \\
    w_{n+1} (k)  =  \pi_0  (w_n(k) * c_n(k)) 
    $$

    Parameters
    ----------
    W0 : DiscreteDistribution
        The initial system distribution.
    C : DiscreteDistribution
        The characteristic function of the system.
    eps : float (default 1e-16)
        Threshold which leading or trailing probabilities are to be removed. See `DiscreteDistribution.trimPMF`.  

    Returns
    -------
    DiscreteDistribution
        Steady-state distribution of the stationary discrete-time Lindley equation.
    """         
    Wn = W0
    Wn1 = DiscreteDistribution([-1], [1])
    i = 0
    
    while Wn1 != Wn:
        Wn1 = pi0(Wn+C)
        
        Wn = Wn1
        Wn.name = None
        Wn.trimPMF(eps=epsProb)
        i += 1
    return Wn, i


def GIGI1_waitingTime(A, B, W0=DiscreteDistribution([0],[1]), epsProb=1e-16):  
    r"""Returns the stationary waiting time distribution of the GI/GI/1 queue.

    The stationary waiting time distribution of the GI/GI/1 queue is derived by solving
    the Lindley equation, see `discreteTimeAnalysis.lindley_equation`.

    Parameters
    ----------
    W0 : DiscreteDistribution, optional (default DET(0))
        The initial waiting time distribution. The default value is an empty system, i.e. no waiting time 
        `W0 = DET(0)`.
    A : DiscreteDistribution
        Interarrival time.
    B : DiscreteDistribution
        Service time.
    eps : float (default 1e-16)
        Threshold which leading or trailing probabilities are to be removed. See `DiscreteDistribution.trimPMF`.  

    Returns
    -------
    DiscreteDistribution
        Steady-state waiting time distribution of the GI/GI/1 queue.
        
    Raises
    -------
    ValueError
        If the system utilization EB/EA>1.
        
    See also
    --------
    `discreteTimeAnalysis.lindley_equation`
    """ 
    if B.mean()/A.mean() >= 1:
        raise ValueError(f'GIGI1_waitingTime: System utilization is rho={B.mean()/A.mean():.2f}>1')     
    return lindley_equation(W0, B-A, epsProb)
    
def kingman(EA, cA, EB, cB):
    r"""Returns the Kingman approximation for the mean waiting time of a GI/GI/1 queue.

    Parameters
    ----------
    EA : float
        Mean interarrival time.
    cA : float
        Coefficient of variation of the interarrival time.
    EB : float
        Mean service time.
    cB : float
        Coefficient of variation of the service time.

    Returns
    -------
    float
        Kingman approximation of the mean waiting time.
        
    Raises
    -------
    ValueError
        If the system utilization EB/EA>1.
    """     
    rho = EB/EA
    if rho>1:
        raise ValueError(f'Kingman: System utilization is rho={rho:.2f}>1')
    return rho/(1-rho)*EB*(cA**2+cB**2)/2

#%% Bernoulli distribution
def BER(p, name=None):
    r"""Returns a Bernoulli distribution.
    
    With the success probability p, the Bernoulli experiment is sucessful.
    \(P(X=1)=p\) and \(P(X=0)=1-p\).

    Parameters
    ----------
    p : float
        Sucess probability.
    name : string, optional (default 'BER(p)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a Bernoulli distribution with success probability p.
        
    Raises
    -------
    ValueError
        If the success probability is not in the range 0<p<1. 
    """         
    if p>1 or p<0:
        raise ValueError(f'BER: success probability {p:.2f} out of range')
    s = f'BER({p:.2f})' if name is None else name
    return DiscreteDistribution([0,1],[1-p,p], name=s)

from scipy.stats import binom
# Binomial distribution
def BINOM(N, p, name=None):
    r"""Returns a Binomial distribution.
    
    The binomial distribution counts the number of successes, if 
    a Bernoulli experiment is repeated N-times with success probability p.
    
    Parameters
    ----------
    N : integer
        Number of Bernoulli experiments.
    p : float
        Sucess probability.
    name : string, optional (default 'BINOM(N,p)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a Binomial distribution with parameters N and p.
        
    Raises
    -------
    ValueError
        If the success probability is not in the range 0<p<1. 
    """         
    if p>1 or p<0:
        raise ValueError(f'BINOM: success probability {p:.2f} out of range')
    s = f'BINOM({N}, {p:.2f})' if name is None else name
    xk = np.arange(N+1)
    return DiscreteDistribution(xk, binom.pmf(xk, N, p), name=s)

from scipy.stats import poisson
# poisson distribution
def POIS(y, eps=1e-8, name=None):
    r"""Returns a Poisson distribution with mean y.
    
    The Poisson distribution is a discrete distribution and has a single parameter 
    reflecting the mean of the random variable. Since the DiscreteDistribution needs to 
    have a finite range, the distribution is truncated at the right side if the probabilities
    are less than `eps`.
    
    Parameters
    ----------
    y : float
        Mean of the Poisson distribution.
    eps : float, optional (default 1e-8)
        Threshold value where to truncate the right part of the CDF.
    name : string, optional (default 'POIS(y)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a Poisson distribution with parameter y.
        
    Raises
    -------
    ValueError
        If the mean value is negative.
    """   
    if y<0:
        raise ValueError(f'POIS: mean value {y:.2f} out of range')
    
    s = f'POIS({y:.2f})' if name is None else name
    
    rv = poisson(y)
    cut = int(rv.isf(eps))
    #print(f'cut at {cut}')
    x = np.arange(cut)
    pk = rv.pmf(x)
    return DiscreteDistribution(x, pk/pk.sum(), name=s)

#%% NEGBIN files
from scipy.stats import nbinom, geom

def getNegBinPars(mu,cx):
    r"""Returns the two parameters of a negative binomial distribution for given mean and coefficient of variation.

    Parameters
    ----------
    mu : float
        Mean value.
    cx : float
        Coefficient of variation.

    Returns
    -------
    a,b : float, float
        Parameters of the negative binomial distribution.
        
    Raises
    -------
    ValueError
        If the parameter range is violated: mu*cx**2>1
    """     
    if mu*cx**2<=1:
        raise ValueError(f'getNegBinPars: parameter range is not possible, mu*cx**2={mu*cx**2:2.f}<=1 ')    
    z = cx**2*mu-1    
    return mu/z, 1- z/(cx**2*mu)


def NEGBIN(EX,cx, eps=1e-8, name=None):
    r"""Returns a negative binomial distribution for given mean and coefficient of variation.

    Parameters
    ----------
    mu : float
        Mean value.
    cx : float
        Coefficient of variation.
    eps : float, optional (default 1e-8)
        Threshold value where to truncate the right part of the CDF.
    name : string, optional (default 'NEGBIN(EX,cx)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a negative binomial distribution with mean EX and coefficient of variation cx.
        
    Raises
    -------
    ValueError
        If the parameter range is violated: mu*cx**2>1
    """     
    r,p = getNegBinPars(EX,cx)
    
    s = f'NEGBIN({EX:.2f},{cx:.2f})' if name is None else name
    
    rv = nbinom(r,p)
    cut = int(rv.isf(eps))
    #print(f'cut at {cut}')
    x = np.arange(cut)
    pk = rv.pmf(x)
    return DiscreteDistribution(x, pk/pk.sum(), name=s)

def DET(EX, name=None):
    r"""Returns a deterministic distribution.

    With probability 1, the distribution takes the value EX.

    Parameters
    ----------
    EX : integer
        Mean value.    
    name : string, optional (default 'DET(EX)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a deterministic distribution with parameter EX.        
    """     
    s = f'DET({EX})' if name is None else name
    return DiscreteDistribution([EX], [1.0], name=s)
    
def DU(a=1, b=10, name=None):    
    r"""Returns a discrete uniform distribution in the range [a,b].

    With the same probability, any value a <= k <=b is taken. 

    Parameters
    ----------
    a : integer
        Lower value range.    
    b : integer
        Upper value range.    
    name : string, optional (default 'DU(a,b)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a discrete uniform distribution in the interval [a;b].        
    """    
    s = f'DU({a},{b})' if name is None else name
    
    xk = np.arange(a,b+1)
    n = b-a+1
    pk = 1.0/n
    return DiscreteDistribution(xk, np.array([pk]*n), name=s)    

def GEOM(EX=1, p=None, m=0, eps=1e-8, name=None):
    r"""Returns a shifted geometric distribution with mean EX or parameter p.

    A shifted geometric distribution is returned which has the mean value `EX`. 
    The distribution is thereby shifted by `m`. Thus, \(P(X=k=0\) for any \(k<m\).
                                                        
    If the parameter p is provided, then p is used and EX is ignored.                                                    
    
    Parameters
    ----------
    EX : float (default 1)
        Mean value of the shifted geometric distribution.
    p : float (default None)
        If the parameter p is provided, then p is used and EX is ignored. 
    m : integer (default 0)
        Distribution is shifted by m.    
    eps : float, optional (default 1e-8)
        Threshold value where to truncate the right part of the CDF.
    name : string, optional (default 'GEOM_m(p)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a shifted geometric distribution with mean EX.        
    """   
    if p is None:     
        p = 1.0/(EX+1-m)    
    else:
        EX = p
    rv = geom(p, loc=m-1)
    cut = int(rv.isf(eps))    
    x = np.arange(cut)
    pk = rv.pmf(x)
    
    s = f'GEOM_{m}({EX:.2f})' if name is None else name   
    return DiscreteDistribution(x, pk/pk.sum(), name=s)

def GEOM0(EX=1, p=None, eps=1e-8, name=None):
    r"""Returns a geometric distribution with mean EX or parameter p.

    A geometric distribution is returned which has the mean value `EX`. 
    If the parameter p is provided, then p is used and EX is ignored.                                                    
    
    Parameters
    ----------
    EX : float (default 1)
        Mean value of the geometric distribution.
    p : float (default None)
        If the parameter p is provided, then p is used and EX is ignored. 
    eps : float, optional (default 1e-8)
        Threshold value where to truncate the right part of the CDF.
    name : string, optional (default 'GEOM_m(p)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a geometric distribution with mean EX.        
    """   
    return GEOM(EX=EX, p=p, eps=eps, name=name)

def GEOM1(EX=1, p=None, eps=1e-8, name=None):
    r"""Returns a geometric distribution (shifted by one) with mean EX or parameter p.

    A geometric distribution (shifted by one) is returned which has the mean value `EX`. 
    If the parameter p is provided, then p is used and EX is ignored.                                                    
    
    Parameters
    ----------
    EX : float (default 1)
        Mean value of the shifted geometric distribution.
    p : float (default None)
        If the parameter p is provided, then p is used and EX is ignored. 
    eps : float, optional (default 1e-8)
        Threshold value where to truncate the right part of the CDF.
    name : string, optional (default 'GEOM_m(p)')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a geometric distribution with mean EX.        
    """   
    return GEOM(EX=EX, p=p, m=1, eps=eps, name=name)


#%% mixture distribution
def MIX(A, w=None, name=None):
    r"""Returns the mixture distribution with weights w.

    Consider a set of independent random variables [A_1,..,A_k].
    A random variable $A$ is now constructed in such a way that with the probability p_i the random variable A_i is selected. 
    
    Parameters
    ----------
    A : list of DiscreteDistributions
        List of distributions. 
    w : list of weights, optional (default w=[1/k, ..., 1/k])
        A distribution is considered with the probabilities given in the list of weights.
    name : string, optional (default 'MIX')
        Name of the distribution for string representation.

    Returns
    -------
    DiscreteDistribution
        Returns a shifted geometric distribution with mean EX.        
        
    Example
    -------
    >>> A = DET(4)
    >>> B = DU(1,10)
    >>> C = MIX( (A,B) )
    >>> D = A+B

    >>> plt.figure(1, clear=True)
    >>> A.plotCDF(label='A')
    >>> B.plotCDF(label='B')
    >>> C.plotCDF(label='MIX')
    >>> D.plotCDF(label='A+B')
    >>> plt.legend()
    """     
    xkMin = min(list(map(lambda Ai: Ai.xk[0], A)))
    xkMax = max(list(map(lambda Ai: Ai.xk[-1], A)))
    
    if w is None:
        n = len(A)
        w = [1.0/n]*n
    
    xk = np.arange( xkMin, xkMax+1)
    pk = np.zeros(len(xk))
    for (Ai, wi) in zip(A,w):
        iA = np.searchsorted(xk, Ai.xk, side='left')
        pk[iA] += Ai.pk*wi
    s = 'MIX' if name is None else name   
    return DiscreteDistribution(xk, pk, name=s)