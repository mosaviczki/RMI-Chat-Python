import sys
from PyQt5 import uic, QtWidgets

def confereSenha(passaword, confPassword):
    if passaword == confPassword:
        return
    else:
        print("As duas senhas devem ser iguais")

def cadastrar():
    cadastro.show()
    cadastro.pushButton.clicked.connect(voltar)

def voltar():
    cadastro.close()

def entrar():
    chat.show()

app = QtWidgets.QApplication(sys.argv)
login = uic.loadUi("login.ui")
cadastro = uic.loadUi("cadastro.ui")
chat = uic.loadUi("chat.ui")

login.pushButton.clicked.connect(cadastrar)
login.pushButton_2.clicked.connect(entrar)



login.show()
app.exec_()