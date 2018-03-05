
import sys
from PyQt5 import Qt
from gui import MyWindow

app = Qt.QApplication(sys.argv)

wnd = MyWindow()
wnd.show()

sys.exit(app.exec())