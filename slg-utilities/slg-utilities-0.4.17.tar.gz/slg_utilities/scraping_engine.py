import time
import os
import requests
import re
from bs4 import BeautifulSoup as BS
from pymongo import MongoClient
from .mongo_engine import *
from .file_operations import *
from datetime import datetime as dt
from datetime import timedelta as td
from .helpers import *
from .decorators.decorators import exponential_backoff, db_lookup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'


class Scraper:

    def __init__(self,
                 db='scraped_data',
                 collection=None,
                 db_host=os.environ.get('MONGODB_URI'),
                 update_interval=None,
                 use_selenium=False,
                 selenium_sleep=0,
                 connect_to_db=True):
        '''
        Scraper classes will be tied to the scraped_data db where they will [hopefully] check for data before trying to scrape
        '''
        self.use_selenium = use_selenium
        self.selenium_sleep = selenium_sleep
        if connect_to_db:
            self.db = MongoEngine(db, collection, db_host)
        self.update_interval = update_interval or 720  # minutes
        self.UPDATE_INTERVAL = self.update_interval * 60  # seconds
        self.file_operations = FileOperations()
        # self.user_agent = self.set_user_agent()

    @exponential_backoff()
    def make_request(self,
                     url,
                     headers={'Accept-Encoding': 'identity',
                              'User-Agent': USER_AGENT},
                     params={},
                     data={},
                     type='get',
                     timeout=1,
                     verify=True):

        if re.match('https?://', url) == None:
            url = f"https://{url}"

        return requests.get(
            url, headers=headers, params=params, timeout=timeout,
            verify=verify)

    @db_lookup('scraped_data', 'full_html', 'html')
    def get_html_source(self, selection_filter={'url': 'example_url'}):
        '''
        In order for db_lookup decorator to work we need to specify the selection_filter
        used in order to potentially find a cached value for our html

        Simply pass in the parameter like so: \
            {'url': '<the url you want the html from>'}
        '''
        return self.get_html(selection_filter['url'])

    def get_html(self, url, verify=True):
        '''Preference for using selenium because selenium allows the javascript to be run before returning'''

        if self.use_selenium:
            options = Options()
            options.headless = True
            options.add_argument("window-size=1280,800")
            options.add_argument(f"user-agent={USER_AGENT}")
            options.add_argument(
                '--disable-blink-features=AutomationControlled')
            driver = webdriver.Chrome(
                options=options)
            driver.get(url)
            time.sleep(self.selenium_sleep)
            html = driver.page_source
            return html

        else:
            response = self.make_request(url, verify=verify)
            return response.text

    def get_selenium_driver(self, url):
        options = Options()
        options.headless = True
        options.add_argument("window-size=1920,1080")
        options.add_argument(f"user-agent={USER_AGENT}")
        options.add_argument(
            '--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(
            options=options)
        driver.get(url)
        return driver


    def add_db_entry(self, obj, collection=None, last_updated=True):
        '''
        add obj to collection; if last_updated is true, adds field {'last_updated': dt.now()} to obj
        '''
        if last_updated:
            obj.update({'last_updated': dt.utcnow()})

        self.db[collection].insert_one(obj)

    def get_page_html(self, page_url):
        db_obj = next(self.db["full_html"].find({'page_url': page_url}))
        return db_obj['html'] if(db_obj['created_at'] - dt.now()).seconds < (
            self.update_interval * 60) else self.set_page_html(page_url)

    def set_page_html(self, page_url):
        response = self.make_request(page_url)
        html = response.content.decode('utf-8')
        obj = {'page_url': page_url,
               'html': html}
        self.add_db_entry('full_html', obj)
        return html

    # deprecated cause ugly db_lookup decorator will solve issues of finding specific html, sections wont be stored, only the full html
    # methods for gathering the sections will be defined from the html source which will be generally either updated daily
    # def get_section_html(self, html, section):
    #     db_obj = next(self.db["sections"].find({'section': section}))
    #     return db_obj['html'] if (db_obj['created_at'] - dt.now()).seconds < (self.update_interval * 60) else self.set_section_html(html, section)

    # def set_section_html(self, html, section):
    #     section_regex = f"<a href=\"#{section}\">.*?</a>.*?<ul>(.*?)</ul>"
    #     pattern = re.compile(section_regex, re.S)
    #     section_html = re.findall(pattern, html)[0]
    #     obj = {'section': section,
    #                  'html': section_html}
    #     self.add_db_entry('sections', obj)
    #     return section_html

    def set_user_agent(self, value=None):
        if value:
            self.user_agent = value
        else:
            self.user_agent = get_random_user_agent()

    def rotate_user_agent(self):
        self.user_agent = self.set_user_agent()

    def log_error(self, source, pertinent_info, error):
        logging.basicConfig(
            filename=f'logs/{source}.log', level=logging.INFO,
            format='%(asctime)s %(message)s')
        logging.error(f'Error: {error} caused by line: {pertinent_info}')


class AlphaVantageScraper(Scraper):

    def __init__(self, update_interval=None):
        super().__init__(update_interval=update_interval)

        self.documentation_url = 'https://www.alphavantage.co/documentation/'
        self.html = None

    def get_section_html(self, html, section):
        section_regex = f"<a href=\"#{section}\">.*?</a>.*?<ul>(.*?)</ul>"
        pattern = re.compile(section_regex, re.S)
        section_html = re.findall(pattern, html)[0]
        return section_html

    # @_db_lookup
    def get_tech_indicator_params(self, tech_ind):
        '''
        Returns required and optional fields for passing in a search in form:
            {'required': {<field>: <field_description>, ...},
             'optional': {<field>: <field_description>, ...}
             }
        '''
        tech_ind = tech_ind.lower()

        self.html = self.get_html_source(
            selection_filter={'url': self.documentation_url})

        # response = self.make_request(self.documentation_url)
        # html = response.content.decode('utf-8')
        section_regex = f"<h4 id=\"{tech_ind.replace('_', '')}\">(.*?)Required: <code>apikey"
        pattern = re.compile(section_regex, re.S)
        section = re.findall(pattern, self.html)[0]

        description = re.findall(
            re.compile("<br>.*?<p>(.*?)</p>.*?<br>", re.S),
            section)[0]
        required = re.findall(
            re.compile("Required: ?<code>(.*?)</code>", re.S),
            section)
        optional = re.findall(
            re.compile("Optional: ?<code>(.*?)</code>", re.S),
            section)

        # required descs are the descriptions tied to the required parameters
        required_descs = [
            re.findall(
                re.compile(
                    f"<code>{var}</code></b></p>.*?<p>(.*?)</p>", re.S),
                section)[0].replace('<code>', '').replace('</code>', '')
            for var in required]
        optional_descs = [
            re.findall(
                re.compile(f"<code>{var}</code></p>.*?<p>(.*?)</p>", re.S),
                section)[0].replace('<code>', '').replace('</code>', '')
            for var in optional]

        requirements = zip(required, required_descs)
        options = zip(optional, optional_descs)

        return {
            'description': description,
            'required': dict(requirements),
            'optional': dict(options)
        }

    def get_tech_indicator_params_db(self, tech_ind):
        try:
            return self.db['tech_ind'].find({'name': tech_ind}).next()
        except:
            return None

    def get_high_usage(self, type_="tech_ind", section=''):
        '''
        Pass in a type ("technical-indicators", "time-series-data", "fx" (forex), "digital-currency" (Crypto), "sector-information") \
        to get which indicators are currently being highly used
        '''
        self.get_option_names(type_)[0]

    def get_non_high_usage(self, type="technical-indicators"):
        '''
        Opposite of self.get_high_usage
        '''
        return self.get_option_names(type_)[1]

    def update_db_html(self, page_url):
        pass

    def get_option_names(self, type_="technical-indicators"):
        '''
        type_ options are ("technical-indicators", "time-series-data", "fx" (forex), "digital-currency" (Crypto), "sector-information")

        returns 2 lists: high usage options and low(er) usage options
        '''
        html = self.get_html_source(
            selection_filter={'url': self.documentation_url})

        section = self.get_section_html(html, type_)

        # print(html)
        # print(section)
        options = re.findall(
            re.compile("<li><a href=.*?>([A-Za-z0-9_]+).+?</li>", re.S),
            section)
        high_usage_options = []
        for option in options:
            if len(
                re.findall(
                    re.compile(
                        f"{option} <span.*?(High Usage).*?</li>", re.S),
                    section)) > 0:
                high_usage_options.append(option)

        non_high_usage_options = [
            option for option in options if option not in high_usage_options]

        return high_usage_options, non_high_usage_options

    def get_tech_indicators_json(self):

        output = {}

        high_usage, low_usage = self.get_option_names()

        for tech_ind in high_usage:
            output[tech_ind] = self.get_tech_indicator_params(tech_ind)
            output[tech_ind]['usage'] = 'high'

        for tech_ind in low_usage:
            output[tech_ind] = self.get_tech_indicator_params(tech_ind)
            output[tech_ind]['usage'] = 'low'

        return output

    def set_tech_indicators_json_file(self):

        data = self.get_tech_indicators_json()

        self.file_operations.write_json(data, 'technical-indicators.json')
