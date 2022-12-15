import threading, time, sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from hashlib import md5

@expose
class Cliente(object):
    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha
        self.uri = None
        self.uriUser = None

    def get_nome(self):
        return self.nome

    def get_senha(self):
        return self.senha
    
    def get_uri(self):
        return self.uri

    def set_uriUser(self, uri):
        self.uriUser = uri

    def request_loop(self, daemon):
        daemon.requestLoop()
        time.sleep(2)
    @oneway
    def notificar(self, msg):
        print(msg)

    def show(self):
        print("Nome: ", self.nome)
        print("Senha: ", self.senha)
        print("Uri: ", self.uri)
        print("UriUSer: ", self.uriUser)

with Daemon() as daemon:
        
    with Proxy("PYRONAME:RMI") as server:

        cliente = None

        while True: 
            class Login(QDialog):
                def __init__(self):
                    super(Login, self).__init__()
                    loadUi("../view/login.ui", self)
                    self.buttonEntrar.clicked.connect(self.logIn)
                    self.pushButton_2.clicked.connect(self.cadastrarClient)

                def logIn(self): #Efetua o login
                    nome = self.lineEdit.text()
                    senha = self.lineEdit_2.text()
                    
                    senha = md5(senha.encode())
                    senha = senha.hexdigest()

                    cliente = Cliente(nome, senha)

                    callback = cliente
                    callback.uri = daemon.register(callback)

                    loop_thread = threading.Thread(target=callback.request_loop, args=(daemon, ))
                    loop_thread.daemon = False
                    loop_thread.start()

                    server.login(callback.uri)

                    if cliente.uriUser == None:
                        QMessageBox.about(self, "Error", "Senha incorreta!")
                        
                    else:
                        telaChat = Chatbox()
                        widget.addWidget(telaChat)
                        widget.setCurrentIndex(widget.currentIndex()+1)
                    

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
                        senha = senha.hexdigest()   #Transformando em string 

                        server.cadastrar_usuario(nome, senha)
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
                    #self.pushButton.clicked.connect(self.message)
                    #self.pushButton_2.clicked.connect(self.LogOut)

                #def message(self):
                #    self.chatBox.setText(self.lineEdit.text())
                            
                #def logOut(self):
                #    login = Login()
                #    widget.addWidget(login)
                #    widget.setCurrentIndex(widget.currentIndex()+1)

            app=QApplication(sys.argv)
            mainwindow=Login()
            widget=QtWidgets.QStackedWidget()
            widget.addWidget(mainwindow)
            widget.setFixedWidth(1900)
            widget.setFixedHeight(1024)
            widget.show()
            app.exec_()

        """
            print("--------------------------------")
            print("1-Login\n2-Registrar\n3-Mandar mesagem\n4-Mostrar Cliente\n5-Carregar mensagens")
            option = int(input(""))
            
            if option == 1:

                nome = input("Nome: ")
                senha = input("Senha: ")

                senha = md5(senha.encode())
                senha = senha.hexdigest()

                cliente = Cliente(nome, senha)

                callback = cliente
                callback.uri = daemon.register(callback)

                loop_thread = threading.Thread(target=callback.request_loop, args=(daemon, ))
                loop_thread.daemon = False
                loop_thread.start()

                server.login(callback.uri)

                if cliente.uriUser == None:
                    print('[-] Senha incorreta')
                    
                else:
                    print('[+] Logado!')

                    user = Proxy(cliente.uriUser)

                    cnv = user.get_mensagens()
                    print(cnv)
            
            if option == 2:

                nome = input("Digite seu nome: ")
                senha = input("Digite sua senha: ")

                senha = md5(senha.encode())
                senha = senha.hexdigest()   #Transformando em string 

                server.cadastrar_usuario(nome, senha)

            if option == 3:
                
                de = input("Digite seu nome: ")
                para = input("Digite para quem vai a msg: ")
                msg = input('Digite a msg: ')
                
                server.mandarMensagem(de, para, msg)

            if option  == 4:
                if cliente == None:
                    print("Cliente não logado!")
                else:
                    cliente.show()    

            if option == 5:       

                user = Proxy(cliente.uriUser)
                for arq in user.get_mensagens():
                    msgs = server.carregarMensagens(arq)
                    print(msgs)

            if option == 6:
                server.show_users()
        """
    