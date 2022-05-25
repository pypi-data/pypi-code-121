from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from server.tasks import run_code
from server.utils import build_structure

import subprocess
import pandas as pd
from pyvirtualdisplay import Display
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from lxml import etree
import lxml.html
import time
from urllib.parse import urljoin


def get_cleaned_html(html, url):
    '''
    Given a string of html and a URL that served the html, return a new string with the cleaned html.

    All tags irrelevant to scraping or displaying snapshots is removed
    All links are made absolute using the given URL
    All elements have node IDs added as data attributes
    '''
    parser = lxml.html.HTMLParser(remove_comments=True, remove_pis=True)
    root = lxml.html.fromstring(html, parser=parser)
    etree.strip_elements(root, 'script', with_tail=False)
    etree.strip_elements(root, 'noscript', with_tail=False)
    root.make_links_absolute(url)
    for elem in root.xpath('//img[@srcset]'):
        srcset_list = []
        for s in elem.get('srcset').split(','):
            parts = s.strip().split()
            if not parts:
                continue
            parts[0] = urljoin(url, parts[0])
            srcset_list.append(' '.join(parts))
        elem.set('srcset', ', '.join(srcset_list))
    for index, elem in enumerate(root.xpath('//*')):
        elem.set('data-psgn-id', str(index))
        elem.attrib.pop('data-psgn-pg', None)
    return lxml.html.tostring(root)


@api_view(['GET'])
def ping(request):
    return Response('pong')


@api_view(['POST'])
def update(request):
    subprocess.run(["/home/ubuntu/parsagon/parsagon-local-server/bin/parsagon-server-update"])
    return Response('OK')


@api_view(['POST'])
def read_db(request):
    db_type = request.data['db_type']
    db_name = request.data['db_name']
    user = request.data['db_user']
    password = request.data['db_password']
    host = request.data['db_host']
    port = request.data['db_port']
    table = request.data['table']
    schema = request.data['schema']

    con = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'

    df_iter = pd.read_sql_table(table, con=con, schema=schema, chunksize=100)
    df = next(df_iter)
    result = df.to_dict(orient='records')

    return Response(result)


@api_view(['POST'])
def write_db(request):
    db_type = request.data['db_type']
    db_name = request.data['db_name']
    user = request.data['db_user']
    password = request.data['db_password']
    host = request.data['db_host']
    port = request.data['db_port']
    table = request.data['table']
    schema = request.data['schema']

    con = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'

    return Response('OK')


@api_view(['POST'])
def fetch_web(request):
    url = request.data['url']
    chrome_version = subprocess.run(['google-chrome', '--version'], check=True, stdout=subprocess.PIPE).stdout
    chrome_version = int(chrome_version.decode('utf-8').split()[2].split('.')[0])
    chrome_options = uc.ChromeOptions()
    chrome_prefs = {}
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    chrome_options.add_experimental_option('prefs', chrome_prefs)
    if settings.PROXY:
        chrome_options.add_argument(f'--proxy-server={settings.PROXY}')
        chrome_options.add_argument('--ignore-certificate-errors')
    display = Display(visible=False, size=(1680, 1050)).start()
    driver = uc.Chrome(version_main=chrome_version, options=chrome_options)
    driver.maximize_window()
    driver.get(url)
    time.sleep(1)
    page_source = driver.page_source
    url = driver.current_url
    driver.quit()
    display.stop()
    return Response({'url': url, 'html': get_cleaned_html(page_source, url)})


@api_view(['POST'])
def fetch_web_action(request):
    code = request.data['code']
    elem_var_name = request.data['variable']
    action = request.data['action']
    args = request.data['args']

    loc = dict(locals(), **globals())
    try:
        exec(code, loc, loc)

        driver = loc['driver']
        elem = loc['parsagon_variables'][elem_var_name]
        if isinstance(elem, lxml.html.HtmlElement):
            elem_id = elem.get('data-psgn-id')
            elem = driver.find_element_by_xpath(f'//*[@data-psgn-id="{elem_id}"]')

        page = driver.current_window_handle
        page_source = driver.page_source
        old_url = driver.current_url
        old_html = get_cleaned_html(page_source, old_url)

        if action == 'CLICK_HTMLELEM':
            elem.click()
        elif action == 'SELECT_HTMLELEM':
            select_obj = Select(elem)
            if args['outputWebActionOptionType'] == 'INDEX':
                select_obj.select_by_index(int(args['outputWebActionOption']))
            else:
                select_obj.select_by_visible_text(args['outputWebActionOption'])
        elif action == 'FILL_HTMLELEM':
            elem.clear()
            elem.send_keys(args['outputWebActionInput'])
            end_key = args['outputWebActionEndKey']
            if end_key == 'RETURN':
                elem.send_keys(Keys.RETURN)
        elif action == 'SCROLL_PAGE':
            driver.execute_script(f"window.scrollTo({{top: document.documentElement.scrollHeight * {args['outputWebActionY']}, left: document.documentElement.scrollWidth * {args['outputWebActionX']}, behavior: 'smooth'}})")
            time.sleep(0.5)
        elif action == 'WAIT_PAGE':
            time.sleep(float(args['outputWebActionSeconds']))

        driver.switch_to.window(page)
        page_source = driver.page_source
        new_url = driver.current_url
        new_html = get_cleaned_html(page_source, new_url)
    finally:
        if 'driver' in loc:
            loc['driver'].quit()
        if 'display' in loc:
            loc['display'].stop()
    return Response({'old_page': {'url': old_url, 'html': old_html}, 'new_page': {'url': new_url, 'html': new_html}})


@api_view(['POST'])
def run_pipeline(request):
    run_code.delay(request.data['pipeline_id'], request.data['run_id'])
    return Response('OK')
