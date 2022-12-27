from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
from hashlib import md5
# senha =
# hash = sha256(senha.encode())
# senha_hash = hash.digest()


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("../view/login.ui", self)
        self.pushButton.clicked.connect(self.logIn)
        self.pushButton_2.clicked.connect(self.cadastrarClient)

    def logIn(self): #Efetua o login
        nome = self.lineEdit.text()
        senha = self.lineEdit_2.text()

    def cadastrarClient(self): #Direcionara para o cadastro
        createClient = Cadastrar()
        widget.addWidget(createClient)
        widget.setCurrentIndex(widget.currentIndex()+1)
        #server.show_users()
                    
                
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
            senha = md5(senha.encode())

            senha = senha.hexdigest()

            callback = Cliente(nome, senha)
            callback.uri = daemon.register(callback)

            loop_thread = threading.Thread(target=callback.request_loop, args=(daemon, ))
            loop_thread.daemon = False
            loop_thread.start()

            server.cadastrar_cliente(callback.uri)
            QMessageBox.about(self, "Sucess", "Cliente cadastrado com sucesso!")
                        
        else:
            QMessageBox.about(self, "Error", "As senhas devem ser iguais!")

                
    
    def voltar(self):
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
            

class Chatbox(QDialog):
    def __init__(self):
        super(Chatbox,self).__init__()
        loadUi("../view/chat.ui",self)
        self.pushButton.clicked.connect(self.message)
        self.pushButton_2.clicked.connect(self.LogOut)

    def message(self):
        self.chatBox.setText(self.lineEdit.text())
                
    def logOut(self):
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

app=QApplication(sys.argv)
mainwindow=Login()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(1900)
widget.setFixedHeight(1024)
widget.show()
app.exec_()
