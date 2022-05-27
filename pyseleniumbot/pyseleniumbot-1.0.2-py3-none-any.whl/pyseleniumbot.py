from selenium.webdriver.common.by import By
class wrapper:
    def __init__(self,browser):
        self.browser=browser
    def findElementsBy(self,xpath):
        #self.browser.presence_of_all_elements_located(xpath)
        #self.browser.visibility_of_element_located(xpath)
        return self.browser.find_elements(By.XPATH,xpath)
    def findElementBy(self,xpath):
        self.browser.presence_of_element_located(xpath)
        self.browser.visibility_of_element_located(xpath)
        self.browser.find_element(By.XPATH,xpath)
    def click(self,xpath):
        self.browser.visibility_of_element_located(xpath)
        self.browser.element_to_be_clickable(By.XPATH,xpath) 
        self.browser.find_element(By.XPATH,xpath).click()
    def navigateto(self,urlstring):
        self.browser.get(urlstring)
