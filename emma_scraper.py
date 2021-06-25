import requests
from bs4 import BeautifulSoup
import pprint
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import time, sys

def getTime():
    return time.time()


def getTimeElapsed(t1, t0):
    return t1 - t0


class ScrapeEmma():

    def __init__(self, searchDates, cusip, timeout=60):
        self.base_url = 'https://emma.msrb.org/TradeData/Search'
        self.search_url = 'http://emma.msrb.org/Search/Search.aspx?hlt=search'
        self.headers = headers = {
            'User-Agent':'Mozilla/5.0 (Windows; Intel Mac OS X 10_6_8) AppleWebKit/537.4' +
            ' (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.4'
        }
        self.searchDates = searchDates
        self.cusip = cusip
        self.timeout = timeout
        self.data = []
        self.driver = None
        
    def accessEmma(self):
        session = requests.Session()
        r = session.get(self.search_url, headers=self.headers)

        soup = BeautifulSoup(r.content)
        tbl = soup.findAll('table', {'id': 'ctl00_mainContentArea_SearchResultsControl1_searchResultsGridView'})

        ua=UserAgent()
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (ua.random)
        service_args=['--ssl-protocol=any','--ignore-ssl-errors=true']
        return webdriver.Chrome('C:\\Users\\denni\\Downloads\\chromedriver_win32 (1)\\chromedriver.exe', service_args=service_args)

    def runDriver(self, driver):
        self.driver = driver
        self.driver.get(self.base_url)

        but1 = self.driver.find_element_by_id('ctl00_mainContentArea_disclaimerContent_yesButton')
        but1.click()

        tradeDateFrom = self.driver.find_element_by_id('tradeDateFrom')
        tradeDateFrom.clear()
        tradeDateFrom.send_keys(self.searchDates[0])

        tradeDateTo = self.driver.find_element_by_id('tradeDateTo')
        tradeDateTo.clear()
        tradeDateTo.send_keys(self.searchDates[1])

        getCusipFrom = self.driver.find_element_by_id("cusip")
        getCusipFrom.clear()
        getCusipFrom.send_keys(self.cusip) 

        runSearch = self.driver.find_element_by_id('searchButton')
        runSearch.click()

        time.sleep(2)

        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(
                                                             (By.ID, 'lvSearchResults')))

    def scrapeDateFromTable(self, table):
        while True:
            pprint.pprint(self.driver)
            nextPage = WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(
                                                                    (By.ID, 'lvSearchResults_next')))

            rows = table.find_elements_by_tag_name('tr')
            for tr in rows:
                tds = tr.find_elements_by_tag_name('td')
                if tds:
                    row_data = []
                    idx = 0
                    for td in tds:
                        if idx == 1 :
                            row_data.append(self.cusip)
                            idx += 1
                        else:
                            row_data.append(td.text)
                            idx += 1
                    if(row_data[0] != ''):
                        self.data.append(row_data)
            if 'disabled' in nextPage.get_attribute('class'):
                break
            nextPage.click()
            time.sleep(3)

    def buildStatment(self):
        statement = {}
        for d in self.data:
            trade_type = d[9]
            if trade_type == "Customer bought":
                purchase_date = d[0].split()[0]
                cusip = d[1]
                security_desc = d[2]
                coupon_rate = d[3]
                maturity_date = d[4]
                price_prct = d[5]
                yield_prct = d[6]
                circ_day_price = d[7]
                trade_amount = int("".join(d[8].split(",")))
                statement = {"Cusip": cusip,
                             "Purchase Date": purchase_date,
                             "Security Description": security_desc,
                             "Coupon Rate": float(coupon_rate),
                             "Maturity Date": maturity_date,
                             "Price Percent": float(price_prct),
                             "Yield Percent": yield_prct,
                             "Circulation Day and Price": circ_day_price,
                             "Trade Amount": float(trade_amount),
                             "Trade Type": trade_type}
        self.driver.close()
        return statement
