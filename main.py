import sys, Pyro5
from PyQt5 import uic, QtWidgets
from hashlib import sha256
# senha = 
# hash = sha256(senha.encode())
# senha_hash = hash.digest()

def confereSenha(passaword, confPassword):
    if passaword == confPassword:
        return
    else:
        print("As duas senhas devem ser iguais")

def cadastrar():
    cadastro.show()
    cadastro.pushButton_2.clicked.connect(voltar)

def voltar():
    cadastro.close()
    chat.close()

def entrar():
    chat.show()
    chat.pushButton_2.clicked.connect(voltar)

app = QtWidgets.QApplication(sys.argv)
login = uic.loadUi("login.ui")
cadastro = uic.loadUi("cadastro.ui")
chat = uic.loadUi("chat.ui")


login.pushButton.clicked.connect(entrar)
login.pushButton_2.clicked.connect(cadastrar)

#login.lineEdit.text()
#login.lineEdit_2.text()



login.show()
app.exec_()