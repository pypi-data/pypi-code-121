from pyrda.dbms.rds import RdClient
def api_getInfo(api_token ='BEC6002E-C3AE-4947-AD70-212CF2B4218B'):
    token1 = "069800C1-C14D"
    token2 = "4574-8DC8"
    token3 = "27B2349BAFBB"
    token_wx = token1 +"-" + token2+"-" + token3
    app1 = RdClient(token= token_wx)
    sql_head = "SELECT  Facct_id   ,Fuser_name   ,Fapp_id     ,Fapp_secret     ,Fserver_url    FROM  t_sec_erpApi  "
    sql_where = " where  FToken ='" +api_token+"' and  FDeleted = 0 "
    sql_all = sql_head + sql_where
    data1 = app1.select(sql_all)
    ncount = len(data1)
    if ncount >0:
        res = data1[0]
    else:
        res = 'Error'
    return(res)
if __name__ == '__main__':
    print(api_getInfo())
    print(api_getInfo('C3BD38AD-8684-488B-831C-DBADBAA05845'))

