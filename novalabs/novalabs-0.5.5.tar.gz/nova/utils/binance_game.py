import bs4
import requests
import smtplib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Download Binance page
# web_page = requests.get('https://www.binance.com/en/activity/bitcoin-button-game')
# web_page.raise_for_status()  # if error it will stop the program
#
# menu = bs4.BeautifulSoup(web_page.text, 'html.parser')
# print(menu.prettify())

s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.maximize_window()
driver.get('https://www.binance.com/en/activity/bitcoin-button-game')
elements = driver.find_elements(By.CLASS_NAME, 'css-w39bvu')

time = ''
for element in elements:
    time += element.text

print(time)
