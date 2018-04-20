from selenium import webdriver
import os.path
import yaml

COOKIES_PATH = 'cookies.yaml'


def get_cookies(force=False):
    if os.path.exists(COOKIES_PATH) and not force:
        return yaml.load(open(COOKIES_PATH))

    driver = webdriver.Chrome()
    driver.get("http://www.facebook.com")

    # wait for the user to enter in their password
    while True:
        try:
            driver.find_element_by_class_name("innerWrap")
            break
        except:
            continue

    # get the cookies and quit
    cookies = driver.get_cookies()
    driver.quit()

    # desired format for requests library
    formatted = {}
    for cook in cookies:
        formatted[cook['name']] = cook['value']

    yaml.safe_dump(formatted, open(COOKIES_PATH, 'w'))
    return formatted
