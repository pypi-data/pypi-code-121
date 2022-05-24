import pandas as pd
import numpy as np

# data frame - 1 
d1 = {'Customer_id': pd.Series([1,2,3,4,5,6]),
'Product':pd.Series(['Oven', 'Oven', 'Oven', 'TV', 'TV', 'TV'])
}
df1 = pd.DataFrame(d1)


# data frame - 2
d2 = {'Customer_id': pd.Series([2,4,6,7,8]),
'State':pd.Series(['California', 'California', 'Texas', 'New York', 'Indiana'])
}
df2 = pd.DataFrame(d2)

# INNER JOIN
# inner_join_df = pd.merge(df1, df2, on="Customer_id", how="inner")
# print(inner_join_df)

# # OUTER JOIN
# outer_join_df = pd.merge(df1, df2, on="Customer_id", how="outer")
# print(outer_join_df)

# # LEFT JOIN
# left_join_df = pd.merge(df1, df2, on="Customer_id", how="left")
# print(left_join_df)

# RIGHT JOIN
# right_join_df = pd.merge(df1, df2, on="Customer_id", how="right")
# print(right_join_df)

