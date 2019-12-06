from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['mvideo']
hits = db.hits

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru/')

while True:
    time.sleep(1)
    next_btn = driver.find_element_by_xpath("//body[@class='home']/div[@class='wrapper']/div[@class='page-content']/div[@class='main-holder sel-main-holder']/div[5]/div[1]/div[2]//a[contains(@class,'sel-hits-button-next')]")
    if next_btn.get_attribute("class").find("disabled") != -1:
        break
    else:
        next_btn.click()

products = driver.find_elements_by_xpath("//a[@class='sel-product-tile-title']")
products_price = driver.find_elements_by_xpath("//div[@class='c-pdp-price__current']")

for i in range(0, len(products)):
    print(products[i].get_attribute('title'))
    print(products[i].get_attribute('href'))
    print(products_price[i].text)
    hits.insert_one({'title':products[i].get_attribute('title'),'href': products[i].get_attribute('href'),'text':products_price[i].text})