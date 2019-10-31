from bs4 import BeautifulSoup as bs
import requests
from pymongo import MongoClient
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

client = MongoClient('localhost', 27017)
db = client['vacancies_db']
vacancies = db.hh

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
        except TypeError:
            print("попробуйте ввести еще раз")
            continue
        if (sal == 0): break
        objects = vacancies.find({'compensation_min': {'$gt': sal}},
                                 {'name', 'compensation_min', 'compensation_max', 'company'})
        for obj in objects:
            print(obj)


def req_hh(a):
    html = requests.get(
        main_link + '/search/vacancy?st=searchVacancy&text=Data+analyst&area=1&experience=doesNotMatter&order_by=publication_time&items_on_page=100&no_magic=true&page=' + str(a),
        headers=headers).text
    return bs(html, 'lxml')




def create_vacancy(vacancy):
    vacancy_info = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'})
    vacancy_comp = vacancy.find('div', {'class': 'vacancy-serp-item__compensation'})
    if vacancy_comp != None:
        vacancy_comp = vacancy_comp.string.replace(' руб.', '').replace(' USD', '').replace("\xa0", "")
        if vacancy_comp.find('от') != -1:
            comp = [int(vacancy_comp.split(' ')[1]), 0]
        elif vacancy_comp.find('до ') != -1:
            comp = [0, int(vacancy_comp.split(' ')[1])]
        else:
            comp = [int(vacancy_comp.split('-')[0]), int(vacancy_comp.split('-')[1])]
    else:
        comp = comp = [0, 0]
    vacancy_employer = vacancy.find('a', {
        'class': 'bloko-link bloko-link_secondary HH-AnonymousIndexAnalytics-Recommended-Company'})
    if vacancy_employer != None:
        empl = vacancy_employer.string
    else:
        vacancy_employer = vacancy.find('div', {
            'class': 'vacancy-serp-item__meta-info'})
        empl = vacancy_employer.getText()
    vacancy_addr = vacancy.find('span', {'class': 'vacancy-serp-item__meta-info'})
    return [vacancy_info.string, vacancy_info['href'], comp[0], comp[1], empl, vacancy_addr.getText(), main_link]

while True:
    parsed_html = req_hh(a)
    vacancy_list = parsed_html.find_all('div', {'class': 'vacancy-serp-item'})
    for vacancy in vacancy_list:
        df.loc[i] = create_vacancy(vacancy)
        i+=1
    has_next = parsed_html.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
    if has_next == None: break
    a += 1
    time.sleep(1)

df.to_excel('hh3.xlsx')
# ins_mongo_many()
ins_mongo_one()
find_gt_comp()

