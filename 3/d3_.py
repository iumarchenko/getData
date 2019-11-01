from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from pymongo import MongoClient

i=0
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 YaBrowser/19.9.0.1343 Yowser/2.5 Safari/537.36'
main_link = ('https://www.superjob.ru')
url = ('https://www.superjob.ru/vacancy/search/?keywords=программист%201C&geo%5Bc%5D%5B0%5D=1')
df = pd.DataFrame({
    'name': [],
    'href': [],
    'compensation_min': [],
    'compensation_max': [],
    'company': [],
    'addr': [],
    'site' : []
})

client = MongoClient('localhost', 27017)
db = client['vacancies_db']
vacancies = db.sj

# Задание 1: реализовать функцию, записывающую собранные вакансии в созданную БД
def ins_mongo_many():
    vacancies.insert_many(df.to_dict('records'))

# Задание 3: Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта
def ins_mongo_one():
    for index, row in df.iterrows():
        if vacancies.count_documents({'href': {'$eq': row['href']}}) == 0:
            vacancies.insert_one(row.to_dict())
            print('INSERTED: {}'.format(row.to_dict()))
        else:
            vac = vacancies.find({'href': {'$eq': row['href']}})
            if vac[0]['name'] != row['name']:
                print('UPDATED record:{} \n from Name "{}" to "{}"'.format(row.to_dict(), vac[0]['name'], row['name']))
                vacancies.update_one({'href':{'$eq': row['href']}},{'$set':{'name':row['name']}})
            if vac[0]['compensation_min'] != row['compensation_min']:
                print('UPDATED record:{} \n from Compensation_min "{}" to "{}"'.format(row.to_dict(), vac[0]['compensation_min'], row['compensation_min']))
                vacancies.update_one({'href': {'$eq': row['href']}}, {'$set': {'compensation_min': row['compensation_min']}})
            if vac[0]['compensation_max'] != row['compensation_max']:
                print('UPDATED record:{} \n from Compensation_max "{}" to "{}"'.format(row.to_dict(), vac[0]['compensation_max'], row['compensation_max']))
                vacancies.update_one({'href': {'$eq': row['href']}}, {'$set': {'compensation_max': row['compensation_max']}})
            if vac[0]['company'] != row['company']:
                print('UPDATED record:{} \n from Company "{}" to "{}"'.format(row.to_dict(), vac[0]['company'], row['company']))
                vacancies.update_one({'href': {'$eq': row['href']}}, {'$set': {'company': row['company']}})
            if vac[0]['addr'] != row['addr']:
                print('UPDATED record:{} \n from Addr "{}" to "{}"'.format(row.to_dict(), vac[0]['addr'], row['addr']))
                vacancies.update_one({'href': {'$eq': row['href']}}, {'$set': {'addr': row['addr']}})

# Задание 2: Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы
def find_gt_comp():
    while True:
        sal = input("Введите интересующий уровень зп (или 0 для выхода):")
        try:
            sal = int(sal)
        except ValueError:
            print("попробуйте ввести еще раз")
            continue
        if (sal == 0): break
        objects = vacancies.find({'compensation_min': {'$gt': sal}},
                                 {'name', 'compensation_min', 'compensation_max', 'company'})
        for obj in objects:
            print(obj)

def req_sj(url):
    html = requests.get(url, headers={'User-Agent': USER_AGENT}).text
    return bs(html, 'lxml')

def create_vacancy(vacancy):
    vacancy_ = vacancy.find(lambda tag: tag.name == 'div' and not tag.attrs).contents[1].contents
    vacancy_info = vacancy_[0].getText()
    vacancy_href = main_link + vacancy_[0].find('a')['href']
    vacancy_employer = vacancy_[1].contents[0].contents[0].getText()
    vacancy_addr = vacancy_[1].contents[0].contents[1].getText().split(" • ")[1]
    vacancy_comp = vacancy_[2].getText().replace("\xa0", "").replace('₽', '')
    if vacancy_comp != '':
        if vacancy_comp.find('от') != -1:
            comp = [int(vacancy_comp.replace('от', '')), 0]
        elif vacancy_comp.find('—') != -1:
            comp = [int(vacancy_comp.split('—')[0]), int(vacancy_comp.split('—')[1])]
        elif vacancy_comp.find('По договорённости') != -1:
            comp = [0, 0]
        else:
            comp = [int(vacancy_comp), int(vacancy_comp)]
    else:
        comp = [0, 0]
    return [vacancy_info, vacancy_href, comp[0], comp[1], vacancy_employer, vacancy_addr, main_link]

while True:
     parsed_html = req_sj(url)
     vacancy_list = parsed_html.find_all('div', {'class': 'f-test-vacancy-item'})
     for vacancy in vacancy_list:
          df.loc[i] = create_vacancy(vacancy)
          i += 1
     try:
          next_page = parsed_html.find('a', attrs={'class': 'f-test-link-dalshe'}).get('href')
          url = main_link + next_page
     except AttributeError:
          break

df.to_excel('sj3.xlsx')

# ins_mongo_many()
ins_mongo_one()
find_gt_comp()