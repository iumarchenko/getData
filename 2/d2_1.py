from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

i=0
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 YaBrowser/19.9.0.1343 Yowser/2.5 Safari/537.36'
main_link = ('https://www.superjob.ru')
url = ('https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bc%5D%5B0%5D=1')
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
     html = requests.get(url, headers={'User-Agent': USER_AGENT}).text
     parsed_html = bs(html, 'lxml')
     vacancy_list = parsed_html.find_all('div', {'class': 'f-test-vacancy-item'})
     for vacancy in vacancy_list:
          vacancy_ = vacancy.find(lambda tag: tag.name == 'div' and not tag.attrs).contents[1].contents
          vacancy_info = vacancy_[0].getText()
          vacancy_href = main_link+vacancy_[0].find('a')['href']
          vacancy_employer = vacancy_[1].contents[0].contents[0].getText()
          vacancy_addr = vacancy_[1].contents[0].contents[1].getText().split(" • ")[1]
          vacancy_comp = vacancy_[2].getText().replace("\xa0", " ")
          if vacancy_comp != '':
               if vacancy_comp.find('от') != -1:
                    comp = [vacancy_comp.split(' ')[1], '']
               elif vacancy_comp.find('—') != -1:
                    comp = [vacancy_comp.split('—')[0], vacancy_comp.split('—')[1]]
               elif vacancy_comp.find('По договорённости') != -1:
                    comp = ['', '']
               else:
                    comp =  [vacancy_comp, vacancy_comp]
          else:
               comp = ['', '']
          df.loc[i] = [vacancy_info, vacancy_href, comp[0], comp[1], vacancy_employer, vacancy_addr, main_link]
          i += 1

     try:
          next_page = parsed_html.find('a', attrs={'class': 'f-test-link-dalshe'}).get('href')
          url = main_link + next_page

     except AttributeError:
          break

df.to_excel('sj.xlsx')

