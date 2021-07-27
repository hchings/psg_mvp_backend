from seleniumwire import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import typer
import time

CHROME_DRIVER_PATH = "./chromedriver"


def defining_driver():
    """
    Please change the webdriver path to your corresponding one

    :return:
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('window-size=1536x824')
    wire_options = {
        'connection_timeout': 1000
    }
    driver = webdriver.Chrome("./chromedriver", seleniumwire_options=wire_options, options=options)
    return driver

def tmp():
    print("in tmp")
    browser = defining_driver()

    browser.get('http://www.facebook.com')
    assert 'Facebook' in browser.title

    elem = browser.find_element(By.ID, 'email')  # Find the search box
    elem.send_keys('cjoun@vt.edu') #+ Keys.RETURN)

    elem = browser.find_element(By.ID, 'pass')  # Find the search box
    elem.send_keys('djchristianjoun1616' + Keys.RETURN)

    print(browser.title)
    time.sleep(2)
    print(browser.title)
    #WebDriverWait(browser, 10).until(EC.title_contains("7"))

    assert 'Facebook - Log In or Sign Up' not in browser.title

    browser.quit()

def auth():
    url = "https://www.facebook.com/charm3c/reviews/?ref=page_internal"
    print("trying to authenticate")

    driver = defining_driver()
    driver.get(url)
    clicked=False

if __name__ == "__main__":
    typer.run(tmp)