import os
from os.path import exists
import datetime
import time
import logging

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import pandas as pd


logging.basicConfig(
    filename="inoc_automator.log",
    format="%(asctime)s %(message)s",
    filemode="w",
    level=logging.INFO,
)

logger = logging.getLogger()


load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# creates chromedriver, logs into footprints, and selects format for report
# returns chromedriver to be used in other functions
def automate():

    c = ChromeOptions()

    # page will open incognito
    c.add_argument("--incognito")

    driver = webdriver.Chrome(options=c)

    # opens login page
    driver.get("https://tts.inoc.com/MRcgi/MRentrancePage.pl")

    # enters username
    driver.find_element_by_name("USER").send_keys(USERNAME)

    # enters password
    driver.find_element_by_name("PASSWORD").send_keys(PASSWORD)

    # clicks submit button
    driver.find_element_by_id("button").click()

    # Report dropdown
    try:

        report_dd = WebDriverWait(driver, 3000).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[4]/div[4]/div/ul[1]/li[3]/div/a")
            )
        )
        myreports = WebDriverWait(driver, 3000).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[4]/div[4]/div/ul[1]/li[3]/ul/li[1]/a")
            )
        )

        # clicks my reports
        ActionChains(driver).move_to_element(report_dd).click(myreports).perform()

    except:
        logger.error(f"Error with selecting drop down")
        print("Error")

    return driver


# generates report based on date
def generate_report(driver, report_date, criteria):
    # select edit
    time.sleep(5)
    driver.find_element_by_xpath(
        '//*[@id="Main"]/table[2]/tbody/tr[2]/td/form/input[2]'
    ).click()
    driver.implicitly_wait(3000)

    # go button
    driver.find_element_by_xpath('//*[@id="submitpvtLink"]').click()
    driver.implicitly_wait(3000)

    # select wrapped
    driver.find_element_by_xpath(
        "/html/body/div[3]/div[5]/form/table[1]/tbody/tr/td/div/table/tbody/tr[2]/td[1]/input"
    ).click()
    driver.implicitly_wait(3000)

    datetm = datetime.datetime.strptime(report_date, "%Y-%m-%d")

    YEAR = datetm.year
    MONTH = datetm.month
    DAY = datetm.day

    # Advanced Criteria tab

    driver.find_element_by_xpath(
        "/html/body/div[3]/div[5]/form/div/table/tbody/tr/td[6]/div"
    ).click()

    driver.implicitly_wait(3000)

    # either clicks created or last edited based upon criteria variable

    window = 0
    if criteria == "created":
        # click created
        driver.find_element_by_xpath('//*[@id="DATERANGEWHAT"]/option[1]').click()
        print('"Created" report to be generated')
        window = 1
    if criteria == "last edited":
        # click last edited
        driver.find_element_by_xpath('//*[@id="DATERANGEWHAT"]/option[2]').click()
        print('"Last edit" report to be generated')
        window = 2
    driver.implicitly_wait(3000)

    # month input
    month = driver.find_element_by_xpath('//*[@id="DATE_S_MonthInput_LOWDATE_S_Month"]')
    month.clear()
    driver.implicitly_wait(3000)
    month.send_keys(MONTH)

    driver.implicitly_wait(3000)

    # day input
    day = driver.find_element_by_xpath('//*[@id="DATE_S_DayInput_LOWDATE_S_Day"]')
    day.clear()
    driver.implicitly_wait(3000)
    day.send_keys(DAY)

    driver.implicitly_wait(3000)

    # year input
    year = driver.find_element_by_xpath('//*[@id="DATE_S_YearInput_LOWDATE_S_Year"]')
    year.clear()
    driver.implicitly_wait(3000)
    year.send_keys(YEAR)

    driver.implicitly_wait(3000)

    # month input
    month = driver.find_element_by_xpath(
        '//*[@id="DATE_S_MonthInput_HIGHDATE_S_Month"]'
    )
    month.clear()
    driver.implicitly_wait(3000)
    month.send_keys(MONTH)

    driver.implicitly_wait(3000)

    # day input
    day = driver.find_element_by_xpath('//*[@id="DATE_S_DayInput_HIGHDATE_S_Day"]')
    day.clear()
    driver.implicitly_wait(3000)
    day.send_keys(DAY)

    driver.implicitly_wait(3000)

    # year input
    year = driver.find_element_by_xpath('//*[@id="DATE_S_YearInput_HIGHDATE_S_Year"]')
    year.clear()
    driver.implicitly_wait(3000)
    year.send_keys(YEAR)

    # save/run
    driver.implicitly_wait(3000)
    driver.find_element_by_xpath(
        "/html/body/div[3]/div[5]/form/div/table/tbody/tr/td[7]/div"
    ).click()

    driver.implicitly_wait(3000)
    # click GO and generate report
    try:

        driver.find_element(
            by=By.XPATH,
            value="/html/body/div[3]/div[5]/form/table[7]/tbody/tr/td/p/table/tbody/tr/td/a/div",
        ).click()
        driver.implicitly_wait(3000)

    except:
        logger.error(f"Error with generating report for {report_date}")
        print("Error")

    # switches to generated report page
    driver.switch_to.window(driver.window_handles[window])

    # allows page to fully load before looking for tables
    time.sleep(90)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.select("table")

    print("Creating tables from report...")
    pd_tables = pd.read_html(str(tables))
    count = 1
    for x in range(1, len(pd_tables), 6):

        pd_tables[x].reset_index(drop=True, inplace=True)
        pd_tables[x].to_csv(f"report{count}.csv", index=False)
        count += 1

    print("Tables created")

    df = pd.DataFrame()
    df["Ticket Number"] = ""
    df["Ticket Type"] = ""
    df["Priority"] = ""
    df["Status"] = ""
    df["Title"] = ""
    df["Submitted By"] = ""
    df["Assignees"] = ""
    df["Last Edit Date"] = " "
    df["Date Submitted"] = ""
    df["Date Closed"] = ""
    df["Description"] = ""
    df["History"] = ""
    df["Ticket Category"] = ""
    df["Date of Alarm"] = ""
    df["Time of Alarm"] = ""
    df["Product"] = ""
    df["Device ID"] = ""
    df["Device Name"] = ""
    df["Device Type"] = ""
    df["Client Internal"] = ""
    df["Client Priority"] = ""
    df["Client Ticket Number"] = ""
    df["Comments"] = ""
    df["Company"] = ""

    dfh = pd.DataFrame()
    dfh["Ticket Number"] = ""
    dfh["Date"] = ""
    dfh["Time"] = ""
    dfh["User"] = ""
    dfh["Action"] = ""

    for x in range(1, count):
        dff = pd.read_csv(f"report{x}.csv")
        row = dff.iloc[0]
        df.loc[len(df.index)] = row

    df.reset_index(drop=True, inplace=True)
    df.to_csv("mainreport.csv", index=False)

    for i in range(1, count):
        dff = pd.read_csv(f"report{i}.csv")
        length = len(dff.index)
        ticketnum = dff.iloc[0, 0]
        for j in range(3, length):
            row = len(dfh.index)
            dfh.at[row, "Ticket Number"] = ticketnum
            dfh.at[row, "Date"] = dff.iloc[j][0]
            dfh.at[row, "Time"] = dff.iloc[j][1]
            dfh.at[row, "User"] = dff.iloc[j][2]
            dfh.at[row, "Action"] = dff.iloc[j][3]

    dfh.reset_index(drop=True, inplace=True)
    dfh.to_csv("mainhistoryreport.csv")

    # switches back to footprint main page
    driver.switch_to.window(driver.window_handles[0])

    return count
