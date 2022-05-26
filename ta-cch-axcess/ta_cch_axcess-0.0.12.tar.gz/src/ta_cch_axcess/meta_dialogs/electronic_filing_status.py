from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ElectronicFilingStatus:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        driver = webdriver.Chrome(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe", options=chrome_options
        )
        driver.get("google.com")


if __name__ == "__main__":
    e = ElectronicFilingStatus()
