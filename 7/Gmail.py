from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['mail']
gmail = db.gmail

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome()
driver.get('https://mail.google.com/mail/u/0/#inbox')

email = driver.find_element_by_name('identifier')
email.send_keys('inessa.vtsft@gmail.com')
email.send_keys(Keys.RETURN)
time.sleep(2)

paswd = driver.find_element_by_name('password')
paswd.send_keys('VDhebvsy6')
paswd.send_keys(Keys.RETURN)

time.sleep(3)
mail = driver.find_element_by_xpath("//table[@role='grid'][last()]//tr")
mail.click()
while True:
    time.sleep(2)
    from_mail = driver.find_element_by_xpath("//span[@class='qu']").text
    date_mail = driver.find_element_by_xpath("//div[@class='gK']").text
    theme_mail = driver.find_element_by_xpath("//h2[@class='hP']").text
    text_mail = driver.find_element_by_xpath("//div[@class='']").text
    gmail.insert_one({'from':from_mail,'date':date_mail,'theme':theme_mail,'text':text_mail})
    next_btn = driver.find_element_by_xpath("//div[@class='h0']/div[last()]")
    if next_btn.get_attribute("aria-disabled") != 'true':
         next_btn.click()
    else:
         break
driver.quit()
