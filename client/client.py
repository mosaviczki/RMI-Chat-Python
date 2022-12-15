import threading, time, sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QListWidget, QListWidgetItem
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

    def get_uriUser(self):
        return self.uriUser

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

                    print(cliente.get_uriUser())

                    if cliente.get_uriUser() == None:
                        QMessageBox.about(self, "Error", "Usuario ou senha inválida!")
                    else:
                        telaChat = Chatbox(nome, cliente)
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
                def __init__(self, nome, cliente):
                    super(Chatbox,self).__init__()
                    self.nome = nome
                    self.client = cliente 
                    loadUi("../view/chat.ui",self)
                    self.user.setText(nome)
                    self.listarUser()
                    #self.pushButton.clicked.connect(self.message)
                    self.pushButton_2.clicked.connect(self.logOut)
                    #self.buttonArq.clicked.connect(self.enviaArquivo)

                def listarUser(self):
                    lista = []
                    for users in server.showUser():
                        if users != self.nome:
                            if users != None:
                                lista.append(users)
                    for u in lista:
                        usuario = self.listWidget.addItem(u)

                    self.listWidget.itemClicked.connect(self.getItem)

                def getItem(self, itm):
                    para = itm.text()
                    self.carregaMensagem(para)
                    self.message(para)

                def carregaMensagem(self, usuario_dest):
                    user = Proxy(self.client.uriUser)

                    print(self.nome, usuario_dest)

                    aux = [self.nome, usuario_dest]
                    aux.sort()
                    aux = aux[0] + aux[1]

                    aux = md5(aux.encode())
                    aux = aux.hexdigest()

                    for arq in user.get_mensagens():
                        msgs = server.carregarMensagens(aux + '.log')
                        for x in range(len(msgs)):
                            self.chatBox.append(msgs[x])
                        

                def message(self, usuario_dest):
                    msg = self.lineEdit.text()
                    self.chatBox.append(self.nome + ": " + msg)
                    callback = self.client
                    server.mandarMensagem(callback.uri, usuario_dest, msg)

                            
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

        """
        if option == 3:
                
                callback = cliente
                para = input("Digite para quem vai a msg: ")
                msg = input('Digite a msg: ')
                
                server.mandarMensagem(callback.uri, para, msg)

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

                nomeFile = input("Nome do arquivo: ")

                arq = open(nomeFile, 'rb')

                arqNome = arq.name
                arqBuffer = arq.read()

                callback = cliente
                server.enviarArquivo(callback.uri, arqNome, arqBuffer)

            if option == 7:

                nome = input('Informe o nome do grupo: ')

                callback = cliente
                server.criaGrupo(callback.uri, ['Maycom', 'Luis'], nome)

            if option == 8:
                
                callback = cliente
                server.addNovoUsuarioGrupo(callback.uri, 'UTF')
            

            if option == 9:
                print(server.showUser())
        """
    