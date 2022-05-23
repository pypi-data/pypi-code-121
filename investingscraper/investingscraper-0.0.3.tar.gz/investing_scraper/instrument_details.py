import re
import cloudscraper

class InstrumentDetails:
    __url = None

    def __init__(self, url):
        self.__url = url
    
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
        return re.findall(r'<div data-test="instrument-header-details">(.+?)</div></li></ul></div>', data)
    
    def __ParseData(self, data):
        instrument_prices = re.findall(r'instrument-price_instrument-price(.+?)</div></div>', data[0])
        trading_hours = re.findall(r'<li(.+?)</div></li>', data[0] + "</div></li>")
        prices = self.__ParseInstrumentPrices(instrument_prices)
        hours = self.__ParseTradingHours(trading_hours)
        return prices, hours
    
    def __GetData(self, prices, hours):
        data = {
            'instrument-price-last': prices[0],
            'instrument-price_change-value': prices[1],
            'instrument-price_change-percent': prices[2],
            'Prev. Close': hours[0],
            'Bid/Ask': hours[1],
            'Day\'s Range': hours[2]
        }

        return data
    
    def __ParseInstrumentPrices(self, data):
        prices = re.findall(r'<span(.+?)</span>', data[0])
        prices[0] = prices[0].split('>')[-1]
        prices[1] = prices[1].split('>')[-1]
        prices[2] = prices[2].split('+<!')[-1].split('<!')[0].split('>')[-1]
        return prices
    
    def __ParseTradingHours(self, data):
        data[0] = data[0].split('>')[-1]
        bid_ask = re.findall(r'<span class="">(.+?)</span>', data[1])
        data[1] = bid_ask[0] + " / " + bid_ask[1]
        data[2] = data[2].split('>')[-1]
        return data

    def GetInstrumentDetails(self):
        raw_data = self.__GetRawData()
        clean_data = self.__GetCleanData(raw_data)
        prices, hours = self.__ParseData(clean_data)
        data = self.__GetData(prices, hours)
        return data