import sys, Pyro4
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
from hashlib import sha256


class Login(QDialog):
    def __init__(self):
        super(Login,self).__init__()
        loadUi("../view/login.ui",self)
        self.pushButton.clicked.connect(self.logIn) 
        self.pushButton_2.clicked.connect(self.cadastrarClient)

    def logIn(self): #Efetua o login
        nome = self.lineEdit.text()
        senha = self.lineEdit_2.text()

    def cadastrarClient(self): #Direcionara para o cadastro
        createClient=Cadastrar()
        widget.addWidget(createClient)
        widget.setCurrentIndex(widget.currentIndex()+1)

class Cadastrar(QDialog):
    def __init__(self):
        super(Cadastrar,self).__init__()
        loadUi("../view/cadastro.ui",self)
        self.pushButton.clicked.connect(self.createClientFunction)
        self.pushButton_2.clicked.connect(self.voltar)


    def createClientFunction(self): #Irá efetuar o cadastro
        nome = self.lineEdit.text()
        if self.lineEdit_2.text() == self.lineEdit_3.text():
            senha = self.lineEdit_2.text()
            QMessageBox.about(self, "Sucess", "Cliente cadastrado com sucesso!")
        else:
            QMessageBox.about(self, "Error", "As senhas devem ser iguais!")

    
    def voltar(self):
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
        

if __name__ == "__main__":
    app=QApplication(sys.argv)
    mainwindow=Login()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setFixedWidth(1900)
    widget.setFixedHeight(1024)
    widget.show()
    app.exec_()