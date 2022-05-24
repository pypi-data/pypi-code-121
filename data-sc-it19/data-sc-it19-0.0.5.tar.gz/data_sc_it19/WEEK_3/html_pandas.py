# readind data from HTML file ---------------------------------------------------
'''
import pandas as pd

tables = pd.read_html('table_data.html')
print('Tables found:', len(tables))
df1 = tables[0]  # Save first table in variable df1
df2 = tables[1]  # Saving next table in variable df2

print('First Table')
print(df1)
print('Another Table')
print(df2)
'''

# Reading HTML Data From URL -----------------------------------------------------
'''
import pandas as pd

tables = pd.read_html('https://en.wikipedia.org/wiki/Python_(programming_language)')
print('Tables found:', len(tables))
df1 = tables[0]  # Save first table in variable df1
print('First Table')
print(df1.head())  # To print first 5 rows
'''

# Reading HTML Data From URL That Requires Authentication -----------------------
# raise HTTPError(req.full_url, code, msg, hdrs, fp)
# urllib.error.HTTPError: HTTP Error 401: UNAUTHORIZED
# $ pip install requests
import pandas as pd
import requests

# Can use auth parameter for authenticated URLs
r = requests.get('https://en.wikipedia.org/wiki/Python_(programming_language)',
                 auth=('john', 'johnspassword'))
tables = pd.read_html(r.text)
print('Tables found:', len(tables))
df1 = tables[0]
print('First Table')
print(df1.head())


# Writing HTML Tables with Python's Pandas --------------------------------------
# This code will produce the following file write_html.html in the current directory
import pandas as pd

df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df.to_html('write_html.html')