import sqlite3
import sys
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLineEdit, QLCDNumber, QLabel, QCheckBox, QMainWindow, \
    QPlainTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QErrorMessage, QStackedLayout, QFrame, QScrollArea, QGridLayout


class Orders(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

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

        self.StatsBtn = QPushButton('Отчёт')

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

        self.Footer2 = QHBoxLayout()
        self.Footer2.addWidget(self.Help2, alignment=Qt.AlignLeft | Qt.AlignCenter)
        self.Footer2.addWidget(self.TotalMoney, alignment=Qt.AlignLeft | Qt.AlignBottom)
        self.Footer2.addStretch(1)

        self.MainScreen = QVBoxLayout()
        self.MainScreen.addLayout(self.Header1)
        self.MainScreen.addWidget(self.Menu1, stretch=1)
        self.MainScreen.addLayout(self.Footer2)
        self.MainScreen.addLayout(self.Footer1)

        self.StLayout = QStackedLayout()

        self.F1 = QFrame(self)
        self.F1.setLayout(self.FirstScreen)



        self.StLayout.addWidget(self.F1)

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

    def start_main(self):
        now = datetime.now()
        self.DateTime.setText(now.strftime("%d %B %Y"))
        self.ordernum.setText('Заказ №1')
        self.TotalMoney.setText('0 рублей')
        if not self.IsMenuLoaded:
            self.prices = []
            self.choices = []
            self.money = []
            self.counting = []
            self.numbers = []
            for i, row in enumerate(self.meals):
                self.prices.append(row[2])
                qc = QCheckBox(row[1])
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
            self.MenuLayout.setRowStretch(7,1)
            self.F2 = QFrame(self)
            self.F2.setLayout(self.MainScreen)
            self.StLayout.addWidget(self.F2)
            self.IsMenuLoaded = True

        # обнулить все значения
        self.StLayout.setCurrentIndex(1)

    def less(self):
        number = self.numbers[self.counting.index(self.sender()) // 2]
        if number.text() != '0':
            number.setText(str(int(number.text()) - 1))

    def more(self):
        number = self.numbers[self.counting.index(self.sender()) // 2]
        number.setText(str(int(number.text()) + 1))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Orders()
    ex.show()
    sys.exit(app.exec())