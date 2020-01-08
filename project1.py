import sqlite3
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLineEdit, QLCDNumber, QLabel, QCheckBox, QMainWindow, \
    QPlainTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QErrorMessage, QStackedLayout, QFrame


class Orders(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 150, 500, 500)
        self.setWindowTitle('Заказ в Ресторане')

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

        self.ordernum = QLineEdit()

        self.Header1 = QHBoxLayout()
        self.Header1.addWidget(self.DateTime, alignment=Qt.AlignLeft | Qt.AlignTop)
        self.Header1.addWidget(self.ordernum, alignment=Qt.AlignRight | Qt.AlignTop)

        self.MainScreen = QVBoxLayout()
        self.MainScreen.addLayout(self.Header1)

        self.StLayout = QStackedLayout()

        self.F1 = QFrame(self)
        self.F1.setLayout(self.FirstScreen)

        self.F2 = QFrame(self)
        self.F2.setLayout(self.MainScreen)

        self.StLayout.addWidget(self.F1)
        self.StLayout.addWidget(self.F2)

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
                result = cur.execute("""SELECT count(*) FROM meals""").fetchall()
                if len(result) == 0:
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
        self.StLayout.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Orders()
    ex.show()
    sys.exit(app.exec())