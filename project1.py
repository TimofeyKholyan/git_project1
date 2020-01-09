import sqlite3
import sys
from datetime import datetime
from threading import Timer,Thread,Event
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLineEdit, QLCDNumber, QLabel, QCheckBox, QMainWindow, \
    QPlainTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QErrorMessage, QStackedLayout, QFrame, QScrollArea, QGridLayout

class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

class Orders(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def closeEvent(self, event):
        if self.Timer:
            self.Timer.cancel()
        event.accept()

    def initUI(self):
        self.setGeometry(200, 150, 500, 500)
        self.setWindowTitle('Заказ в Ресторане')

        self.IsMenuLoaded = False

        self.DescriptionLabel = QPlainTextEdit('Программа оформления заказов в ресторане')
        self.DescriptionLabel.setReadOnly(True)

        self.Help1 = QLabel('Укажите путь до базы данных')

        self.PathToDB = QLineEdit()

        self.OpenDBFile = QPushButton('...')
        self.OpenDBFile.clicked.connect(self.on_select_file)

        self.StartBtn = QPushButton('Старт')
        self.StartBtn.clicked.connect(self.on_start)

        self.OpenFileLayout = QHBoxLayout()
        self.OpenFileLayout.addWidget(self.PathToDB)
        self.OpenFileLayout.addWidget(self.OpenDBFile)

        self.FirstScreen = QVBoxLayout()
        self.FirstScreen.addWidget(self.DescriptionLabel, alignment=Qt.AlignCenter)
        self.FirstScreen.addWidget(self.Help1, alignment=Qt.AlignCenter)
        self.FirstScreen.addLayout(self.OpenFileLayout)
        self.FirstScreen.addWidget(self.StartBtn, alignment=Qt.AlignCenter)
        self.FirstScreen.addStretch(1)

        self.DateTime = QLineEdit()
        self.DateTime.setReadOnly(True)

        self.ordernum = QLineEdit()
        self.ordernum.setReadOnly(True)

        self.Header1 = QHBoxLayout()
        self.Header1.addWidget(self.DateTime, alignment=Qt.AlignLeft | Qt.AlignTop)
        self.Header1.addWidget(self.ordernum, alignment=Qt.AlignRight | Qt.AlignTop)

        self.SaveOrderBtn = QPushButton('Оформить заказ')
        self.SaveOrderBtn.clicked.connect(self.get_receipt)

        self.StatsBtn = QPushButton('Отчёт')
        self.StatsBtn.clicked.connect(self.get_stats)

        self.MenuLayout = QGridLayout()

        self.MenuForm = QWidget()
        self.MenuForm.setLayout(self.MenuLayout)

        self.Menu1 = QScrollArea()
        self.Menu1.setWidget(self.MenuForm)
        self.Menu1.setWidgetResizable(True)

        self.Footer1 = QHBoxLayout()
        self.Footer1.addWidget(self.SaveOrderBtn, alignment=Qt.AlignCenter | Qt.AlignBottom)
        self.Footer1.addWidget(self.StatsBtn, alignment=Qt.AlignCenter | Qt.AlignBottom)

        self.Help2 = QLabel('Сумма заказа: ')

        self.TotalMoney = QLineEdit()
        self.TotalMoney.setReadOnly(True)
        self.TotalMoney.setFixedWidth(200)

        self.Footer2 = QHBoxLayout()
        self.Footer2.addWidget(self.Help2, alignment=Qt.AlignLeft | Qt.AlignCenter)
        self.Footer2.addWidget(self.TotalMoney, alignment=Qt.AlignLeft | Qt.AlignBottom)
        self.Footer2.addStretch(1)

        self.MainScreen = QVBoxLayout()
        self.MainScreen.addLayout(self.Header1)
        self.MainScreen.addWidget(self.Menu1, stretch=1)
        self.MainScreen.addLayout(self.Footer2)
        self.MainScreen.addLayout(self.Footer1)

        self.Notification = QLabel('Заказ прошёл успешно')

        self.Receipt = QPlainTextEdit()
        self.Receipt.setReadOnly(True)

        self.Back1 = QPushButton('Назад')
        self.Back1.clicked.connect(self.start_main)

        self.OrderScreen = QVBoxLayout()
        self.OrderScreen.addWidget(self.Notification, alignment=Qt.AlignCenter|Qt.AlignTop)
        self.OrderScreen.addWidget(self.Receipt, stretch=1)
        self.OrderScreen.addWidget(self.Back1, alignment=Qt.AlignCenter|Qt.AlignBottom)

        self.Stats = QPlainTextEdit()
        self.Stats.setReadOnly(True)

        self.Back2 = QPushButton('Назад')
        self.Back2.clicked.connect(self.back_to_main)

        self.StatsScreen = QVBoxLayout()
        self.StatsScreen.addWidget(self.Stats, stretch=1)
        self.StatsScreen.addWidget(self.Back2, alignment=Qt.AlignCenter|Qt.AlignBottom)

        self.StLayout = QStackedLayout()

        self.Frame1 = QFrame(self)
        self.Frame1.setLayout(self.FirstScreen)

        self.StLayout.addWidget(self.Frame1)

        self.setLayout(self.StLayout)

    def on_select_file(self):
        FileName, _ = QFileDialog.getOpenFileName(self, 'Открыть базу данных', None, '*.db')
        if FileName:
            self.PathToDB.setText(FileName)

    def get_filename(self):
        return self.PathToDB.text()

    def on_start(self):
        FileName = self.get_filename()
        if FileName:
            try:
                con = sqlite3.connect(FileName)
                cur = con.cursor()
                self.meals = cur.execute("""SELECT id, name, price FROM meals""").fetchall()
                if len(self.meals) == 0:
                    msg = QErrorMessage(self)
                    msg.showMessage('В базе данных нет продуктов')
                con.close()
                self.start_main()
            except Exception as e:
                msg = QErrorMessage(self)
                msg.showMessage('Неверный путь до базы данных. ' + str(e))
        else:
            msg = QErrorMessage(self)
            msg.showMessage('Не указан путь до базы данных')

    def GetMaxOrdersNum(self):
        con = sqlite3.connect(self.get_filename())
        cur = con.cursor()
        maxId = cur.execute("""SELECT MAX(id) FROM orders""").fetchone()
        con.close()
        if maxId[0] is None:
            return 0
        return maxId[0]

    def SaveOrder(self):
        con = sqlite3.connect(self.get_filename())
        cur = con.cursor()
        cur.execute("""INSERT INTO orders (date) VALUES (date('now'))""")
        self.OrderId = cur.lastrowid
        for i in self.choices:
            if i.isChecked() and int(self.numbers[self.choices.index(i)].text()) != 0:
                cur.execute("""INSERT INTO ordered (id_order,id_meal,count) VALUES (?,?,?)""",
                            (self.OrderId,self.mealsid[self.choices.index(i)],int(self.numbers[self.choices.index(i)].text())))
        con.commit()
        con.close()

    def getStatsDaily(self):
        con = sqlite3.connect(self.get_filename())
        cur = con.cursor()
        result = cur.execute("""SELECT id_meal, count FROM ordered 
                                    WHERE(id_order in (SELECT id FROM orders WHERE date=date('now')))""").fetchall()
        con.close()
        g = []
        for i in self.mealsid:
            s = 0
            for j in result:
                if j[0] == i:
                    s += j[1]
            if s != 0:
                g.append((i, s))
        return g

    def getTotalSell(self):
        con = sqlite3.connect(self.get_filename())
        cur = con.cursor()
        result = cur.execute("""SELECT id_meal, count FROM ordered 
                                    WHERE(id_order in (SELECT id FROM orders WHERE date=date('now')))""").fetchall()
        con.close()
        s = 0.0
        for i in result:
            ind = self.mealsid.index(i[0])
            s += self.prices[ind] * i[1]
        return s

    def updateTime(self):
        now = datetime.now()
        self.DateTime.setText(now.strftime("%d.%m.%Y %H:%M:%S"))

    def start_main(self):
        self.ordernum.setText('Заказ №' + str(self.GetMaxOrdersNum() + 1))
        self.TotalMoney.setText('0.0 рублей')
        if not self.IsMenuLoaded:
            self.timer = perpetualTimer(1,self.updateTime)
            self.timer.start()
            self.updateTime()
            self.mealsid = []
            self.prices = []
            self.choices = []
            self.money = []
            self.counting = []
            self.numbers = []
            for i, row in enumerate(self.meals):
                self.mealsid.append(row[0])
                self.prices.append(row[2])
                qc = QCheckBox(row[1])
                qc.clicked.connect(self.updateTotalMoney)
                self.choices.append(qc)
                self.MenuLayout.addWidget(qc, i, 1)
                qm = QLabel(str(self.prices[i]) + ' р.')
                self.MenuLayout.addWidget(qm, i, 2)
                btn, btn2 = QPushButton('-'), QPushButton('+')
                self.MenuLayout.addWidget(btn, i, 3)
                self.MenuLayout.addWidget(btn2, i, 4)
                btn.setFixedWidth(40)
                btn2.setFixedWidth(40)
                btn.clicked.connect(self.less)
                btn2.clicked.connect(self.more)
                self.counting.append(btn)
                self.counting.append(btn2)
                qn = QLabel('0')
                self.numbers.append(qn)
                self.MenuLayout.addWidget(qn, i, 5)

            self.MenuLayout.setColumnStretch(5,1)
            self.MenuLayout.setRowStretch(len(self.meals),1)
            self.Frame2 = QFrame(self)
            self.Frame2.setLayout(self.MainScreen)
            self.StLayout.addWidget(self.Frame2)
            self.Frame3 = QFrame(self)
            self.Frame3.setLayout(self.OrderScreen)
            self.StLayout.addWidget(self.Frame3)
            self.Frame4 = QFrame(self)
            self.Frame4.setLayout(self.StatsScreen)
            self.StLayout.addWidget(self.Frame4)
            self.IsMenuLoaded = True
        else:
            # обнулить все значения
            for i in self.numbers:
                i.setText('0')
            for i in self.choices:
                i.setChecked(False)
        self.StLayout.setCurrentIndex(1)

    def back_to_main(self):
        self.StLayout.setCurrentIndex(1)

    def get_receipt(self):
        self.start_receipt()

    def start_receipt(self):
        try:
            if sum([int(self.numbers[self.choices.index(i)].text()) for i in self.choices if i.isChecked()]) == 0:
                msg = QErrorMessage(self)
                msg.showMessage('Не выбрано ни одного блюда.')
                return
            self.SaveOrder()
            self.Receipt.setPlainText(self.PrintReciept())
            self.StLayout.setCurrentIndex(2)
        except Exception as e:
            msg = QErrorMessage(self)
            msg.showMessage('Ошибка: ' + str(e))

    def PrintReciept(self):
        ordered = [i.text() + ' (*' + self.numbers[self.choices.index(i)].text() + ')' + ' - ' + str(int(self.numbers[self.choices.index(i)].text()) * self.prices[self.choices.index(i)]) + ' рублей' for i in self.choices if i.isChecked() and self.numbers[self.choices.index(i)].text() != '0']
        strReciept = ''
        strReciept= strReciept + '------------------------------------------' + '\n'

        now = datetime.now()
        strReciept= strReciept + 'Заказ №' + str(self.OrderId) + '  ' + now.strftime("%d.%m.%Y %H:%M:%S")
        strReciept= strReciept + '\n' + '------------------------------------------' + '\n'
        strReciept= strReciept + str('\n'.join(ordered))
        strReciept= strReciept + '\n' + '------------------------------------------' + '\n'
        strReciept= strReciept + 'Всего - ' + str(self.calculateTotal()) + ' рублей'
        strReciept= strReciept + '\n' + '------------------------------------------' + '\n'
        return strReciept

    def get_stats(self):
        self.start_stats()

    def start_stats(self):
        try:
            self.Stats.setPlainText(self.PrintStats())
            self.StLayout.setCurrentIndex(3)
        except Exception as e:
            msg = QErrorMessage(self)
            msg.showMessage('Ошибка: ' + str(e))

    def PrintStats(self):
        StatsDaily = self.getStatsDaily()
        TotalSell = self.getTotalSell()
        now = datetime.now()
        strStats = ''
        strStats += 'Отчёт за ' + now.strftime("%d.%m.%Y")
        strStats += '\n\nПродано за день:\n'
        for i in StatsDaily:
            mealnum = self.mealsid.index(i[0])
            strStats += '- ' + self.choices[mealnum].text() + ': ' + str(i[1]) + ' шт.\n'
        strStats += 'Всего продано товаров на сумму ' + str(TotalSell) + ' рублей.'
        return strStats

    def less(self):
        number = self.numbers[self.counting.index(self.sender()) // 2]
        if number.text() != '0':
            number.setText(str(int(number.text()) - 1))
        self.updateTotalMoney()

    def more(self):
        number = self.numbers[self.counting.index(self.sender()) // 2]
        number.setText(str(int(number.text()) + 1))
        self.updateTotalMoney()

    def updateTotalMoney(self):
        self.TotalMoney.setText(str(self.calculateTotal()) + ' рублей')

    def calculateTotal(self):
        return float(sum([float(self.numbers[self.choices.index(i)].text()) * self.prices[self.choices.index(i)] for i in self.choices if i.isChecked()]))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Orders()
    ex.show()
    sys.exit(app.exec())