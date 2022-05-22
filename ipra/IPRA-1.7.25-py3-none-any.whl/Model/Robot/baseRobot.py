from abc import abstractmethod
from itertools import count
import tkinter as tk
from tkinter import *
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
#from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from pandas import ExcelWriter
import xlsxwriter
import time
import pandas as pd
from ipra.Logger.logger import Logger
import json


class BaseRobot:

    STATUS_EXCEPTION = 0
    STATUS_SCRAP_COMPLETE = 1
    STATUS_REPORT_COMPLETE = 2
    
    def __init__(self, policyList, frame, reportPath,inputPath,downloadReport=False):
        self.policyList = policyList
        self.frame = frame
        self.frame.resetProgress()
        self.isLogin = False
        self.isStopped = False
        self.buildReportQueue = []
        self.buildHeaderQueue = []
        self.buildReportThread = None
        self.reportPath = reportPath
        self.inputPath = inputPath
        self.logger = Logger()
        self.downloadReport = downloadReport

    def SearchByIdValue(self, soup, key):
        result = soup.find_all(id=key)
        result_soup = BeautifulSoup(str(result), 'lxml')
        return result_soup

    def SearchByHtmlTagClassValue(self, soup, tag, class_key):
        result = soup.find_all(tag, attrs={'class': class_key})
        result_soup = BeautifulSoup(str(result), 'lxml')
        return result_soup

    def SearchByHtmlTagValueKey(self, soup, tag, key, value):
        result = soup.find_all(tag, attrs={key: value})
        result_soup = BeautifulSoup(str(result), 'lxml')
        return result_soup

    def DoClickUntilNoException(self,xPath,timeout = 5):
        isWaiting = True
        counter = 0
        while isWaiting:
            try:
                self.browser.find_element_by_xpath(xPath).click()
                isWaiting = False
            except:
                time.sleep(1)
                if counter > timeout:
                    isWaiting = False
                else:
                    counter = counter + 1
                

    def setIsStopped(self, status):
        self.isStopped = status

    def getIsStopped(self):
        return self.isStopped

    def startBrowser(self):
        
        appState = {
            "recentDestinations": [
                {
                    "id": "Save as PDF",
                    "origin": "local",
                    "account": ""
                }
            ],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }

        profile = {
            'printing.print_preview_sticky_settings.appState': json.dumps(appState),
            "download.default_directory": self.reportPath,
            'savefile.default_directory': self.reportPath,
            "directory_upgrade": True,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('prefs', profile)
        chrome_options.add_argument('--kiosk-printing')
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

    @abstractmethod
    def waitingLoginComplete(self):
        pass

    @abstractmethod
    def scrapPolicy(self):
        pass
    
    @abstractmethod
    def downloadPolicyReport(self,policy):
        pass

    @abstractmethod
    def buildReport(self):
        pass

    @abstractmethod
    def buildReportOnly(self):
        pass
    
    @abstractmethod
    def buildReportHeaderFullFlow(self):
        pass
    
    @abstractmethod
    def buildReportHeaderHalfFlow(self):
        pass

    def execReport(self):
        self.buildReportOnly()
        
    def execRobot(self):
        self.startBrowser()
        self.waitingLoginComplete()
        self.buildReport()
        self.scrapPolicy()
        self.buildReportThread.join()
        self.browser.close()
