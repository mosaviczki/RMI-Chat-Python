import sys
from PyQt5 import uic, QtWidgets

app = QtWidgets.QApplication(sys.argv)
login = uic.loadUi("login.ui")
cadastro = uic.loadUi("cadastro.ui")
chat = uic.loadUi("chat.ui")


chat.show()
app.exec_()