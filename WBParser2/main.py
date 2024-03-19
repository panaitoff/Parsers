import requests
import csv
import json

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
import sys


class Worker(QObject):
    progress = Signal(int)
    completed = Signal(int)
    debg = Signal(str)

    @Slot(list)
    def do_work(self, n):
        url = n[0]
        path = n[1]
        massive_url = [i.replace('https://www.wildberries.ru', '') for i in url]
        csvfile = open(path, 'w', newline='')
        fieldnames = ['Названия']
        max_price = int(n[2])

        for i in range(0, max_price, 100):
            fieldnames.append(f'{i}-{i + 99}')
        seo = ''
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        with open('menu.json', encoding='utf-8') as f:
            menu_json_1 = json.load(f)

        menu_json = []
        menu_json_2 = []
        menu_json_3 = []
        templates = []

        for i in menu_json_1:
            if 'childs' in list(i.keys()):
                for j in i['childs']:
                    menu_json.append(j)
            else:
                menu_json.append(i)

        for i in menu_json:
            if 'childs' in list(i.keys()):
                for j in i['childs']:
                    menu_json_2.append(j)
            else:
                menu_json_2.append(i)

        for i in menu_json_2:
            if 'childs' in list(i.keys()):
                for j in i['childs']:
                    menu_json_3.append(j)
            else:
                menu_json_3.append(i)

        for i in menu_json_3:
            if 'childs' in list(i.keys()):
                for j in i['childs']:
                    templates.append(j)
            else:
                templates.append(i)

        for reqr in massive_url:
            massiv = {}
            shard = None
            query = None
            article = []

            seo = ''
            for i in templates:
                if i['url'] == reqr:
                    shard = i['shard']
                    query = i['query']
                    if 'subject' in query:
                        break
                    for price in range(100, max_price, 100):
                        parse_url = f'https://catalog.wb.ru/catalog/{shard}/catalog?TestGroup=test_005&TestID=311&appType=1&{query}&curr=rub&dest=-1257786&regions=80,83,38,4,64,33,68,70,30,40,86,75,69,1,66,110,22,48,31,71,112,114&sort=priceup&priceU={price - 100}00%3B{price}00'
                        reqr_answ = requests.get(parse_url).json()
                        article.append([i['id'] for i in reqr_answ['data']['products']])
                    print(article)
                    for num, k in enumerate(article):
                        url = f'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1400000&regions=80,38,83,4,64,33,68,' \
                              f'70,30,40,86,69,1,31,66,48,22,114&spp=33&nm={k[0]}'
                        rqs = requests.get(url)
                        data = rqs.json()
                        try:
                            seo = i['seo']
                        except:
                            seo = i['name']
                        massiv[data['data']['products'][0]['salePriceU'] // 10000] = \
                                    data['data']['products'][0]['extended']['clientSale']

                    article = []
                    # self.progress.emit(int(((price / 100) / len(reqr)) * 100))

            mk = ['0'] * (max_price // 100 + 1)
            mk[0] = seo
            print(massiv)
            for i in massiv:
                mk[i + 1] = str(massiv[i])
            mk[-1] += '\n'
            csvfile.write(';'.join(mk))
        self.completed.emit(100)


class WBParser(QMainWindow):
    work_requested = Signal(list)

    def __init__(self, a):
        super(WBParser, self).__init__()
        uic.loadUi('inteface.ui', self)
        self.pushButton.clicked.connect(self.gttextedit)

        for i in a:
            self.textEdit.append(i)

        self.worker = Worker()
        self.worker_thread = QThread()

        self.worker.progress.connect(self.update_progress)
        self.worker.completed.connect(self.complete)
        self.worker.debg.connect(self.debg)
        self.work_requested.connect(self.worker.do_work)

        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.start()

    def gttextedit(self):
        self.pushButton.setEnabled(False)

        self.textBrowser.append(f'Старт')
        n = list([i.strip() for i in self.textEdit.toPlainText().strip().split('\n')])
        path = self.lineEdit.text()
        if path == '':
            path = '..\\result.csv'
        else:
            path += '\\result.csv'
        mx_pr = self.lineEdit_2.text().strip()
        self.work_requested.emit([n, path.strip(), mx_pr])

    def update_progress(self, v):
        self.progressBar.setValue(v)

    def debg(self, v):
        self.textBrowser.append(v)

    def complete(self, v):
        self.progressBar.setValue(v)
        self.pushButton.setEnabled(True)
        self.textBrowser.append(f'Готово')

    def closeEvent(self, event):
        fil = open('input.txt', 'w')
        for i in self.textEdit.toPlainText().strip().split('\n'):
            fil.writelines(i + '\n')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    f = [i for i in open('input.txt').readlines()]

    main_app = WBParser(f)
    main_app.show()

    sys.exit(app.exec())