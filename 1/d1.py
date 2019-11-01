# список репозиториев
import requests
req = requests.get('https://api.github.com/users/iumarchenko/repos?type=all&sort=created&direction=desc')
with open('res.json','wb') as file:
     file.write(req.content)

# авторизация
req = requests.get('https://api.github.com/user',
                        auth=requests.auth.HTTPBasicAuth(
                          'iumarchenko',
                          '111111'))
with open('2.res.json','wb') as file:
     file.write(req.content)