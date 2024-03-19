import requests

url = 'https://www.wildberries.ru/catalog/178927230/detail.aspx'

rqs = requests.get(url)
print(rqs.content)