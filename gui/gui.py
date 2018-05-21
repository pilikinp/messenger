import time

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from gui.py_form import Ui_MainWindow as ui_class
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QFont

from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

from jim.models import JimMessage, JimAnswer
from client.models_client import Client
# from client.async_client import Client #не разобрался как сделать, зависает в ожидание посылок от сервера
class MyWindow(QtWidgets.QMainWindow):

    flag = False

    def __init__(self, parent = None):

        super().__init__(parent)
        # uic.loadUi('main.ui', self)
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        # self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)

        self.ui.sendButton.setIcon(QIcon('gui/icon/send.png'))
        self.ui.sendButton.setStyleSheet('QPushButton {background-color: #ffffff}')
        self.ui.listWidget_contacts.setIconSize(QtCore.QSize(35, 35))

        self.monitor = Monitor(self)
        self.thread = QtCore.QThread()

        self.bold = QAction(QIcon('gui/icon/b.jpg'), 'Bold', self)
        self.italic = QAction(QIcon('gui/icon/i.jpg'), 'Italic', self)
        self.underlined = QAction(QIcon('gui/icon/u.jpg'), 'Underlined', self)
        self.smile = QAction(QIcon('gui/smile/ab.gif'), ' Smile', self)
        self.melancholy = QAction(QIcon('gui/smile/ac.gif'), 'Melancholy', self)
        self.surprise = QAction(QIcon('gui/smile/ai.gif'), 'Surprise', self)
        self.bold.setCheckable(True)
        self.italic.setCheckable(True)
        self.underlined.setCheckable(True)
        self.ui.toolBar.addAction(self.bold)
        self.ui.toolBar.addAction(self.italic)
        self.ui.toolBar.addAction(self.underlined)
        self.ui.toolBar.addAction(self.smile)
        self.ui.toolBar.addAction(self.melancholy)
        self.ui.toolBar.addAction(self.surprise)

        self.bold.triggered.connect(self.action_bold)
        self.italic.triggered.connect(self.action_italic)
        self.underlined.triggered.connect(self.action_underlined)
        self.smile.triggered.connect(lambda: self.action_smile('gui/smile/ab.gif'))
        self.melancholy.triggered.connect(lambda: self.action_smile('gui/smile/ac.gif'))
        self.surprise.triggered.connect(lambda: self.action_smile('gui/smile/ai.gif'))

        self.ui.login.triggered.connect(lambda: self.login('presence'))
        # self.ui.registration.triggered.connect(lambda: self.login('registration'))
        self.ui.registration.triggered.connect(lambda: self.registration())
        self.ui.profile.triggered.connect(self.profile)
        self.ui.listWidget_contacts.clicked.connect(self.chat)

        self.monitor.gotData.connect(self.update_message)
        self.monitor.gotResp.connect(self.update_console)
        self.monitor.gotCont.connect(self.update_contacts)
        self.monitor.gotChat.connect(self.update_chats)

        ################################################

    #################################################################################
    #Функции форматирования
    #продумать чтобы можно было добавлять одновременно и жирный и италик и подчеркнутый
    #добавить форматировние выделенного текста, Как у выделенного текста определить его стиль

    def action_bold(self):
        myFont = QFont()
        if self.bold.isChecked():
            myFont.setBold(True)
            self.ui.textEdit_message.setFont(myFont)
        else:
            myFont.setBold(False)
            self.ui.textEdit_message.setFont(myFont)

    def action_italic(self):
        myFont = QFont()
        if self.italic.isChecked():
            myFont.setItalic(True)
            self.ui.textEdit_message.setFont(myFont)
        else:
            myFont.setItalic(False)
            self.ui.textEdit_message.setFont(myFont)

    def action_underlined(self):
        myFont = QFont()
        if self.underlined.isChecked():
            myFont.setUnderline(True)
            self.ui.textEdit_message.setFont(myFont)
        else:
            myFont.setUnderline(False)
            self.ui.textEdit_message.setFont(myFont)

    ##################################################################################
    # Смайлики
    # сделать при наведении на иконку смайлика чтобы открывалось окно с разными смайлами
    def action_smile(self, url):
        text = self.ui.textEdit_message.toHtml()
        self.ui.textEdit_message.setText('{} <img src="{}" />'.format(text, url))
        self.ui.textEdit_message.moveCursor(11)

########################################################################################

    def chat(self):
        self.ui.listWidget_message.clear()
        name = self.ui.listWidget_contacts.currentItem().text()
        if self.monitor.client.rep.get_contact(name):
            avatar = self.monitor.client.rep.get_avatar_contact(name)
            pixmap = QtGui.QImage.fromData(avatar)
            pixmap = QtGui.QPixmap.fromImage(pixmap)

            self.ui.listWidget_contacts.currentItem().setIcon(QIcon(pixmap))

            history = self.monitor.client.rep.get_history(name, self.monitor.client.username)
            print(history)
            for his in history:
                # self.ui.listWidget_message.addItem('{} - {} - {}'.format(his.time_, his.from_id, his.message))
                item = QtWidgets.QListWidgetItem()

                widget = QtWidgets.QWidget()
                widgetText = QtWidgets.QLabel(his.message)
                widgetTime = QtWidgets.QLabel(his.time_)
                widgetName = QtWidgets.QLabel(his.from_id)
                widgetLayout = QtWidgets.QHBoxLayout()
                widgetLayout.addWidget(widgetTime)
                widgetLayout.addWidget(widgetName)
                widgetLayout.addWidget(widgetText)

                widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                widget.setLayout(widgetLayout)
                item.setSizeHint(widget.sizeHint())

                self.ui.listWidget_message.addItem(item)
                self.ui.listWidget_message.setItemWidget(item, widget)
                self.ui.listWidget_message.scrollToBottom()


    def get_contacts(self):
        self.ui.listWidget_contacts.clear()
        self.monitor.client.get_contact_list(self.monitor.client.socket)

    def get_chat_list(self):
        self.ui.listWidget_chat.clear()
        self.monitor.client.get_chat_list()

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
            if self.ui.listWidget_chat.currentItem():
                chat_name = self.ui.listWidget_chat.currentItem().text()
                self.monitor.client.add_chat(chat_name)
            else:
                pass
                # добавить открытие диалогового окна на добавление нового чата

    def on_delContact_pressed(self):
        if self.ui.tabContacts.currentIndex() == 0:
            try:
                name = self.ui.listWidget_contacts.currentItem().text()
                self.monitor.client.del_contact(name)
                time.sleep(0.5) # Почему без данной задержки не работает. попробовать избавиться от задержек
                self.get_contacts()
            except AttributeError:
                self.ui.console.addItem('Не выбран контакт')

    def on_sendButton_pressed(self):
        try:
            if self.ui.tabContacts.currentIndex() == 0:
                message = self.ui.textEdit_message.toHtml()
                to_ = self.ui.listWidget_contacts.currentItem().text()
                print(to_)
                #поменять способ добавления контактов, сделать чтобы контакты добавлялись
                #если написать им сообщение или получить сообщение
                item = QtWidgets.QListWidgetItem()

                widget = QtWidgets.QWidget()
                widgetText = QtWidgets.QLabel(message)
                widgetName = QtWidgets.QLabel(self.monitor.client.username)
                widgetTime = QtWidgets.QLabel(time.ctime())
                widgetLayout = QtWidgets.QHBoxLayout()
                widgetLayout.addWidget(widgetTime)
                widgetLayout.addWidget(widgetName)
                widgetLayout.addWidget(widgetText)
                # widgetLayout.addStretch()

                widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                widget.setLayout(widgetLayout)
                item.setSizeHint(widget.sizeHint())

                self.ui.listWidget_message.addItem(item)
                self.ui.listWidget_message.setItemWidget(item, widget)

                self.ui.listWidget_message.scrollToBottom()
                self.monitor.client._send_message(
                    self.monitor.client.socket, to_, message, self.monitor.client.username, self.ui.security.isChecked())
                self.ui.textEdit_message.clear()
                self.ui.textEdit_message.setFocus()
            else:
                message = self.ui.textEdit_message.toHtml()
                to_ = ''
                print(to_)
                # поменять способ добавления контактов, сделать чтобы контакты добавлялись
                # если написать им сообщение или получить сообщение
                item = QtWidgets.QListWidgetItem()

                widget = QtWidgets.QWidget()
                widgetText = QtWidgets.QLabel(message)
                widgetName = QtWidgets.QLabel(self.monitor.client.username)
                widgetTime = QtWidgets.QLabel(time.ctime())
                widgetLayout = QtWidgets.QHBoxLayout()
                widgetLayout.addWidget(widgetTime)
                widgetLayout.addWidget(widgetName)
                widgetLayout.addWidget(widgetText)
                # widgetLayout.addStretch()

                widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                widget.setLayout(widgetLayout)
                item.setSizeHint(widget.sizeHint())

                self.ui.listWidget_message.addItem(item)
                self.ui.listWidget_message.setItemWidget(item, widget)

                self.ui.listWidget_message.scrollToBottom()
                self.monitor.client._send_message(
                    self.monitor.client.socket, to_, message, self.monitor.client.username,
                    self.ui.security.isChecked())
                self.ui.textEdit_message.clear()
                self.ui.textEdit_message.setFocus()
            # Добавить отправку сообщений в чаты
        except AttributeError:
            self.ui.console.addItem('Не выбран контакт')

    @QtCore.pyqtSlot(dict)
    def update_message(self, data_recv):
        data = data_recv['data']
        if self.ui.listWidget_contacts.currentItem() and self.ui.listWidget_contacts.currentItem().text() == data['from'] and self.ui.tabContacts.currentIndex() == 0:
            ##########################
            #сделать отдельной функцией
            item = QtWidgets.QListWidgetItem()

            widget = QtWidgets.QWidget()
            widgetText = QtWidgets.QLabel(data['message'])
            widgetName = QtWidgets.QLabel(data['from'])
            widgetTime = QtWidgets.QLabel(data_recv['time'])
            widgetLayout = QtWidgets.QHBoxLayout()
            widgetLayout.addWidget(widgetTime)
            widgetLayout.addWidget(widgetName)
            widgetLayout.addWidget(widgetText)
            # widgetLayout.addStretch()

            widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
            widget.setLayout(widgetLayout)
            item.setSizeHint(widget.sizeHint())
            ##################################################
            self.ui.listWidget_message.addItem(item)
            self.ui.listWidget_message.setItemWidget(item, widget)
            ################################
            self.ui.listWidget_message.scrollToBottom()
        else:
            a = self.ui.listWidget_contacts.findItems(data['from'], QtCore.Qt.MatchContains)
            print(a)
            a[0].setIcon(QIcon('gui/icon/send.png'))

    @QtCore.pyqtSlot(dict)
    def update_console(self, data):
        self.ui.console.addItem('{} - {} - {}'.format(data['response'], data['time'], data['data']['alert']))
        self.ui.console.scrollToBottom()
        if data['response'] == '102':
            self.setWindowTitle('Messenger - {}'.format(data['data']['user']))
        self.ui.statusbar.showMessage('{} - {} - {}'.format(data['response'], data['time'], data['data']['alert']))
        # if data['response'] == '402':
        #     self.thread.quit()
        #     print('поток остановлен') Надо ли останавливать потое?? Если вход не выполнен и будет попытка повторного входа


    @QtCore.pyqtSlot(dict)
    def update_contacts(self, data):
        self.ui.listWidget_contacts.clear()
        for contact, d in data['users'].items():
            pixmap = QtGui.QImage.fromData(d[1], 'png')
            pixmap = QtGui.QPixmap.fromImage(pixmap)

            contact = QtWidgets.QListWidgetItem(str(contact))
            contact.setIcon(QIcon(pixmap))
            self.ui.listWidget_contacts.addItem(contact)


    @QtCore.pyqtSlot(dict)
    def update_chats(self, data_recv):
        data = data_recv['data']
        if self.ui.tabContacts.currentIndex() == 1:
            item = QtWidgets.QListWidgetItem()

            widget = QtWidgets.QWidget()
            widgetText = QtWidgets.QLabel(data['message'])
            widgetName = QtWidgets.QLabel(data['from'])
            widgetTime = QtWidgets.QLabel(data_recv['time'])
            widgetLayout = QtWidgets.QHBoxLayout()
            widgetLayout.addWidget(widgetTime)
            widgetLayout.addWidget(widgetName)
            widgetLayout.addWidget(widgetText)
            # widgetLayout.addStretch()

            widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
            widget.setLayout(widgetLayout)
            item.setSizeHint(widget.sizeHint())
            ##################################################
            self.ui.listWidget_message.addItem(item)
            self.ui.listWidget_message.setItemWidget(item, widget)
            ################################
            self.ui.listWidget_message.scrollToBottom()

        else:
            print('чат')

    def on_lineEditSearch_textChanged(self):
        try:
            text = self.ui.lineEditSearch.text()
            self.ui.listWidget_contacts.clear()
            self.monitor.client.search_contact(text)
        except AttributeError:
            self.ui.console.addItem('Требуется выполнить вход')

# перенести все диалоговые окна и работу с ними в отдельные скрипты
    def login(self, action):

        dialog = uic.loadUi('gui/dial.ui')
        file = ''
        self.monitor.moveToThread(self.thread)
        self.thread.started.connect(self.monitor.recv_msg)
        dialog.lineEdit_login.setFocus()

        def reg():
            name = dialog.lineEdit_login.text()
            password = dialog.lineEdit_password.text()
            self.monitor.client.run(name, password, file, action)
            self.thread.start()

        dialog.pushOk.clicked.connect(reg)
        dialog.pushOk.clicked.connect(dialog.accept)
        dialog.exec()

    def registration(self):
        dialog = uic.loadUi('gui/reg_form.ui')
        with open('gui/icon/ava.png', 'rb') as f:
            dialog.file = f.read()
            print(dialog.file)
        pixmap = QtGui.QPixmap('gui/icon/ava.png')
        dialog.label_ava.resize(300, 200)
        dialog.label_ava.setPixmap(pixmap)
        self.monitor.moveToThread(self.thread)
        self.thread.started.connect(self.monitor.recv_msg)

        def reg():
            action = 'registration'
            print(dialog.file)
            name = dialog.lineEdit_login.text()
            password = dialog.lineEdit_password.text()
            #добавить сохранение дополнительных полей в базу данных
            self.monitor.client.run(name, password, dialog.file, action)
            self.thread.start()

        def open_file():

            fname = QtWidgets.QFileDialog.getOpenFileName(dialog, 'Open file', '/')[0]
            image = Image.open(fname)
            width = image.size[0]
            height = image.size[1]
            while width > 300:
                width = int(width*0.8)
                height = int(height*0.8)
            image = image.resize((width, height), Image.ANTIALIAS)
            img_tmp = ImageQt(image.convert('RGBA'))
            pixmap = QtGui.QPixmap.fromImage(img_tmp)
            ######################################
            inbyte = QtCore.QByteArray()
            inbuf = QtCore.QBuffer(inbyte)
            inbuf.open(QtCore.QBuffer.WriteOnly)
            pixmap.save(inbuf, 'png')
            dialog.file = inbyte
            ######################################
            dialog.label_ava.setPixmap(pixmap)

        dialog.pushButton_open.clicked.connect(open_file)
        dialog.pushOk.clicked.connect(reg)
        dialog.pushOk.clicked.connect(dialog.accept)
        dialog.exec()

    def profile(self):
        dialog = uic.loadUi('gui/profile.ui')
        file = self.monitor.client.rep.get_avatar()
        dialog.pixmap = QtGui.QImage.fromData(file)
        dialog.pixmap = QtGui.QPixmap.fromImage(dialog.pixmap)
        dialog.label_ava.resize(150,150)
        dialog.label_ava.setPixmap(dialog.pixmap)

        dialog.comboBox_filter.addItem('Выберите фильтр')
        dialog.comboBox_filter.addItem('Sepia')
        dialog.comboBox_filter.addItem('Black')
        dialog.comboBox_filter.addItem('Negative')


        def open_file():
            fname = QtWidgets.QFileDialog.getOpenFileName(dialog, 'Open file', '/')[0]
            dialog.pixmap = QtGui.QPixmap(fname)
            dialog.label_ava.setPixmap(dialog.pixmap)
            #добавить отправку нового аватара в базу

        def action_filter():
            image = Image.fromqpixmap(dialog.pixmap)
            print(type(image))
            draw = ImageDraw.Draw(image)
            width = image.size[0]
            height = image.size[1]
            pix = image.load()

            if dialog.comboBox_filter.currentText() == 'Black':
                for i in range(width):
                    for j in range(height):
                        a = pix[i,j][0]
                        b = pix[i,j][1]
                        c = pix[i,j][2]
                        s = (a+b+c)
                        draw.point((i,j), (s, s, s))
            if dialog.comboBox_filter.currentText() == 'Sepia':
                for i in range(width):
                    for j in range(height):
                        a = pix[i,j][0]
                        b = pix[i,j][1]
                        c = pix[i,j][2]
                        draw.point([i,j],(255 - a,255 - b,255 - c))
            if dialog.comboBox_filter.currentText() == 'Negative':
                depth = 30
                for i in range(width):
                    for j in range(height):
                        a = pix[i, j][0]
                        b = pix[i, j][1]
                        c = pix[i, j][2]
                        s = (a + b + c)
                        a = s + depth * 2
                        b = s + depth
                        c = s
                        if a > 255: a = 255
                        if b > 255: b = 255
                        if c > 255: c = 255
                        draw.point([i, j], (a, b, c))
            img_tmp = ImageQt(image.convert('RGBA'))
            pixmap = QtGui.QPixmap.fromImage(img_tmp)
            dialog.label_ava.resize(150, 150)
            dialog.label_ava.setPixmap(pixmap)

        dialog.comboBox_filter.currentIndexChanged.connect(action_filter)
        dialog.pushButton_open.clicked.connect(open_file)

        dialog.exec()
        #доделать заполнение окна

class Monitor(QtCore.QObject):

    msg_client = JimMessage()
    msg_server = JimAnswer()
    gotData = QtCore.pyqtSignal(dict)
    gotResp = QtCore.pyqtSignal(dict)
    gotCont = QtCore.pyqtSignal(dict)
    gotChat = QtCore.pyqtSignal(dict)



    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.client = Client('185.189.12.43', 7777)
        self.resv_queue = self.client.recv_queue

    def recv_msg(self):
        while 1:
            data = self.resv_queue.get()
            print(data)
            if 'action' in data and data['action'] == 'msg':
                self.gotData.emit(data)
            elif 'action' in data and data['action'] =='chat':
                self.gotChat.emit(data)
            elif 'response' in data:
                self.gotResp.emit(data)
            elif 'users' in data:
                self.gotCont.emit(data)
            elif 'chats' in data:
                self.gotChat.emit(data)
            self.resv_queue.task_done()






