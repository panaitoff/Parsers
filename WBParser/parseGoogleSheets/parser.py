import datetime
import time

import gspread
import requests

url_sheets = input('Ссылка на таблицу: ')
list_name = input('Название листа в котором будет работа')
try:
    sa = gspread.service_account('service_account.json')
    sh = sa.open_by_url(url_sheets)
    # sh = sa.open('parse_copy')

    wks = sh.worksheet(list_name)
except:
    input('Возникла ошибка с вводом данных')
wks.format(['A:A', 'H:H'], {"numberFormat": {"type": "Text"}})
art_data_1 = wks.col_values(1)[2:]
art_data_2 = wks.col_values(8)[2:]

art_data = []

if len(art_data_1) > len(art_data_2):
    OnSmallerArray = [list(i) for i in zip(art_data_1, art_data_2)]
    pacifiers = ['' for i in range(len(art_data_1[len(OnSmallerArray):len(art_data_1)]))]
    MissingElem = art_data_1[len(OnSmallerArray):len(art_data_1)]
    CombinedArray = [list(i) for i in zip(MissingElem, pacifiers)]
    art_data = OnSmallerArray + CombinedArray
elif len(art_data_1) < len(art_data_2):
    OnSmallerArray = [list(i) for i in zip(art_data_1, art_data_2)]
    pacifiers = ['' for i in range(len(art_data_2[len(OnSmallerArray):len(art_data_2)]))]
    MissingElem = art_data_2[len(OnSmallerArray):len(art_data_2)]
    CombinedArray = [list(i) for i in zip(pacifiers, MissingElem)]
    art_data = OnSmallerArray + CombinedArray
else:
    art_data = [list(i) for i in zip(art_data_1, art_data_2)]

input('Для продолжения нажмите Enter')
try:
    for num, i in enumerate(art_data):

        data_res_1 = ['', '', '', '', '', '']
        data_res_2 = ['', '', '', '', '', '']

        if i[0] != '':
            try:
                url1 = f'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1400000&regions=80,38,83,4,64,33,68,' \
                      f'70,30,40,86,69,1,31,66,48,22,114&spp=33&nm={i[0]}'

                rqs = requests.get(url1)

                data = rqs.json()
                data_res_1 = [
                    data['data']['products'][0]['supplierId'],
                    data['data']['products'][0]['extended']['basicSale'],
                    data['data']['products'][0]['extended']['basicPriceU'] / 100,
                    data['data']['products'][0]['extended']['clientSale'],
                    data['data']['products'][0]['extended']['clientPriceU'] / 100
                ]
            except IndexError:
                data_res_1 = [
                    i[0],
                    'Не существует',
                    '', '', ''
                ]

        if i[1] != '':
            try:
                url2 = f'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1400000&regions=80,38,83,4,64,33,68,' \
                       f'70,30,40,86,69,1,31,66,48,22,114&spp=33&nm={i[1]}'
                rqs = requests.get(url2)

                data = rqs.json()
                data_res_2 = [
                    data['data']['products'][0]['supplierId'],
                    data['data']['products'][0]['extended']['basicSale'],
                    data['data']['products'][0]['extended']['basicPriceU'] / 100,
                    data['data']['products'][0]['extended']['clientSale'],
                    data['data']['products'][0]['extended']['clientPriceU'] / 100
                ]
            except IndexError:
                data_res_2 = [
                    i[1],
                    'Не существует',
                    '', '', '',
                ]

        wks.update(range_name=f'B{num + 3}:F{num + 3}', values=[data_res_1])
        wks.update(range_name=f'I{num + 3}:M{num + 3}', values=[data_res_2])
        print(datetime.datetime.now(), f'{num + 1}{data_res_1 + data_res_2}')
        time.sleep(1.5)
except:
    input('Возникла ошибка')
input('Нажмите Enter для закрытия')