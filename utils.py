from bs4 import BeautifulSoup
import requests
from data import constant
import logging
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import time
from data.constant import Months
from retrying import retry


def get_source_soup(url, timeout=3):
    driver = webdriver.PhantomJS(executable_path='phantomjs-1.9.7-windows\phantomjs.exe')
    driver.get(url)
    try:
        loadmore = driver.find_element_by_class_name("button hollow expanded-mobile js-load-more-results")
        actions = ActionChains(driver)
        actions.move_to_element(loadmore)
        actions.click(loadmore)
        actions.perform()
        time.sleep(2)
        driver.quit()
    except Exception as e:
        logging.exception(e)


@retry(stop_max_attempt_number=3)
def get_fresh_soup(url, timeout=5):
    try:
        cafile = constant.cafile
        html = requests.get(url, verify=cafile, headers=constant.headers, timeout=5)
        # if html.status_code != 200:
        #     return None
        # else:
        html.encoding='utf-8'
        logging.info('crawl succeed')
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup
    except Exception as e:
        logging.exception(e)


def time_formatter(t):
    t = t.split()
    month = Months[t[0].split()]
    date = t[1].strip(',').strip()
    date = '0'+date if len(date) == 1 else date
    return t[2].strip()+month+date


if __name__ == '__main__':
    soup = get_fresh_soup('https://www.gofundme.com/f/hna-jogathon-20212022')
    print(soup.prettify())