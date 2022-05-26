class mf_movement():
    
    def __init__(self):
        import pandas as pd
        self.keeper = 'tbd'
        self.num_days = 0 #number of days for group size; used in line 60
        self.days_back = 400 #number of days to go back from today to collect data. line 152
        self.df_summary_table = pd.DataFrame(columns = ['n', 'Static_Profit', 'Dynamic_Profit', 'Dynamic_Over_Static'])
        self.n = 0
        self.begin_shares = 1
        self.days_to_keep = 60
        self.starting_index = 0
    
    def obj_to_date(self, df):
        import pandas as pd
        df['Date'] = pd.to_datetime(df['Date'])
        
    def cmf(self, df):
        self.num_days = int(input('What is the group size to be used for the cmf? '))
        df['pre_cmf'] = ((df['close_low'] - df['high_close']) / df['high_low']) * df['Volume']
        df['cmf'] = df['pre_cmf'].rolling(self.num_days).sum() / df['Volume'].rolling(self.num_days).sum()
        df = df.dropna()
        return df
    
    def differences(self, df):
        df['high_low'] = df['High'] - df['Low']
        df['open_close'] = df['Open'] - df['Close']
        df['open_high'] = df['Open'] - df['High']
        df['open_low'] = df['Open'] - df['Low']
        df['high_close'] = df['High'] - df['Close']
        df['close_low'] = df['Close'] - df['Low']
        return df    
    
    def yahoo_api(self):
        import pandas as pd
        import yfinance as yf
        from datetime import datetime, timedelta

        symbol = input('What is the stock symbol? ')
        print('The symbol is: ', symbol)
        end_date = datetime.now()       
        d = timedelta(days = self.days_back) #you are getting self.days_back records (first self.num_days dropped when calculated 20 simple moving average.)
        a = end_date - d # goes back self.days_back
        end_date = end_date.strftime('%Y-%m-%d') #keeps only the date ... removes the time stamp
        begin_date = a.strftime('%Y-%m-%d')

        df = yf.download(symbol,
        start = begin_date,
        end = end_date,
        progress = False)
        
        #display('In api:', df)
        #df.to_csv('test.csv')
        
        return df
        
    def cmf_stats(self, df):
        
        df1 = df.copy() #to fix: A value is trying to be set on a copy of a slice from a DataFrame.
        df1.reset_index(inplace=True)   
        df1['Category'] = 'Neutral'
        
        i = 0
        while i < len(df):
            #print(i, df.loc[i, 'cmf'])
            if df1.loc[i, 'cmf'] > 0: # column 14 is cmf 
                df1.loc[i, 'Category'] = 'Positive' # column 15 is Category 
            else:
                df1.loc[i, 'Category'] = 'Negative'
                
            i += 1
        
        print('average cmf:', df1['cmf'].mean())
        print('median cmf:', df1['cmf'].median())
        print('\naverage pos/neg cmf:', df1[['Category', 'cmf']].groupby('Category').mean())
        print('\nthe number of pos/neg cmf:', df1[['Category', 'cmf']].groupby('Category').count())
        
        
        #print('It has been in this phase for', no_days, 'days.')
        
        return df1
    
    def sub_grouping(self, df):
        import pandas as pd
        
        df_category_groupings = pd.DataFrame(columns = ['Date', 'Close', 'Days', 'cmf', 'Category'])
        
        i = 1
        counter = 1
        
        while i < len(df): #creates a dataframe that captures the number of days that the cmf is in accumulation or distribution (pos or neg.)
            if df.loc[i, 'Category'] == df.loc[ i - 1, 'Category']:
                counter += 1
            else:
                counter = 1
            
            # The list to append as row
            ls = [df.loc[i, 'Date'], df.loc[i,'Close'], counter, df.loc[i, 'cmf'], df.loc[i, 'Category']]
            
            # Create a pandas series from the list
            row = pd.Series(ls, index=df_category_groupings.columns)

            # Append the row to the dataframe
            df_category_groupings = df_category_groupings.append(row, ignore_index=True)

            i += 1
        
        max_close_value = df_category_groupings['Close'].max()
        
        df_category_groupings['normalized_close'] = df_category_groupings['Close'] / max_close_value #normalizes the clost price
        
        mean_normalized_close = df_category_groupings['normalized_close'].mean()
        
        df_category_groupings['adjusted_normalized_close'] = df_category_groupings['normalized_close'] - mean_normalized_close
        
        df_category_groupings['zero_line'] = 0
        
        #print(len(df_category_groupings))
        print('\nMost recent date: ', df_category_groupings.loc[len(df_category_groupings) - 1, 'Date'])
        print('For this date the cmf is: ', df_category_groupings.loc[len(df_category_groupings) - 1, 'Category'], 'at', df_category_groupings.loc[len(df_category_groupings) - 1, 'cmf'] )
        print('The number of days that the cmf has been in this category is: ', df_category_groupings.loc[len(df_category_groupings) - 1, 'Days'])      
        print('The closing stock price for this period is: ', '${:,.2f}'.format(df_category_groupings.loc[len(df_category_groupings) - 1, 'Close']))
        return df_category_groupings
    
    def summary_plot(self, df):#plotting
        import matplotlib.pyplot as plt
        import pandas as pd
        
        starting_index = 0
        #self.days_to_keep = 60
        
        df = df.drop(index=df.index[self.starting_index : len(df) - self.days_to_keep]) # keeps the last 60 records

        df = df.set_index('Date') #set the Date as the index
                
        df['cmf'] = df['cmf'].astype(float)  #converts string to float
        
        plt.figure(figsize=(8, 5))
        plt.xticks(rotation = 45) # Rotates X-Axis Ticks by 45-degrees
        plt.title("CMF vs Adjusted Normalized Close Curve") 
        plt.plot(df.index, df['cmf'] , c='b', label="cmf") #plots 
        plt.plot(df.index, df['adjusted_normalized_close'] , c='r', label="adjusted normalized close price") #plots the
        plt.plot(df.index, df['zero_line'] , c = 'k')
        plt.legend(loc="upper left")

        plt.show()
     
    def pearson_spearman_corr(self , df):
        # calculate the Pearson's correlation between two variables
        from numpy.random import randn
        from numpy.random import seed
        from scipy.stats import pearsonr
        from scipy.stats import spearmanr
        
        # calculate Pearson's correlation
        corr, _ = pearsonr(df['cmf'], df['adjusted_normalized_close'])
        print('Pearsons correlation: %.3f' % corr)
        
        corr, _ = spearmanr(df['cmf'], df['adjusted_normalized_close'])
        print('Spearmans correlation: %.3f' % corr)

    def output_signal(self):
        import time
        #date = df1.index[0].strftime('%Y-%m-%d')
        print('WARNING: This is for illustration and entertainment purposes ONLY.')
        print('Do NOT use this information for anything. This includes but is not limited to any financial ')
        print('decisions, and/or stock, option and/or bond purchases or sales, real estate transactions or any other decision.' )
        print('If you disregard this warning you do so at your sole risk and you assume all responsibility for the consequences.')
        print('In using this application you also agree that you will indemnify Kokoro Analytics, its officers,')
        print('employees, volunteers, vendors and contractors from any damages incured from disregarding this warning.\n')
        
        time.sleep(.5)
        agreement = input('Press enter if you have read and will abide by the "Warning" statement above.')
        
        if agreement != '':
            import sys 
            print('\nThank you for your interest but we cannot go any further because you entered something other than enter! \nHave a great day!')
            sys.exit()
            
        print('\nWe use the Chaikin Money Flow indicator. What is the Chaikin Money Flow? See the link below.')
        print('https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmf\n')
        
    def smoothing(self, df):
        import numpy as np
        import numpy as np
        from scipy.interpolate import make_interp_spline
        import matplotlib.pyplot as plt

        # Dataset
        
        df = df.drop(index=df.index[self.starting_index : len(df) - self.days_to_keep]) # keeps the last 60 records (days to keep)
        
        x = df.index.to_numpy() #creates an array from the dataframe index
        y = df['cmf'].to_numpy() #cretes an array from the cmf column of the dataframe
        z = df['adjusted_normalized_close'].to_numpy() 
        zero = df['zero_line'].to_numpy()

        X_Y_Spline = make_interp_spline(x, y)
        X_Z_Spline = make_interp_spline(x, z)
        X_ZERO_Spline = make_interp_spline(x, zero)

        # Returns evenly spaced numbers
        # over a specified interval.
        X_ = np.linspace(x.min(), x.max(), 15)
        Y_ = X_Y_Spline(X_)
        Z_ = X_Z_Spline(X_)
        ZERO_ = X_ZERO_Spline(X_)
        
        df = df.set_index('Date') #set the Date as the index

        # Plotting the Graph
        plt.figure(figsize=(8, 5))
        plt.plot(X_, Y_, c = 'b', label = 'cmf')
        plt.plot(X_, Z_, c = 'r', label = 'adjusted nomalized close price')
        plt.plot(X_, ZERO_, c = 'k')
        plt.legend(loc="upper left")
        plt.title("Smoothed CMF vs Adjusted Normalized Close Curve") 
        
        #Using the scipy.interpolate.make_interp_spline() Class")
        plt.xlabel("X")
        plt.ylabel("Y")
    
        plt.show()

