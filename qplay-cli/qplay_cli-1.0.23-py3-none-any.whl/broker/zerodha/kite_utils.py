import time
import traceback

from retrying import retry
import getpass
from qplay_cli.utils.selenium_utils import Selenium

class KiteUtils():

    @staticmethod
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def get_request_token(kite_api_key=None):
        try:
            browser = Selenium.get_browser()

            #TODO api should be fetched from configuration

            kite_url = "https://kite.trade/connect/login?api_key={}&v=3".format(kite_api_key)
            print("Kite Url {}".format(kite_url))
            browser.get(kite_url)
            time.sleep(5)

            username = browser.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[1]/input')
            password = browser.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[2]/input')

            print("Enter zerodha username:")
            username_value = input()
            
            print("Enter zerodha password:")
            password_value = getpass.getpass()
            
            username.send_keys(username_value)
            password.send_keys(password_value)
            login_attempt = browser.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[4]/button')
            login_attempt.submit()
            time.sleep(5)


            kite_pin = browser.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/div/input')

            print("Enter TOTP:")
            totp = input()
            kite_pin.send_keys(totp)
            time.sleep(3)


            login_attempt = browser.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[3]/button')
            login_attempt.submit()
            time.sleep(5)

            url = browser.current_url
            print("got kite url {}".format(url))
            request_token = url.split('token=')[1].split('&')[0]

            browser.close()

            return request_token
        except:
            print(traceback.print_exc())
            raise

if __name__ == '__main__':
    k = KiteUtils()
    k.get_request_token()
