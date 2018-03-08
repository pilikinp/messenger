import sys
from PyQt5 import QtWidgets
import py_form
import threading
import time
import select

from PyQt5 import Qt, QtCore, QtGui, QtWidgets, uic
from py_form import Ui_MainWindow as ui_class


from models import JimMessage, JimAnswer
from models_client import Client
from models_repository_client import Repository, Contacts, HistoryMessage


class MyWindow(QtWidgets.QMainWindow):

    def __init__(self, parent = None):

        super().__init__(parent)
        # uic.loadUi('main.ui', self)
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.monitor = Monitor(self)
        self.thread = QtCore.QThread()

        self.ui.login.triggered.connect(lambda: self.login('presence'))
        self.ui.registration.triggered.connect(lambda: self.login('registration'))
        self.ui.listWidget_contacts.clicked.connect(self.chat)

        self.monitor.gotData.connect(self.update_message)
        self.monitor.gotResp.connect(self.update_console)
        self.monitor.gotCont.connect(self.update_contacts)

    def chat(self):
        self.ui.listWidget_message.clear()
        name = self.ui.listWidget_contacts.currentItem().text()
        history = self.monitor.client.rep.get_history(name)
        print(history)
        for his in history:
            self.ui.listWidget_message.addItem('{} - {} - {}'.format(his.time_, his.from_id, his.message))
            self.ui.listWidget_message.scrollToBottom()

    def get_contacts(self):
        self.ui.listWidget_contacts.clear()
        self.monitor.client.get_contact_list(self.monitor.client.socket)



    def on_addContact_pressed(self):
        if self.ui.tabContacts.currentIndex() == 0:
            try:
                name = self.ui.listWidget_contacts.currentItem().text()
                self.monitor.client.add_contact(name)
                # self.ui.lineEditSearch.clear()
                time.sleep(0.5)
                self.get_contacts()
            except AttributeError:
                self.ui.console.addItem('Не выбран контакт')
        else:
            self.ui.tabContacts.setCurrentIndex(1)

    def on_delContact_pressed(self):
        if self.ui.tabContacts.currentIndex() == 0:
            try:
                name = self.ui.listWidget_contacts.currentItem().text()
                self.monitor.client.del_contact(name)
                time.sleep(0.5) # Почему без данной задержки не работает
                self.get_contacts()
            except AttributeError:
                self.ui.console.addItem('Не выбран контакт')

    def on_sendButton_pressed(self):
        try:
            message = self.ui.lineEdit_message.text()
            to_ = self.ui.listWidget_contacts.currentItem().text()
            self.ui.listWidget_message.addItem('{} - {} - {}'.format(time.ctime(), self.monitor.client.username, message))
            self.ui.listWidget_message.scrollToBottom()
            self.monitor.client._send_message(self.monitor.client.socket, to_, message, self.monitor.client.username)
            self.ui.lineEdit_message.clear()
            self.ui.lineEdit_message.setFocus()
        except AttributeError:
            self.ui.console.addItem('Не выбран контакт')

    @QtCore.pyqtSlot(str)
    def update_message(self, data):
        self.ui.listWidget_message.addItem(data)
        self.ui.listWidget_message.scrollToBottom()

    @QtCore.pyqtSlot(dict)
    def update_console(self, data):
        self.ui.console.addItem('{} - {} - {}'.format(data['response'], data['time'], data['alert']))
        self.ui.console.scrollToBottom()
        self.ui.statusbar.showMessage('{} - {} - {}'.format(data['response'], data['time'], data['alert']))
        # if data['response'] == '402':
        #     self.thread.quit()
        #     print('поток остановлен') Надо ли останавливать потое?? Если вход не выполнен и будет попытка повторного входа


    @QtCore.pyqtSlot(dict)
    def update_contacts(self, data):
        # self.ui.listWidget_contacts.clear()
        for contact in data['users']:
            self.ui.listWidget_contacts.addItem(str(contact))

    def on_lineEditSearch_textChanged(self):
        try:
            text = self.ui.lineEditSearch.text()
            self.ui.listWidget_contacts.clear()
            self.monitor.client.search_contact(text)
        except AttributeError:
            self.ui.console.addItem('Требуется выполнить вход')

###### почему если использовать для вызова функции 'синтаксический сахар' on_login_triggered то окно QDialog появляется
    # два раза

    def login(self, action):
        dialog = uic.loadUi('dial.ui')
        self.monitor.moveToThread(self.thread)
        self.thread.started.connect(self.monitor.recv_msg)
        dialog.line.setFocus()

        def reg():
            name = dialog.line.text()
            self.monitor.client.run(name, action)
            self.thread.start()

        dialog.pushOk.clicked.connect(reg)
        dialog.pushOk.clicked.connect(dialog.accept)
        dialog.exec()



class Monitor(QtCore.QObject):

    msg_client = JimMessage()
    msg_server = JimAnswer()
    gotData = QtCore.pyqtSignal(str)
    gotResp = QtCore.pyqtSignal(dict)
    gotCont = QtCore.pyqtSignal(dict)



    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.client = Client('127.0.0.1', 7777)
        self.resv_queue = self.client.recv_queue

    def recv_msg(self):
        while 1:
            data = self.resv_queue.get()
            print(data)
            if 'action' in data and data['action'] == 'msg':
                self.gotData.emit('{} - {} - {}'.format(data['time'], data['from'], data['message']))
            elif 'response' in data:
                self.gotResp.emit(data)
            elif 'users' in data:
                self.gotCont.emit(data)
            self.resv_queue.task_done()






