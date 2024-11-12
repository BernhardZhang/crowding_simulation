from pkgutil import resolve_name

from PyQt6 import QtWidgets, QtCore, QtNetwork
from sim import Ui_Form
import json
import random

class Widget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)
        self.setupUi(self)
        self.create_table_widget()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer_refresh = QtCore.QTimer()
        self.timer_refresh.timeout.connect(self.on_refresh_token)
        self.pushButton_start.clicked.connect(self.on_start)
        self.pushButton_end.clicked.connect(self.on_end)
        self.token = ''
        self.manager = QtNetwork.QNetworkAccessManager()
        self.spinBox.valueChanged.connect(self.on_interval_change)
        self.pushButton_end.setEnabled(False)
        self.refresh_manager = QtNetwork.QNetworkAccessManager()
        self.sim_manager = QtNetwork.QNetworkAccessManager()
        self.total = 0

    def on_interval_change(self):
        self.timer.stop()
        self.timer.setInterval(1000 * self.spinBox.value())
        self.timer.start()

    def on_end(self):
        self.timer.stop()
        self.timer_refresh.stop()
        self.pushButton_start.setEnabled(True)
        self.pushButton_end.setEnabled(False)

    def on_start(self):
        data = {
            "account": 'account',
            "password": 'SR4cE/2kQmWV6YcA1xgIxG76AlF2oZvRyj9yduC10n8YzLD634ur4lpj/L6hOUj8'
        }
        ip = self.lineEdit.text()
        url = QtCore.QUrl('http://' + ip + '/api/v1/login')
        request = QtNetwork.QNetworkRequest(url)
        request.setHeader(QtNetwork.QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        reply = self.manager.post(request, QtCore.QByteArray(json.dumps(data).encode()))
        reply.finished.connect(self.on_reply)
        self.pushButton_start.setEnabled(False)
        self.pushButton_end.setEnabled(True)
        self.timer.start(1000 * self.spinBox.value())
        self.timer_refresh.start(1000 * 300)

    def on_reply(self):
        reply = self.sender()
        try:
            data = json.loads(reply.readAll().data().decode())
        except (json.JSONDecodeError):
            return
        self.token = data.get('token')

    def on_refresh_token(self):
        ip = self.lineEdit.text()
        url = QtCore.QUrl('http://' + ip + '/api/v1/refresh')
        request = QtNetwork.QNetworkRequest(url)
        request.setHeader(QtNetwork.QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        request.setRawHeader(b"token", self.token.encode())
        reply = self.refresh_manager.post(request, QtCore.QByteArray())
        reply.finished.connect(self.on_reply)

    def on_timer(self):
        for i in range(self.tableWidget.rowCount()):
            line_code = self.tableWidget.item(i, 0)
            train_code = self.tableWidget.item(i, 1)
            current_station = self.tableWidget.item(i, 2)
            next_station = self.tableWidget.item(i, 3)
            direction = self.tableWidget.item(i, 4)
            crowding = self.tableWidget.item(i, 5)

            data = {
                "line": line_code.text(),
                "train": train_code.text(),
                "current": current_station.text(),
                "next": next_station.text(),
                "direction": int(direction.text()),
                "crowding": list(map(int, crowding.text().split(",")))
            }

            ip = self.lineEdit.text()
            url = QtCore.QUrl('http://' + ip + '/api/v1/car_density/' + line_code.text() + '/' + train_code.text())
            request = QtNetwork.QNetworkRequest(url)
            request.setHeader(QtNetwork.QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
            request.setRawHeader(b"token", self.token.encode())
            self.sim_manager.post(request, QtCore.QByteArray(json.dumps(data).encode()))

    def create_table_widget(self):
        settings = QtCore.QSettings("config.ini", QtCore.QSettings.Format.IniFormat)
        number_of_trains = int(settings.value("number_of_trains", 0))
        self.tableWidget.setRowCount(number_of_trains)
        self.tableWidget.setColumnCount(6)

        self.tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('綫路編號'))
        self.tableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('列車編號'))
        self.tableWidget.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('當前站'))
        self.tableWidget.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem('下一站'))
        self.tableWidget.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem('方向'))
        self.tableWidget.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem('擁擠度'))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setVerticalHeaderLabels([])

        line_code = settings.value("line_code", '')
        number_of_stations = int(settings.value("number_of_stations", 0))
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(line_code))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{line_code + '-TR'}{i+1:02d}"))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{line_code+ '-ST'}{random.randint(1, number_of_stations):02d}"))
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{line_code+ '-ST'}{random.randint(1, number_of_stations):02d}"))
            self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(str(random.randint(1, 2))))
            self.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem('1,2,2,3,4,3,5'))