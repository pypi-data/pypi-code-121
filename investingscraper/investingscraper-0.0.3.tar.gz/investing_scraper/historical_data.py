import re
import pandas
import datetime
import cloudscraper

class HistoricalData:
    __url = None

    def __init__(self, url):
        self.__url = url
    
    def __GetCurrentDate(self):
        currentDate = datetime.datetime.now()
        return datetime.datetime.strptime(currentDate, "%b %d, %Y")
    
    def __GetRawData(self):
        cloudscrap = cloudscraper.create_scraper(
            browser = {
                'browser': 'chrome',
                'platform': 'android',
                'desktop': False
            }
        )
        return str(cloudscrap.get(self.__url).content)
    
    def __GetCleanData(self, data):
        return re.findall(r'<tr(.+?)</tr>', data)
    
    def __ParseData(self, data):
        headers = re.findall(r'>(.+?)</th>', data[0])
        headers[0] = headers[0].split('>')[-1]
        parsed_data = []
        for i in range(1, len(data)):
            values = re.findall(
                r'>(.+?)<', str(data[i].split('/'))
            )
            while values.count("\\\\n") > 0:
                values.remove("\\\\n")
            while values.count("\\\\n ") > 0:
                values.remove("\\\\n ")

            parsed_data.append(values)
        return headers, parsed_data
    
    def __GetDataFrame(self, headers, data):
        dataframe = pandas.DataFrame(data, columns=headers)
        for value in data:
            dataframe.append(value)
        return dataframe    

    def GetHistoricalData(self):
        raw_data = self.__GetRawData()
        clean_data = self.__GetCleanData(raw_data)
        headers, parsed_data = self.__ParseData(clean_data)
        dataframe = self.__GetDataFrame(headers, parsed_data)

        return dataframe