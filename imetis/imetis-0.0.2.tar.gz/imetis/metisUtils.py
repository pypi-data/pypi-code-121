# coding: utf-8

from imetis.metisSettings import METIS_URL, MEITS_API_PATH, LOGIN_HEADERS
import requests
from urllib.parse import quote

class MetisClient(object):
    
    def __init__(self, metisUrl=METIS_URL):
        '''
        Initialize a Metis client object. 
        *OPTIONAL: You can set Metis url with the argument 'metisUrl', otherwise it will use the default setting.
        '''
        self.metisUrl = metisUrl
        self.sessionStatus = False
        self.authenticateStatus = False
        self.__init_session()
        
        
    def __init_session(self):
        '''
        Initialize a requests session.
        '''
        try:
            self.session = requests.session()
            self.sessionStatus = True
        except Exception:
            self.sessionStatus = False
            raise
        
        
    def __get_api_url(self, api):
        '''
        Find API url by API name.
        '''
        try:
            path = MEITS_API_PATH[api]
        except Exception:
            raise KeyError('No API found: %s.' % api)
        
        url = self.metisUrl.rstrip('/') + path
        
        return url        
    
    
    def authenticate(self, username, password):
        '''
        Log into Metis with your username and password.
        '''
        if self.sessionStatus != True:
            self.authenticateStatus = False
            raise ConnectionError('Session not established. sessionStatus: %s.' % self.sessionStatus)
            
        url = self.__get_api_url('auth')
        
        body = {
            "emailAddress": username,
            "passWord": password
        }
        
        response = self.session.post(url, json=body, headers=LOGIN_HEADERS, verify=False)
        
        status = response.status_code
        
        if status != 200:
            self.authenticateStatus = False
            raise ConnectionError('Authentication failed. Status Code: %s.' % status)
        
        self.authenticateStatus = True
        
        cookies = response.cookies.get_dict()
        token = cookies["jwToken"]
        self.token = token
        self.email = username
        
        return        
    
    
    def ticket_search(self, keyword, num=10):
        '''
        Basic ticket search by keyword.
        '''
        if self.authenticateStatus != True:
            raise PermissionError('You must authenticate first to do so.')
        
        url = self.__get_api_url('metis')
        
        qlOrigin = '((TICKET_TITLE token match "%s" or TICKET_DESCRIPTION token match "%s" or TICKET_SOLUTION token match "%s") and TICKET_COMMENT_CONTENT token match "%s") or (TICKET_TITLE ~ "%s" or TICKET_DESCRIPTION ~ "%s" or TICKET_SOLUTION ~ "%s")' % (keyword, keyword, keyword, keyword, keyword, keyword, keyword)
        ql = quote(qlOrigin)
        
        url = url + "?ql=%s&page=0&pageSize=%s" % (ql, num)
        
        #print(url)
        
        response = self.session.get(url, headers={"Authorization": "Bearer %s" % (self.token)}, verify=False)
        
        status = response.status_code
        
        if status != 200:
            raise ConnectionError('Query failed. Status Code: %s.' % status)
        
        temp = response.json()
        total = temp["content"]["total"]
        data = temp["content"]["data"]
        
        tickets = self.__get_format_tickets(data)
        
        return {"totalNum": total, "cases": tickets}
    
    
    def ticket_search(self, keyword, num=10):
        '''
        Basic ticket search by keyword.
        '''
        if self.authenticateStatus != True:
            raise PermissionError('You must authenticate first to do so.')
        
        url = self.__get_api_url('metis')
        
        qlOrigin = '((TICKET_TITLE token match "%s" or TICKET_DESCRIPTION token match "%s" or TICKET_SOLUTION token match "%s") and TICKET_COMMENT_CONTENT token match "%s") or (TICKET_TITLE ~ "%s" or TICKET_DESCRIPTION ~ "%s" or TICKET_SOLUTION ~ "%s")' % (keyword, keyword, keyword, keyword, keyword, keyword, keyword)
        ql = quote(qlOrigin)
        
        url = url + "?ql=%s&page=0&pageSize=%s" % (ql, num)
        
        #print(url)
        
        response = self.session.get(url, headers={"Authorization": "Bearer %s" % (self.token)}, verify=False)
        
        status = response.status_code
        
        if status != 200:
            raise ConnectionError('Query failed. Status Code: %s.' % status)
        
        temp = response.json()
        total = temp["content"]["total"]
        data = temp["content"]["data"]
        
        tickets = self.__get_format_tickets(data)
        
        return {"totalNum": total, "cases": tickets}
    
    
    def jira_search(self, keyword, num=10):
        '''
        Jira case search by keyword.
        '''
        if self.authenticateStatus != True:
            raise PermissionError('You must authenticate first to do so.')
        
        url = self.__get_api_url('jira')
        
        #kwOrigin = '((TICKET_TITLE token match "%s" or TICKET_DESCRIPTION token match "%s" or TICKET_SOLUTION token match "%s") and TICKET_COMMENT_CONTENT token match "%s") or (TICKET_TITLE ~ "%s" or TICKET_DESCRIPTION ~ "%s" or TICKET_SOLUTION ~ "%s")' % (keyword, keyword, keyword, keyword, keyword, keyword, keyword)
        kw = quote(keyword)
        
        url = url + "?keyword=%s&sortField=&sortOrder=&page=0&pageSize=%s" % (kw, num)
        
        #print(url)
        
        response = self.session.get(url, headers={"Authorization": "Bearer %s" % (self.token)}, verify=False)
        
        status = response.status_code
        
        if status != 200:
            raise ConnectionError('Query failed. Status Code: %s.' % status)
        
        temp = response.json()
        total = temp["content"]["total"]
        data = temp["content"]["data"]
        
        cases = self.__get_format_jira_cases(data)
        
        return {"totalNum": total, "cases": cases}
    
    
    def wiki_search(self, keyword, num=10):
        '''
        WIKI case search by keyword.
        '''
        if self.authenticateStatus != True:
            raise PermissionError('You must authenticate first to do so.')
        
        url = self.__get_api_url('wiki')
        
        #kwOrigin = '((TICKET_TITLE token match "%s" or TICKET_DESCRIPTION token match "%s" or TICKET_SOLUTION token match "%s") and TICKET_COMMENT_CONTENT token match "%s") or (TICKET_TITLE ~ "%s" or TICKET_DESCRIPTION ~ "%s" or TICKET_SOLUTION ~ "%s")' % (keyword, keyword, keyword, keyword, keyword, keyword, keyword)
        kw = quote(keyword)
        
        url = url + "?keyword=%s&page=0&pageSize=%s" % (kw, num)
        
        #print(url)
        
        response = self.session.get(url, headers={"Authorization": "Bearer %s" % (self.token)}, verify=False)
        
        status = response.status_code
        
        if status != 200:
            raise ConnectionError('Query failed. Status Code: %s.' % status)
        
        temp = response.json()
        total = temp["content"]["total"]
        data = temp["content"]["data"]
        
        cases = self.__get_format_wiki_cases(data)
        
        return {"totalNum": total, "cases": cases}
    
    
    def aiops_search(self, keyword, num=10):
        '''
        AIOPS case search by keyword.
        '''
        if self.authenticateStatus != True:
            raise PermissionError('You must authenticate first to do so.')
        
        url = self.__get_api_url('aiops')
        
        #kwOrigin = '((TICKET_TITLE token match "%s" or TICKET_DESCRIPTION token match "%s" or TICKET_SOLUTION token match "%s") and TICKET_COMMENT_CONTENT token match "%s") or (TICKET_TITLE ~ "%s" or TICKET_DESCRIPTION ~ "%s" or TICKET_SOLUTION ~ "%s")' % (keyword, keyword, keyword, keyword, keyword, keyword, keyword)
        kw = quote(keyword)
        
        url = url + "?keyword=%s&page=0&pageSize=%s" % (kw, num)
        
        #print(url)
        
        response = self.session.get(url, headers={"Authorization": "Bearer %s" % (self.token)}, verify=False)
        
        status = response.status_code
        
        if status != 200:
            raise ConnectionError('Query failed. Status Code: %s.' % status)
        
        temp = response.json()
        total = temp["content"]["total"]
        data = temp["content"]["data"]
        
        cases = self.__get_format_aiops_cases(data)
        
        return {"totalNum": total, "cases": cases}
    
    
    def intkb_search(self, keyword, num=10):
        '''
        Internal KB case search by keyword.
        '''
        if self.authenticateStatus != True:
            raise PermissionError('You must authenticate first to do so.')
        
        url = self.__get_api_url('intkb')
        
        #kwOrigin = '((TICKET_TITLE token match "%s" or TICKET_DESCRIPTION token match "%s" or TICKET_SOLUTION token match "%s") and TICKET_COMMENT_CONTENT token match "%s") or (TICKET_TITLE ~ "%s" or TICKET_DESCRIPTION ~ "%s" or TICKET_SOLUTION ~ "%s")' % (keyword, keyword, keyword, keyword, keyword, keyword, keyword)
        kw = quote(keyword)
        
        url = url + "?keyword=%s&page=0&pageSize=%s" % (kw, num)
        
        #print(url)
        
        response = self.session.get(url, headers={"Authorization": "Bearer %s" % (self.token)}, verify=False)
        
        status = response.status_code
        
        if status != 200:
            raise ConnectionError('Query failed. Status Code: %s.' % status)
        
        temp = response.json()
        total = temp["content"]["total"]
        data = temp["content"]["data"]
        
        cases = self.__get_format_intkb_cases(data)
        
        return {"totalNum": total, "cases": cases}
    
    
    def ticket_search_by_tql(self, tql, num=10):
        '''
        Basic ticket search by TQL (a kind of query language).
        '''
        if self.authenticateStatus != True:
            raise PermissionError('You must authenticate first to do so.')
        
        url = self.__get_api_url('metis')
        
        qlOrigin = tql
        ql = quote(qlOrigin)
        
        url = url + "?ql=%s&page=0&pageSize=%s" % (ql, num)
        
        #print(url)
        
        response = self.session.get(url, headers={"Authorization": "Bearer %s" % (self.token)}, verify=False)
        
        status = response.status_code
        
        if status != 200:
            raise ConnectionError('Query failed. Status Code: %s.' % status)
        
        temp = response.json()
        total = temp["content"]["total"]
        data = temp["content"]["data"]
        
        tickets = self.__get_format_tickets(data)
        
        return {"totalNum": total, "cases": tickets}
    
    
    def personal_ticket_check(self):
        '''
        Check your own tickets. The result will be sent to your email.
        '''
        if self.authenticateStatus != True:
            raise PermissionError('You must authenticate first to do so.')
        
        url = self.__get_api_url('personalTicketCheck') + '/%s' % (self.email) 
        
        response = self.session.get(url, headers={"Authorization": "Bearer %s" % (self.token)}, verify=False)
        
        status = response.status_code
        
        return status
        
    
    def __get_format_tickets(self, data):
        '''
        Format ticket data from source json.
        '''
        result = list()
        for ticket in data:
            d = dict()
            d["ticketId"] = ticket["ticketId"]
            d["ticketNumber"] = ticket["ticketNumber"]
            d["ticketTitle"] = ticket["ticketTitle"]
            d["ticketRequesterName"] = ticket["ticketRequester"]["name"]
            d["ticketRequesterEmail"] = ticket["ticketRequester"]["email"]
            d["ticketRequesterPhone"] = ticket["ticketRequester"]["mobilePhone"]
            d["engineerName"] = ticket["currentEngineer"]["name"]
            d["ticketCategory"] = ticket["ticketCategory"]
            d["ticketStatus"] = ticket["ticketExtStatus"]
            d["ticketPriority"] = ticket["ticketPriority"]
            d["ticketEndUser"] = ticket["ticketEndUser"]
            d["ticketProduct"] = ticket["ticketProduct"]
            d["ticketProductVersion"] = ticket["ticketProductVersion"]
            d["ticketComponents"] = ticket["ticketComponents"]
            d["ticketJiraNumber"] = ticket["ticketJiraNumber"]
            d["ticketDescription"] = ticket["ticketDescription"]
            d["ticketProblemCause"] = ticket["ticketProblemCause"]
            d["ticketSolution"] = ticket["ticketSolution"]
            d["ticketCreateAt"] = ticket["ticketCreateAt"]
            d["ticketSolveAt"] = ticket["ticketSolveAt"]
            d["eweiLink"] = ticket["eweiLink"]
            
            result.append(d)
            
        return result
            
            
    def __get_format_jira_cases(self, data):
        '''
        Format Jira case data from source json.
        '''
        result = list()
        for case in data:
            d = dict()
            d["jiraNumber"] = case["no"]
            d["jiraStatus"] = case["status"]
            d["jiraSubject"] = case["subject"]
            d["jiraLink"] = case["link"]
            d["jiraDescription"] = case["description"]
            d["jiraSolution"] = case["solution"]
            d["components"] = case["components"]
            d["affectedVersions"] = case["affectedVersions"]
            d["solvedAt"] = case["solvedAt"]
            
            result.append(d)
            
        return result
    
    
    def __get_format_wiki_cases(self, data):
        '''
        Format WIKI case data from source json.
        '''
        result = list()
        for case in data:
            d = dict()
            d["wikiType"] = case["type"]
            d["wikiTitle"] = case["title"]
            d["wikiLink"] = case["link"]
            d["wikiContent"] = case["body"]
            
            result.append(d)
            
        return result
    
    
    def __get_format_aiops_cases(self, data):
        '''
        Format AIOPS case data from source json.
        '''
        result = list()
        for case in data:
            d = dict()
            d["aiopsLink"] = case["link"]
            d["components"] = case["components"]
            d["version"] = case["version"]
            d["aiopsDescription"] = case["description"]
            d["aiopsSolution"] = case["solution"]
            
            result.append(d)
            
        return result
    
    
    def __get_format_intkb_cases(self, data):
        '''
        Format Internal KB case data from source json.
        '''
        result = list()
        for case in data:
            d = dict()
            d["kbId"] = case["id"]
            d["intkbLink"] = case["path"]
            d["kbTitle"] = case["title"]
            d["kbAuthor"] = case["author"]
            d["kbAbstract"] = case["highlightContents"]
            d["kbStatus"] = case["status"]
            d["modifiedDate"] = case["modifiedDate"]
            
            result.append(d)
            
        return result