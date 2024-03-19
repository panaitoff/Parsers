import requests
import csv
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
        article = n[0]
        path = n[1]
        csvfile = open(path, 'w', newline='')
        fieldnames = ['product_id', 'seller_id', 'seller_discount', 'price', 'spp', 'price_spp']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        writer.writeheader()
        for num, i in enumerate(article):
            try:
                # url = f'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1400000&regions=80,38,83,4,64,33,68,70,30,40,86,69,1,31,66,48,22,114&spp=33&nm={i}'
                url = 'https://www.wildberries.ru/catalog/178927230/detail.aspx'

                rqs = requests.get(url)
                print(rqs)
                data = rqs.json()
                writer.writerow({
                    'product_id': data['data']['products'][0]['id'],
                    'seller_id': data['data']['products'][0]['supplierId'],
                    'seller_discount': data['data']['products'][0]['extended']['basicSale'],
                    'price': data['data']['products'][0]['extended']['basicPriceU'] / 100,
                    'spp': data['data']['products'][0]['extended']['clientSale'],
                    'price_spp': data['data']['products'][0]['extended']['clientPriceU'] / 100
                })
                self.progress.emit(int(((num + 1) / len(article)) * 100))
                print(data['data']['products'][0]['extended']['clientSale'])
            except IndexError:
                self.debg.emit(f'{i} - Не найден')
                self.progress.emit(int(((num + 1) / len(article)) * 100))

        self.completed.emit(100)


class WBParser(QMainWindow):
    work_requested = Signal(list)

    def __init__(self):
        super(WBParser, self).__init__()
        uic.loadUi('inteface.ui', self)
        self.pushButton.clicked.connect(self.gttextedit)

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
        self.work_requested.emit([n, path.strip()])

    def update_progress(self, v):
        self.progressBar.setValue(v)

    def debg(self, v):
        self.textBrowser.append(v)

    def complete(self, v):
        self.progressBar.setValue(v)
        self.pushButton.setEnabled(True)
        self.textBrowser.append(f'Готово')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = WBParser()
    main_app.show()

    sys.exit(app.exec())
