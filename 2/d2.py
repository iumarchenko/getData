from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import time
import pandas as pd

a = 0
i=0
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
main_link = ('https://hh.ru')
df = pd.DataFrame({
    'name': [],
    'href': [],
    'compensation_min': [],
    'compensation_max': [],
    'company': [],
    'addr': [],
    'site' : []
})

while True:
    html = requests.get(
        main_link + '/search/vacancy?st=searchVacancy&text=Data+analyst&area=1&experience=doesNotMatter&order_by=publication_time&items_on_page=100&no_magic=true&page=' + str(a),
        headers=headers).text
    parsed_html = bs(html, 'lxml')

    vacancy_list = parsed_html.find_all('div', {'class': 'vacancy-serp-item'})
    for vacancy in vacancy_list:
        vacancy_info = vacancy.find('a' , {'class': 'bloko-link HH-LinkModifier'})
        vacancy_comp = vacancy.find('div', {'class': 'vacancy-serp-item__compensation'})
        if vacancy_comp!= None:
            vacancy_comp = vacancy_comp.string.replace(' руб.','')
            if vacancy_comp.find('от') != -1:
                comp = [vacancy_comp.split(' ')[1],'']
            elif vacancy_comp.find('до ') != -1:
                comp = ['',vacancy_comp.split(' ')[1]]
            else:
                comp = [vacancy_comp.split('-')[0],vacancy_comp.split('-')[1]]
        else:
            comp = comp = ['','']
        vacancy_employer = vacancy.find('a' , {'class': 'bloko-link bloko-link_secondary HH-AnonymousIndexAnalytics-Recommended-Company'})
        if vacancy_employer != None:
            empl = vacancy_employer.string
        else:
            vacancy_employer = vacancy.find('div', {
                'class': 'vacancy-serp-item__meta-info'})
            empl = vacancy_employer.getText()
        vacancy_addr =  vacancy.find('span' , {'class': 'vacancy-serp-item__meta-info'})
        df.loc[i] = [vacancy_info.string, vacancy_info['href'], comp[0], comp[1], empl, vacancy_addr.getText(), main_link]
        i+=1

    has_next = parsed_html.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
    if has_next == None: break
    a += 1
    time.sleep(1)

df.to_excel('hh.xlsx')