'''

*****************************
ExergenicsApi.class.py
*****************************

J.CHRISTIAN JAN 2022
Implements the Exergenics API documented at:

    1. Authentication
        https://app.swaggerhub.com/apis/exergenics/getAuthorizationToken/1.0.0

    2. Data Exchange API
        https://app.swaggerhub.com/apis/exergenics/getBuildings/1.0.0
'''

import json
import requests
import urllib.parse
import boto3
from datetime import date
import uuid
import pandas as pd



class ExergenicsApi:
    # authentication storage
    username, password, authorizationToken = "", "", ""

    # last status and response from a request made
    lastStatus = None
    lastResponse = {}

    # internal counter for iterations
    internalCounter = 0

    # Endpoint for authentication
    authEndpoint = "https://auth.exergenicsportal.com"

    # Endpoint for Data Exchange
    exchangeEndpointProduction = "https://api.exergenicsportal.com"
    exchangeEndpointStaging = "https://f31l6pg1zd.execute-api.ap-southeast-2.amazonaws.com/staging"

    # endpoint for Plotly
    plotlyEndpoint = "http://djago-env.eba-ywiepmh3.us-west-2.elasticbeanstalk.com/{}/{}"
    # plotlyEndpoint = "http://127.0.0.1:8000/{}/{}"

    aws_bucketRoot = "https://exergenics-public.s3.ap-southeast-2.amazonaws.com/"
    aws_bucketName = "exergenics-public"

    # The current version of the API being implemented
    apiVersion = 1

    # mode (production,staging)
    mode = "production"

    # Endpoint Activities
    auth__getAuthorizationToken = "getAuthorizationToken"
    ex__getBuildings = "getBuildings"
    ex__putFile = "putFile"
    ex__getFiles = "getFiles"
    ex__putData = "putData"
    ex__getData = "getData"
    ex__getAllData = "getAllData"
    ex__linkTable = "linkTable"
    ex__deleteFiles = "deleteFiles"
    ex__clearData = "clearData"
    ex__getTreeData = "getTreeData"
    ex__getKeyData = "getKeyData"
    ex__getPlantJobs = "getPlantJobs"

    ex__getJobs = "getJobs"
    ex__JobComplete = "jobStageComplete"
    ex__JobError = "jobStageError"
    ex__JobRunning = "jobStageRunning"
    ex__JobRejected = "jobStageRejected"
    ex__getJob = "getJob"
    ex__setJobData = "setJobData"
    ex__setStage = "setStage"

    ex__sendCSVToPortal = "sendCSVToPortal"


    slackEndpoint = "https://slack.com/api/chat.postMessage"
    slackToken = "xoxb-1346873213426-3302802127301-Z5sczvyXMJw3UmYWKFVbEMK6"

    # Constructor - assign credentials
    def __init__(self, username, password, useProductionApi=True):
        self.username = username
        self.password = password
        if useProductionApi:
            self.useProductionApi()
        else:
            self.useStagingApi()

    def sendSlackMessage(self, text="", channel="bigredbutton"):

        msg = "[{}] {}".format(self.mode, text)
        if self.mode == "staging":
            channel = "{}-staging".format(channel)
        url = "{}".format(self.slackEndpoint, channel, msg)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "Connection": "keepalive",
            "Authorization": "Bearer {}".format(self.slackToken)
        }
        body = {
            "channel": channel,
            "text": msg,
            "as_user": "bigredbutton"
        }
        requests.post(self.slackEndpoint, json=body, headers=headers)

    def useProductionApi(self):
        self.mode = "production"

    def useStagingApi(self):
        self.mode = "staging"

    def getExchangeEndpoint(self):
        if self.mode == "production":
            return self.exchangeEndpointProduction
        return self.exchangeEndpointStaging

    # function: doRequest
    # make a request to the endpoint, returning the json body and status code as a tuple.
    def doRequest(self, endpoint, activity, body):
        request = requests.post(self.getActivityUrl(endpoint, activity), json=body, headers=self.getHeaders())
        self.resetCounter()
        return request.status_code, request.json()

    # function: getHeaders
    # returns a common set of headers each request needs as a minimum or default
    def getHeaders(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "User-Agent": "ExergenicsApi.class.py",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keepalive",
            "apiVersion": str(self.apiVersion),
            "cognitoAuthToken": str(self.authorizationToken)
        }

    # function: getActivityUrl
    # combines the base url of the endpoint being accessed with the specific activity to form a complete endpoint
    def getActivityUrl(self, endpoint, activity):
        return "{}/{}".format(endpoint, activity)

    # function: getBody
    # returns the body element of the last response.
    def getBody(self):
        if self.lastResponse is not None:
            return self.lastResponse['body']
        return None

    # function: getResponseValue
    # returns the object denoted by a specific 'key' offset from the body of the last response.
    def getResponseValue(self, key):
        if self.getBody() is not None:
            return self.getBody()[key]
        return None

    # function: moreResults
    # does the last response have more results left to show
    def moreResults(self):
        return self.numResults() > self.internalCounter

    # function: nextResult
    def nextResult(self):
        if self.lastResponse is None:
            return None

        packet = self.lastResponse[self.internalCounter]
        self.internalCounter += 1
        return packet

    # function: resetCounter
    # reset the internal counter
    def resetCounter(self):
        self.internalCounter = 0

    # function: numResults
    # the number of results returned from the last api call
    def numResults(self):
        if self.lastResponse is None:
            return 0

        return len(self.lastResponse)

    '''
    ********************************
    Start Endpoint Request Functions
    ********************************
    '''

    # function  :   authenticate
    def authenticate(self):
        body = {"username": self.username, "password": self.password}
        self.lastStatus, self.lastResponse = self.doRequest(self.authEndpoint, self.auth__getAuthorizationToken, body)
        if self.lastResponse is None:
            return False

        if "errorMessage" in self.lastResponse:
            exit("Authentication Error: {}".format(self.lastResponse['errorMessage']))
        if "statusCode" in self.lastResponse:
            if int(self.lastResponse['statusCode']) != 200:
                exit("Authentication Error: Status code from server: {}".format(self.lastResponse['statusCode']))

        self.authorizationToken = self.getResponseValue("authorizationToken")
        if self.authorizationToken is None:
            return False
        return True

    # function  : getBuilding
    # param     : buildingCode
    def getBuildings(self, buildingCode=None):
        activityUrl = self.ex__getBuildings
        if buildingCode is not None:
            activityUrl = "{}?buildingCode={}".format(activityUrl, buildingCode)

        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def noResponse(self):
        if self.lastResponse is None:
            return True
        if len(self.lastResponse) == 0:
            return True

    # function  : putFiles
    # param     : plantCode, urlToFile, category, name
    def putFile(self, plantCode, urlToFile, category, name):
        activityUrl = "{}/{}/?urlToFile={}&category={}&name={}".format(self.ex__putFile, plantCode,
                                                                       urllib.parse.quote(urlToFile),
                                                                       urllib.parse.quote(category),
                                                                       urllib.parse.quote(name))
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    # function  : linkTable
    # param     : plantCode, tableName, category
    def linkTable(self, plantCode, tableName, category):
        activityUrl = "{}/{}/?tableName={}&category={}".format(self.ex__linkTable, plantCode,
                                                               urllib.parse.quote(tableName),
                                                               urllib.parse.quote(category))
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    # function  : getFiles
    # param     : plantCode
    def getFiles(self, plantCode, category=None):
        if category is not None:
            activityUrl = "{}/{}?category={}".format(self.ex__getFiles, plantCode, category)
        else:
            activityUrl = "{}/{}".format(self.ex__getFiles, plantCode)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    # function  : deleteFiles
    # param     : plantCode
    # param     : category
    def deleteFiles(self, plantCode, category):
        if category is not None:
            activityUrl = "{}/{}?category={}".format(self.ex__deleteFiles, plantCode, category)
        else:
            activityUrl = "{}/{}".format(self.ex__deleteFiles, plantCode)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    # function  : putData
    # param     : code (any valid code)
    # param     : fieldName
    # param     : value
    def putData(self, code, fieldName, value):

        sendAs = value
        if isinstance(value, list):
            sendAs = json.dumps(value)

        activityUrl = "{}/{}?field={}&value={}".format(self.ex__putData, code, fieldName, sendAs)

        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def sendCSVToPortal(self, jobId):
        activityUrl = "{}/{}".format(self.ex__sendCSVToPortal, jobId)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False

        return True

    # function  : getData
    # param     : code (any valid code)
    # param     : fieldName
    # param     : value
    def getData(self, code, fieldName):
        activityUrl = "{}/{}?field={}".format(self.ex__getData, code, fieldName)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False

        if self.lastResponse["value"][0] == '[' and self.lastResponse["value"][-1] == ']':
            return json.loads(self.lastResponse["value"])
        return self.lastResponse["value"]

    # function  : getKeyData
    # param     : code (any valid code)
    # returns all key data associated with a building (currently contacts, files, dates, urls)
    def getKeyData(self, code):
        activityUrl = "{}/{}".format(self.ex__getKeyData, code)
        print(activityUrl)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})

        # this endpoint comes in as a json dict, api handler expects array, so cast as array.
        self.lastResponse = [self.lastResponse]

        if self.noResponse():
            return False
        return True

    # function  : getAllData
    # param     : code (any valid code)
    def getAllData(self, code):
        allData = {}
        activityUrl = "{}/{}".format(self.ex__getAllData, code)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        while self.moreResults():
            packet = self.nextResult()
            if len(packet["value"]) == 0:
                allData[packet['field']] = ""
            else:
                if packet["value"][0] == '[' and packet["value"][-1] == ']':
                    allData[packet['field']] = json.loads(packet["value"])
                else:
                    allData[packet['field']] = packet["value"]
        return allData

    # function  : clearData
    # param     : code
    # param     : field
    def clearData(self, code, field=None):
        if field is not None:
            activityUrl = "{}/{}?field={}".format(self.ex__clearData, code, field)
        else:
            activityUrl = "{}/{}".format(self.ex__clearData, code)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    # function  : getTreeData
    # param     : treeTag
    def getTreeData(self, treeTag):
        activityUrl = "{}/{}".format(self.ex__getTreeData, treeTag)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def sendToBucket(self, localFile, contentType="text/csv"):
        # create a new name for this file

        client = boto3.client(
            's3',
            aws_access_key_id="AKIATI6JSONTMMCSFQXL",
            aws_secret_access_key="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"
        )
        today = date.today()
        saveAs = "{}/{}/{}/{}__{}".format(today.year, today.month, today.day, uuid.uuid4().hex, localFile)
        client.upload_file(Filename=localFile, Bucket=self.aws_bucketName, Key=saveAs,
                           ExtraArgs={'ContentType': contentType})
        return "{}{}".format(self.aws_bucketRoot, saveAs)

    def getJobs(self, stage, status="completed"):
        activityUrl = "{}/{}/{}".format(self.ex__getJobs, stage, status)

        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})

        if self.noResponse():
            return False
        return True

    def getJobsByPlant(self, plantCode):
        activityUrl = "{}/{}".format(self.ex__getPlantJobs, plantCode)

        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})

        if self.noResponse():
            return False
        return True

    def setStage(self, jobId, stage, status):
        activityUrl = "{}/{}/{}/{}".format(self.ex__setStage,  jobId, stage, status)

        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})

        if self.noResponse():
            return False
        return True

    def setJobStageComplete(self, jobId):
        activityUrl = "{}/{}".format(self.ex__JobComplete, jobId)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def setJobStageError(self, jobId, errorMessage=None):
        if not errorMessage:
            errorMessage = "No error details were provided"
        activityUrl = "{}/{}?errorMessage={}".format(self.ex__JobError, jobId, errorMessage)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def setJobStageRejected(self, jobId, rejectedMessage=None):
        if not rejectedMessage:
            rejectedMessage = "No rejection details were provided"
        activityUrl = "{}/{}?rejectedMessage={}".format(self.ex__JobRejected, jobId, errorejectedMessagerMessage)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def setJobStageRunning(self, jobId, errorMessage=None):
        if not errorMessage:
            errorMessage = "No error details were provided"
        activityUrl = "{}/{}?errorMessage={}".format(self.ex__JobRunning, jobId, errorMessage)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def getJob(self, jobId):
        activityUrl = "{}/{}".format(self.ex__getJob, jobId)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def setJobData(self, jobId, fieldName, fieldValue):
        activityUrl = "{}/{}?fieldName={}&fieldValue={}".format(self.ex__setJobData, jobId, fieldName, fieldValue)
        print(activityUrl)
        self.lastStatus, self.lastResponse = self.doRequest(self.getExchangeEndpoint(), activityUrl, {})
        if self.noResponse():
            return False
        return True

    def plotlyRequest(self, chartType="linechart", params=None, returnValue="urlToLineChart"):
        if params is None:
            params = {}
        getRequest = "?"
        for key in params:
            getRequest = getRequest + "{}={}&".format(key, params[key])
        endpoint = self.plotlyEndpoint.format(chartType, getRequest.replace(" ", "%20"))
        request = requests.get(url=endpoint)
        return request.json()[returnValue]

    '''
    example csv: http://exergenics-public.s3.ap-southeast-2.amazonaws.com/2021/12/14/df8c76a12b316b4cf67e909524f74395___test-chart.csv
    http://djago-env.eba-ywiepmh3.us-west-2.elasticbeanstalk.com/linechart/?title=Chart Title&xAxisTitle=xAxisTitle&yAxisTitle=yAxisTitle&legendTitle=legendTitle&chartWidth=800&chartHeight=600&url2csv=https://exergenics-public.s3.ap-southeast-2.amazonaws.com/2022/3/4/c85e47fc33404edd89ffb31f449d4046__/tmp/data.csv&

    example get request
    http://djago-env.eba-ywiepmh3.us-west-2.elasticbeanstalk.com/linechart/?legendTitle=legend title here&width=800&height=600&title=Chart Title Here&url2csv=http://exergenics-public.s3.ap-southeast-2.amazonaws.com/2021/12/14/df8c76a12b316b4cf67e909524f74395___test-chart.csv
    '''

    def plotlyLineChart(self, dataFrame, title="title", xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                        legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                        fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                        legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                        titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)
        return self.plotlyRequest("linechart", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "outputType":outputType,
        })

    def portalChart_lineChart(self, plantCode, chartName, portalCategory, dataFrame, title="title",
                              xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                              legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                              fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                              legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                              titleColor="black"):
        urlToChart = self.plotlyLineChart(dataFrame, title, xAxisTitle, yAxisTitle,outputType, legendTitle,
                                          chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                          fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                          titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def plotlyBarChart(self, dataFrame, title="title", xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                       legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                       fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                       legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                       titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)
        return self.plotlyRequest("barchart", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "outputType":outputType
        }, "urlToBarChart")

    def portalChart_barChart(self, plantCode, chartName, portalCategory, dataFrame, title="title",
                             xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                             legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                             fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                             legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                             titleColor="black"):
        urlToChart = self.plotlyBarChart(dataFrame, title, xAxisTitle, yAxisTitle,outputType, legendTitle,
                                         chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                         fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                         titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def plotlyRadarChart(self, dataFrame, title="title", xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                         legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                         fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                         legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                         titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)
        return self.plotlyRequest("radarchart", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "outputType":outputType,
        }, "urlToRadarChart")

    def portalChart_radarChart(self, plantCode, chartName, portalCategory, dataFrame, title="title",
                               xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                               legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                               fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                               legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                               titleColor="black"):
        urlToChart = self.plotlyRadarChart(dataFrame, title, xAxisTitle, yAxisTitle,outputType, legendTitle,
                                           chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                           fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                           titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def plotlyScatterPlot(self, dataFrame, title="title", xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                          legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                          fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                          legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                          titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)
        return self.plotlyRequest("scatterplot", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "outputType":outputType
        }, "urlToScatterPlotChart")

    def portalChart_scatterPlot(self, plantCode, chartName, portalCategory, dataFrame, title="title",
                                xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                                legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                                fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                                legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                                titleColor="black"):
        urlToChart = self.plotlyScatterPlot(dataFrame, title, xAxisTitle, yAxisTitle,outputType, legendTitle,
                                            chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                            fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                            titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def plotlyStackedBarGraph(self, dataFrame, title="title", xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                              legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                              fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                              legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                              titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)
        return self.plotlyRequest("stackedbargraph", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "outputType":outputType
        }, "urlToStackedBarChart")

    def portalChart_stackedbarGraph(self, plantCode, chartName, portalCategory, dataFrame, title="title",
                                    xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                                    legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                                    fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                                    legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                                    titleColor="black"):
        urlToChart = self.plotlyStackedBarGraph(dataFrame, title, xAxisTitle, yAxisTitle,outputType, legendTitle,
                                                chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                                fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                                titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def plotlyHistogram(self, dataFrame, title="title", xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                        legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                        fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                        legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                        titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)
        return self.plotlyRequest("histogram", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "outputType":outputType
        }, "urlToHistogram")

    def portalChart_histogram(self, plantCode, chartName, portalCategory, dataFrame, title="title",
                              xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",outputType="html",
                              legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                              fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                              legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                              titleColor="black"):
        urlToChart = self.plotlyHistogram(dataFrame, title, xAxisTitle, yAxisTitle,outputType, legendTitle,
                                          chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                          fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                          titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def plotlySurfacePlot(self, dataFrame, lift, load, cop, title="title", xAxisTitle="xAxisTitle",
                          yAxisTitle="yAxisTitle",zAxisTitle ="zAxisTitle",outputType="html",
                          legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                          fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                          legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                          titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)

        tmpLift = "/tmp/lift.csv"
        lift.to_csv(tmpLift, index=False, index_label=False)

        tmpLoad = "/tmp/load.csv"
        load.to_csv(tmpLoad, index=False, index_label=False)

        tmpCop = "/tmp/cop.csv"
        cop.to_csv(tmpCop, index=False, index_label=False)

        return self.plotlyRequest("surfaceplot", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "zAxisTitle":zAxisTitle,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "liftcsv": self.sendToBucket(tmpLift),
            "loadcsv": self.sendToBucket(tmpLoad),
            "copcsv": self.sendToBucket(tmpCop),
            "outputType":outputType
        }, "urlToSurfacePlot")

    def portalChart_surfacePlot(self, plantCode, chartName, portalCategory, dataFrame, lift, load, cop, title="title",
                                xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",zAxisTitle="zAxisTitle",outputType="html",
                                legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                                fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                                legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                                titleColor="black"):
        urlToChart = self.plotlySurfacePlot(dataFrame, lift, load, cop, title, xAxisTitle, yAxisTitle,zAxisTitle,outputType,legendTitle,
                                            chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                            fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                            titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def plotlyBowlChart(self, dataFrame, title="title", xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",yAxis2="SecondAxis",
                        outputType="html",legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                        fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                        legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                        titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)
        return self.plotlyRequest("bowlchart", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "yAxis2":yAxis2,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "outputType":outputType
        },"urlToBowlChart")

    def portalChart_bowlChart(self, plantCode, chartName, portalCategory, dataFrame, title="title",
                              xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",yAxis2="SecondTitle",outputType="html",
                              legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                              fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                              legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                              titleColor="black"):
        urlToChart = self.plotlyBowlChart(dataFrame, title, xAxisTitle, yAxisTitle,yAxis2,outputType, legendTitle,
                                          chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                          fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                          titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def plotlyBowlChart3d(self, dataFrame, x, y, z, title="title", xAxisTitle="xAxisTitle",
                          yAxisTitle="yAxisTitle",zAxisTitle="zAxisTitle",outputType="html",
                          legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                          fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                          legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                          titleColor="black"):
        tmpFile = "/tmp/data.csv"
        dataFrame.to_csv(tmpFile, index=False, index_label=False)

        tmpX = "/tmp/x.csv"
        x.to_csv(tmpX, index=False, index_label=False)

        tmpY = "/tmp/load.csv"
        y.to_csv(tmpY, index=False, index_label=False)

        tmpZ = "/tmp/cop.csv"
        z.to_csv(tmpZ, index=False, index_label=False)

        return self.plotlyRequest("bowlchart3d", {
            "title": title,
            "xAxisTitle": xAxisTitle,
            "yAxisTitle": yAxisTitle,
            "zAxisTitle": zAxisTitle,
            "outputType" : outputType,
            "legendTitle": legendTitle,
            "chartWidth": chartWidth,
            "chartHeight": chartHeight,
            "url2csv": self.sendToBucket(tmpFile),
            "backgroundColor": backgroundColor,
            "fontSize": fontSize,
            "fontFamily": fontFamily,
            "fontColor": fontColor,
            "legendFamily": legendFamily,
            "legendSize": legendSize,
            "legendColor": legendColor,
            "legendBg": legendBg,
            "titleFont": titleFont,
            "titleColor": titleColor,
            "xcsv": self.sendToBucket(tmpX),
            "ycsv": self.sendToBucket(tmpY),
            "zcsv": self.sendToBucket(tmpZ)
        }, "urlToBowlChart3d")

    def portalChart_BowlChart3d(self, plantCode, chartName, portalCategory, dataFrame, x, y, z, title="title",
                                xAxisTitle="xAxisTitle", yAxisTitle="yAxisTitle",zAxisTitle="zAxisTitle",outputType="html",
                                legendTitle="legendTitle", chartWidth=800, chartHeight=600, backgroundColor="white",
                                fontSize=12, fontFamily="TimesNewRoman", fontColor="black", legendFamily="Courier",
                                legendSize=12, legendColor="black", legendBg="LightSteelBlue", titleFont="Arial",
                                titleColor="black"):
        urlToChart = self.plotlyBowlChart3d(dataFrame, x, y, z, title, xAxisTitle, yAxisTitle,zAxisTitle,outputType,legendTitle,
                                            chartWidth, chartHeight, backgroundColor, fontSize, fontFamily,
                                            fontColor, legendFamily, legendSize, legendColor, legendBg, titleFont,
                                            titleColor)
        self.putFile(plantCode, urlToChart, portalCategory, chartName)
        return urlToChart

    def matlabArraytoDataFrame(self,arr):
        df = pd.DataFrame(arr)
        df = df.transpose()
        return df
