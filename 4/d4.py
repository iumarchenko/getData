from datetime import datetime
from pprint import pprint
from lxml import html
import requests
import pandas as pd

main_link_1 = ('https://mail.ru/')
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}

req = requests.get(main_link_1, headers=headers)
root = html.fromstring(req.text)

names_1 = root.xpath('//h3[@class="news-item__title i-link-deco"]/text() | '
    '//div[@class="news-item__inner"]/a[last()]/text()')
hrefs_1 = root.xpath('//h3[@class="news-item__title i-link-deco"]/ancestor::a/@href | '
    '//div[@class="news-item__inner"]/a[last()]/@href')


main_link_2 = ('https://lenta.ru')
req = requests.get(main_link_2, headers=headers)
root = html.fromstring(req.text)
names_2 = root.xpath('//h2/a/text() | '
    '//div[contains(@class,"span8")]//div[@class="item"]/a/text()')
hrefs_2 =  list(map(lambda x: main_link_2 + x, root.xpath('//h2/a/@href | '
    '//div[contains(@class,"span8")]//div[@class="item"]/a/@href')))

df = pd.DataFrame({
    'name': list(map(lambda x: x.replace(u'\xa0', u' '), names_1+names_2)),
    'href': hrefs_1+hrefs_2,
    'source': [main_link_1 for i in range(len(names_1))]+[main_link_2 for i in range(len(names_2))],
    'date': [datetime.now().strftime("%d-%m-%Y") for i in range(len(names_1+names_2))]
})

df.to_excel('news.xlsx')