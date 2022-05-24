# reading data from html
import pandas as pd

# url: https://stackabuse.com/reading-and-writing-html-tables-with-pandas/
# tables = pd.read_html('table_data.html')
# print('Tables found: ', len(tables))
# df1 = tables[0]
# df2 = tables[1]
# print('First table: \n', df1)
# print('Second table: \n', df2)

# from URL
# tables = pd.read_html('https://en.wikipedia.org/wiki/Python_(programming_language)')
# print('Tables found: ', len(tables))
# df1 = tables[0]
# print('table: \n', df1.head())

# TASK-3: how to filter words that contain at least 2 vowels from a series?
'''
# Input : 
series = pd.Series(['Apple', 'Orange', 'Plum', 'Money'])
# Output:
0  Apple
1  Orange
3  Money
'''

series = pd.Series(['Apple', 'Orange', 'Plum', 'Money'])
# for k in range(len(series)):
#     i = series[k]
#     lower = i.lower()
#     arr = ['a','e','o','i','u']
#     counter = 0
#     for j in lower:
#         if j in arr:
#             counter += 1
    
#     if counter >= 2:
#         print(k, i)

# PANDAS METHOD 
# result = series[series.str.count('(?i)[aeiou]') >= 2]
# print(result)

# TASK-4: how to filter valid emails from a series?
# import re
# import pandas as pd
# emails = pd.Series(['buying books', 'ramzes@msn.com', 'matteo@co', 'ram@cc.com'])
# pattern = '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}'

# def check(emails):
#     if(re.fullmatch(pattern, emails)):
#         print(f" {emails} --- valid email")
#     else:
#         print(f" {emails} --- invalid email")

# PANDAS method
# if __name__ == '__main__':
#     # for i in range(len(emails)):
#     #     check(emails[i])
#     result = emails[emails.str.contains(pat=pattern)]
#     print(result)


# TASK-5: How to change column values when importing csv to a dataframe?
# while importing the dataset, change the 'medv' (median house value)
# column so that values < 25 becomes 'LOW' and > 25 becomes 'HIGH' 

# pd.read_csv('https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv', converters={'medv': lambda x: 'HIGH' if float(x) > 25 else 'LOW'})

# filename = 'https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv'
# def read_my_csv(filename):
#     string_data = pd.read_csv(filename)
#     for val in string_data['medv']:
#         if val > 25:
#             string_data['medv'].replace(val, 'HIGH', inplace=True)
#         else:
#             string_data['medv'].replace(val, 'LOW', inplace=True)
#     return string_data

# if __name__ == '__main__':
#     print(read_my_csv(filename))

# PANDAS WAY
df = pd.read_csv('https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv')
df['medv'] = df['medv'].apply(lambda x: 'HIGH' if x > 25 else 'LOW')

print(df.head())