# coding: utf-8

METIS_URL = 'https://your.metis.com'

LOGIN_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6,ja;q=0.5',
    'Connection': 'keep-alive',
    'Content-Length': '92',
    'Content-Type': 'application/json',
    'Cookie': 'loginType=PASSWORD',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'
}

MEITS_API_PATH = {
    "auth": "/api/user/auth",
    "metis": "/api/uni-search/metis",
    "jira": "/api/uni-search/jira",
    "wiki": "/api/uni-search/confluence",
    "aiops": "/api/uni-search/aiops",
    "intkb": "/api/uni-search/intkb",
    "personalTicketCheck": "/api/cases-check"
}