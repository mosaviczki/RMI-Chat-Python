import threading, time, sys, os
from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
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

        #while True: 
            global cliente
            global user
            class Login(QDialog):
                def __init__(self): #Carrega a tela de login
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
                        QMessageBox.about(self, "Error", "Usuario ou senha inválida!")
                        
                    else:
                        user = Proxy(cliente.uriUser)
                        telaChat = Chatbox(nome, user)
                        widget.addWidget(telaChat)
                        widget.setCurrentIndex(widget.currentIndex()+1)
                        
                def cadastrarClient(self): #Direcionara para o cadastro
                    createClient = Cadastrar()
                    widget.addWidget(createClient)
                    widget.setCurrentIndex(widget.currentIndex()+1)
                
            ############ CADASTRO DE NOVO USUARIO ############
            class Cadastrar(QDialog):
                def __init__(self):#Carrega a tela de cadastro
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
                        print(nome, senha)
                        server.cadastrar_usuario(nome, senha)
                        QMessageBox.about(self, "Sucess", "Cliente cadastrado com sucesso!")                   
                    else:
                        QMessageBox.about(self, "Error", "As senhas devem ser iguais!")              
                
                def voltar(self):#Volta para pagina de login
                    login = Login()
                    widget.addWidget(login)
                    widget.setCurrentIndex(widget.currentIndex()+1)
                        
            ############ CHAT DO USUARIO ############
            class Chatbox(QDialog):
                def __init__(self, nome, user):#Carrega tela do chat
                    super(Chatbox,self).__init__()
                    self.nome = nome
                    self.user = user
                    loadUi("../view/chat.ui",self)
                    widget.setFixedWidth(1900)
                    widget.setFixedHeight(1024)
                    self.listarConversa(self.user.get_p2p())
                    self.listarMeusGrupos(self.user.get_grupos())
                    self.listarUsuario()
                    self.listarGrupo()
                    self.userLabel.setText(self.nome)
                    self.pushButton.clicked.connect(self.logOut)
                    self.buttonGroup.clicked.connect(self.carregaTelaGrupo)
                
                def listarConversa(self, p2p):
                    lista = []
                    for users in p2p:
                        self.listWidget.addItem(users)      

                def listarMeusGrupos(self, grupo):
                    lista = []
                    for grp in grupo:
                        self.listWidget_2.addItem(grp)

                def listarUsuario(self):
                    for aux in server.showUsers():
                        self.listWidget_3.addItem(aux)
                    self.listWidget.itemClicked.connect(self.getItemU)
                
                def listarGrupo(self):
                    for aux in server.showGroups():
                        self.listWidget_4.addItem(aux)
                    self.listWidget.itemClicked.connect(self.getItemG)

                def getItemU(self, itm):
                    userDest = itm.text()
                    self.mandarMensagem(userDest)
                
                def getItemG(self, itm):
                    grupo = itm.text()
                    self.mandarMensagemGrupo(grupo)

                #def carregarMsgP2P(slef):
                #def carregarMsgGrupo(slef):     

                def mandarMensagem(self, dest):
                    msg = self.lineEdit.text()
                    if msg:
                        self.chatBox.append(self.nome +": "+msg)
                        server.mandarMensagem(self.user, dest, msg)
                
                def mandarMensagemGrupo(self, grupo):
                    msg = self.lineEdit.text()
                    if msg:
                        self.chatBox.append(self.nome +": "+msg)
                        server.mandarMensagem(self.user, grupo, msg)
                        if msg == "/deleteGroup":
                            server.excluirGrupo(self.user, grupo)
                            QMessageBox.about(self, "Sucess", "Grupo {} deletado!".format(grupo))
                        if "/add" in msg:
                            msgUser = msg.split(' ')
                            userAdd = msgUser[1]
                            server.addNoGrupo(self.user, userAdd, grupo)
                        if "/ban" in msg:
                            msgUser = msg.split(' ')
                            userBan = msgUser[1]
                            server.banDoGrupo(self.user, userBan, grupo)
                            QMessageBox.about(self, "Sucess", "{} excluido com sucesso do grupo {}".format(user, grupo))
                        if msg == "/sair":
                            server.sairDoGrupo(self.user,grupo)
                            QMessageBox.about(self, "Sucess", "Você saiu do grupo {}".format(grupo))

                def carregaTelaGrupo(self):
                    group= Group(self.nome, self.user)
                    widget.addWidget(group)
                    widget.setCurrentIndex(widget.currentIndex()+1)

                def logOut(self):
                    login = Login()
                    widget.addWidget(login)
                    widget.setCurrentIndex(widget.currentIndex()+1)
                
            class Group(QDialog):
                def __init__(self, nome, user):
                    super(Group,self).__init__()
                    self.nome = nome
                    self.user = user
                    widget.setFixedWidth(580)
                    widget.setFixedHeight(490)
                    loadUi("../view/grupo.ui",self)
                    self.pushButton.clicked.connect(self.createGroup)
                    self.pushButton_2.clicked.connect(self.voltar)

                def createGroup(self):
                    nomeGrupo = self.lineEdit.text()
                    nUsuario = self.lineEdit_2.text()
                    listaUsuario = nUsuario.split(',')
                    if self.radioButton.isChecked():
                        server.criaGrupo(self.user, True, listaUsuario, nomeGrupo)
                        QMessageBox.about(self, "Sucess", "Grupo criado com sucesso!") 
                    elif self.radioButton_2.isChecked():
                        server.criaGrupo(self.user, False, listaUsuario, nomeGrupo)
                        QMessageBox.about(self, "Sucess", "Grupo criado com sucesso!")  
                    else:
                        QMessageBox.about(self, "Error", "Deve selecionar 1 opção!") 

                def voltar(self):
                    chat = Chatbox(self.nome,self.user)
                    widget.addWidget(chat)
                    widget.setCurrentIndex(widget.currentIndex()+1)
                
            ############# INICIALIZAÇÃO DAS VIEWS #############
            app=QApplication(sys.argv)
            mainwindow=Login()
            widget=QtWidgets.QStackedWidget()
            widget.addWidget(mainwindow)
            widget.setFixedWidth(1900)
            widget.setFixedHeight(1024)
            widget.show()
            app.exec_()



