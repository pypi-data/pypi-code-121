import requests

import getpass

import snowflake
import snowflake.connector



def get_tokens(auth_url):
    #get the tokens
    username = input('Username: ')
    password = getpass.getpass(prompt='Password: ')

    data = {
    'client_id': 'snowflake',
    'grant_type': 'password',
    'username': username,
    'password': password,
    'client_secret': 'snowflake',
    'scope': 'session:role-any',
    'encode': 'form'
    }

    response = requests.post(auth_url, data=data)
    json_response=response.json()
    oauth_token = json_response['access_token']
    refresh_token =json_response['refresh_token']
    return oauth_token, refresh_token


def query (con="",sql=""):
    
    try:
        df=pd.read_sql_query(sql,con)
    except Exception as e:
        print("*** ERROR *** The query: [", sql, "] failed. Here's the original error message: ",e)
        return
    
    print("The query: [", sql, "] was successful.")
    return df

def use_role (con="", role=None):
    if role==None:
        print("*** ERROR *** You need to specify a role.")
        
    try:
        cur = con.cursor()
        sql= "USE ROLE " + role
        cur.execute(sql)
        cur.close()
    except Exception as e:
        print ("*** ERROR *** Assignment of user to role ", role, " failed. Here's the original error message: ",e)
        return
    
    print("Assignment of user to ", role, " was successful.")

def use_database (con="", database=None):
    if database==None:
        print("*** ERROR *** You need to specify a database.")
        
    try:
        cur = con.cursor()
        sql= "USE DATABASE " + database
        cur.execute(sql)
        cur.close()
    except Exception as e:
        print ("*** ERROR *** Snowflake connection to ", database, " failed. Here's the original error message: ",e)
        return
    
    print("Snowflake connection to ", database, " was successful.")

def use_warehouse (con="", warehouse=None):
    if warehouse==None:
          print("*** ERROR *** You need to specify a warehouse.")
          
    try:
        cur = con.cursor()
        sql= "USE WAREHOUSE " + warehouse
        cur.execute(sql)
        cur.close()
    except Exception as e:
        print("*** ERROR *** The warehouse: ", warehouse, " cannot be used. Here's the original error message: ",e)
        return
    
    print("The warehouse: ", warehouse, " is running.")


def use_schema (con="", schema=None):
    if schema==None:
          print("*** ERROR *** You need to specify a warehouse.")
          
    try:
        cur = con.cursor()
        sql= "USE SCHEMA " + schema
        cur.execute(sql)
        cur.close()
    except Exception as e:
        print("*** ERROR *** The schema: ", schema, " cannot be used. Here's the original error message: ",e)
        return
    
    print("The current schema: ", schema)


def connect(oauth_token=None, account=None, sf_db=None, sf_role=None, sf_schema=None, sf_warehouse=None):
    con = snowflake.connector.connect(
        account = account,
        authenticator = 'oauth',
        token = oauth_token
    )
    if sf_role:
        use_role(con, sf_role)
    if sf_db:
        use_database(con, sf_db)
    if sf_schema:
        use_schema(con, sf_schema)
    if sf_warehouse:
        use_warehouse(con, sf_warehouse)
    return con
    

def get_createtablestmnt(eos_df, table_name):
    
    smt = "CREATE OR REPLACE TABLE "  + table_name + " ("
    for col in eos_df.columns:
        if (
            eos_df[col].dtype.name == "int"
            or eos_df[col].dtype.name == "int64"
        ):
            smt = smt + col + " int"
        elif eos_df[col].dtype.name == "float64":
            smt = smt + col + " float8"
        elif eos_df[col].dtype.name == "bool":
            smt = smt + col + " boolean"  
        elif eos_df[col].dtype == "datetime64[ns]":
            smt = smt + col + " datetime"
        elif eos_df[col].dtype == "object":
            smt = smt + col + " varchar(16777216)"
        else:
            smt = smt + col + " varchar(16777216)"
        if eos_df[col].name != eos_df.columns[-1]:
            smt = smt + ","
        else:
            smt = smt + ")"
    return smt


def fix_date_cols(df, tz = 'UTC'):
    cols = df.select_dtypes(include=['datetime64[ns]']).columns
    for col in cols:
        df[col] = df[col].dt.tz_localize(tz)

def execute_sql(con, stmt):
    results = con.cursor().execute(stmt).fetchall()
    for res in results:
        print(res)
    return results


