import logging

from info_extractor import IndividualPageInfoExtractor
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import time
import json
import sys
import socket

class Monitor(object):
    def __init__(self, url):
        self.url = url
        self.page_hrefs = []
        with open('data/page_href.txt', 'r', encoding='utf=8') as f:
            for line in f:
                self.page_hrefs.append(line.strip())


    def run(self):
        try:
            start_time = time.time()

            """Extract urls from home page"""
            driver = webdriver.PhantomJS(executable_path='phantomjs-1.9.7-windows/phantomjs.exe', service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
            driver.get(self.url)
            time.sleep(2)
            seemore = driver.find_element_by_xpath("//a[@data-gfm-analytics-element='btn_charitylandingpage_seemoretrending']")
            action = ActionChains(driver)
            action.move_to_element(seemore)
            action.click(seemore)
            action.perform()
            time.sleep(3)
            counting = 500
            for i in range(counting):
                print('click ', i, ' times')
                loadmore = driver.find_element_by_xpath("//a[@data-gfm-analytics-element='btn_showmore_browse']")
                action = ActionChains(driver)
                action.move_to_element(loadmore)
                action.click(loadmore)
                action.perform()
                time.sleep(3)
                hrefs = driver.find_elements_by_xpath("//a[@class='fund_tile_card_link']")
                for link in hrefs:
                    fund_url = link.get_attribute('href')
                    if fund_url not in self.page_hrefs:
                        # extractor = IndividualPageInfoExtractor(fund_url)
                        with open('data/page_href.txt', 'a', encoding='utf-8') as f:
                            f.write(fund_url)
                            f.write('\n')

                    self.page_hrefs.append(fund_url)

            driver.quit()
            end_time = time.time()
            print('time cost for collecting url', end_time-start_time, 's')
        except Exception as e:
            logging.exception(e)

    def extract(self):
        """Extract info from individual campaign"""
        try:
            # s = socket.socket()
            socket.setdefaulttimeout(3)  # timeout 3
            start_time = time.time()
            count = 0

            with open('data/page_href.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.replace('\n', '')
                    count += 1
                    print('extracting ', count, " : ", line)

                    extractor = IndividualPageInfoExtractor(line)
                    info_dict = extractor.extractor()
                    with open('data/CampaignDataSet.txt', 'a', encoding='utf-8') as w:
                        w.write(json.dumps(info_dict, indent=4, separators=(',', ':')))
                        w.write('\n')

            end_time = time.time()
            print('time cost for extracting url', end_time-start_time, 's')
        except Exception as e:
            logging.exception(e)


if __name__ == '__main__':
    try:
        url = 'https://www.gofundme.com/start/charity-fundraising'  # homepage
        monitor = Monitor(url)
        monitor.run()
        monitor.extract()
        time.sleep(1)
    except Exception as e:
        logging.exception(e)
