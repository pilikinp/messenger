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

    client = Client('127.0.0.1', 7777)
    msg_client = JimMessage()
    msg_server = JimAnswer()

    def __init__(self, parent = None):

        super().__init__(parent)
        # uic.loadUi('main.ui', self)

        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        # self.lock = threading.Lock()

        self.ui.login.triggered.connect(self.login)
        self.ui.listWidget_contacts.clicked.connect(self.chat)
        self.ui.pushButtonUp.pressed.connect(self.get_message)

    def get_message(self):
        sock = self.client.socket
        data = sock.recv(1024)
        data = self.msg_server.unpack(data)
        print(data)
        if 'action' in data:
            self.ui.listWidget_message.addItem('{}  {}  {}'.format(data['time'], data['from'], data['message']))
            print(data['time'], data['from'], data['message'])
            self.client.rep.add_obj(HistoryMessage(data['time'], data['from'], data['to'], data['message']))
        else:
            print('ERROR ', data['response'], data['time'], data['alert'])
            self.ui.console.addItem('{} {} {} {}'.format('ERROR ', data['response'], data['time'], data['alert']))


    def chat(self):
        self.ui.listWidget_message.clear()
        name = self.ui.listWidget_contacts.currentItem().text()
        history = self.client.rep.get_history(name)
        print(history)
        for his in history:
            self.ui.listWidget_message.addItem('{} - {} - {}'.format(his.time_, his.from_id, his.message))


    def get_contacts(self):
        self.ui.listWidget_contacts.clear()
        contacts = self.client.get_contact_list(self.client.socket)
        for cont in contacts:
            self.ui.listWidget_contacts.addItem(str(cont))

    def on_addContact_pressed(self):
        dialog = uic.loadUi('dialog_form.ui')
        def add_cont():
            name = dialog.textEditName.toPlainText()
            data = self.client.add_contact(name)
            self.ui.console.addItem(str(data))

        dialog.pushOk.clicked.connect(add_cont)
        dialog.pushOk.clicked.connect(dialog.accept)
        dialog.pushCancel.clicked.connect(dialog.reject)
        dialog.exec()
        self.get_contacts()

    def on_delContact_pressed(self):
        try:
            name = self.ui.listWidget_contacts.currentItem().text()
            data = self.client.del_contact(name)
            self.ui.console.addItem(str(data))
            self.get_contacts()

        except:
            self.ui.console.addItem('Не выбран контакт')

    def on_sendButton_pressed(self):
        message = self.ui.lineEdit_message.text()
        to_ = self.ui.listWidget_contacts.currentItem().text()
        self.ui.listWidget_message.addItem('{} - {} - {}'.format(time.ctime(), self.client.username, message))
        self.client._send_message(self.client.socket, to_, message, self.client.username)
        self.ui.lineEdit_message.clear()

###### почему если использовать для вызова функции синтаксический сахар on_login_trigger то окно QDialog появляется два раза
    def login(self):
        dialog = uic.loadUi('dialog_form.ui')

        def reg():
            name = dialog.textEditName.toPlainText()
            msg = self.client.run(name)
            self.ui.console.addItem(str(msg))

        dialog.pushOk.clicked.connect(reg)
        dialog.pushOk.clicked.connect(dialog.accept)
        dialog.pushCancel.clicked.connect(dialog.reject)
        dialog.exec()
        self.get_contacts()
        # self.get_message()
        # t1 = threading.Thread(target=self.get_message)
        # t1.daemon = True
        # t1.start()


####### почему не работает с Qlineedit??????????????????????????????????
    # def login_tr(self):
    #     dialog = uic.loadUi('dial.ui')
    #
    #     def reg():
    #         name = dialog.line.text()
    #         msg = self.client.run(name)
    #         self.ui.listWidget_message.addItem(str(msg))
    #
    #     dialog.pushOk.clicked.connect(reg)
    #     dialog.pushOk.clicked.connect(dialog.accept)
    #     dialog.pushCancel.clicked.connect(dialog.reject)
    #     dialog.exec()
    #     self.ui.listWidget_contacts.clear()
    #     cont = self.client.get_contact_list(self.client.socket)
    #     for i in cont:
    #         self.ui.listWidget_contacts.addItem(str(i))

