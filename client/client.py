import threading, time, sys, os
from threading import Thread
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

        while True: 
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
                        telaChat = Chatbox(nome, user, cliente)
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
                def __init__(self, nome, user,cliente):#Carrega tela do chat
                    super(Chatbox,self).__init__()
                    self.nome = nome
                    self.user = user
                    self.cliente = cliente
                    loadUi("../view/chat.ui",self)
                    widget.setFixedWidth(1900)
                    widget.setFixedHeight(1024)
                    self.listarConversa()
                    self.listarMeusGrupos()
                    self.listarUsuarioOnline()
                    self.listarUsuarioOffline()
                    self.listarGrupo()
                    self.userLabel.setText(self.nome)
                    self.pushButton.clicked.connect(self.logOut)
                    self.pushButton_2.clicked.connect(self.mandarMensagem)

                    self.buttonGroup.clicked.connect(self.carregaTelaGrupo)
                
                def listarConversa(self):
                    for users in self.user.get_p2p():
                        self.listWidget.addItem(users) 
                    self.listWidget.itemClicked.connect(self.setLabel)
                    self.listWidget.itemClicked.connect(self.carregarMsgP2P)     

                def listarMeusGrupos(self):
                    for grp in self.user.get_grupos():
                        self.listWidget_2.addItem(grp)
                    self.listWidget_2.itemClicked.connect(self.setLabel)
                    self.listWidget_2.itemClicked.connect(self.carregarMsgGrupo)

                def listarUsuarioOnline(self):
                    lista = []
                    for users in server.showOnline():
                        if users != self.nome and users != None:
                            lista.append(users)
                    for us in lista:
                        self.listWidget_3.addItem(us)

                    self.listWidget_3.itemClicked.connect(self.limpaTela)
                    self.listWidget_3.itemClicked.connect(self.setLabel)

                def listarUsuarioOffline(self):
                    for users in server.showOffline():
                        self.listWidget_4.addItem(users)
                    self.listWidget_4.itemClicked.connect(self.limpaTela)
                    self.listWidget_4.itemClicked.connect(self.setLabel)
                
                def listarGrupo(self):
                    for aux in server.showGroups():
                        self.listWidget_5.addItem(aux)
                    self.listWidget_5.itemClicked.connect(self.setLabel)

                def setLabel(self, itm):
                    dest = itm.text()
                    self.label.setText(dest)

                def limpaTela(self):
                   self.chatBox.setText('')

                def carregarMsgP2P(self , itm):
                    usuarioDest = self.label.text()
                    if usuarioDest is not False:
                        aux_dict = self.user.get_p2p()
                        existe = os.path.exists('../server/{}'.format(aux_dict[usuarioDest]))
                        if existe:
                            self.chatBox.setText('')
                            for arq in server.carregarMensagem(aux_dict[usuarioDest]):
                                if arq:
                                    arq = arq.replace('\n', '')
                                    arq = arq.split("|")
                                    data = arq[0]
                                    nome = arq[1]
                                    msg = arq[2]
                                    text = '[' + data + '] ' + nome + ': ' + msg 
                                    self.chatBox.append(text) 

                def carregarMsgGrupo(self): 
                    grupo = self.label.text()
                    if grupo is not False:
                        aux_dict = self.user.get_grupos()
                        existe = os.path.exists('../server/{}'.format(aux_dict[grupo]))
                        if existe:
                            self.chatBox.setText('')
                            for arq in server.carregarMensagem(aux_dict[grupo]):
                                if arq:
                                    arq = arq.replace('\n', '')
                                    arq = arq.split("|")
                                    data = arq[0]
                                    nome = arq[1]
                                    msg = arq[2]
                                    text = '[' + data + '] ' + nome + ': ' + msg 
                                    self.chatBox.append(text) 

                def mandarMensagem(self, dest):
                    dest = self.label.text()
                    msg = self.lineEdit.text()
                    if msg:
                        server.mandarMensagem(self.user, dest, msg)
                        if msg == "/deleteGroup":
                            server.excluirGrupo(self.user, dest)
                            QMessageBox.about(self, "Sucess", "Grupo {} deletado!".format(dest))
                        if "/add" in msg:
                            msgUser = msg.split(' ')
                            if len(msgUser) > 1:
                                print(len(msgUser))
                                userAdd = msgUser[1]
                                server.addNoGrupo(self.user, userAdd, dest)
                                QMessageBox.about(self, "Sucess", "{} adicionado no grupo {}".format(userAdd,dest))
                            else:
                                QMessageBox.about(self, "attention", "Informe o nome de 1 usuario")
                        if "/ban" in msg:
                            if len(msgUser) > 1:
                                msgUser = msg.split(' ')
                                userBan = msgUser[1]
                                server.banDoGrupo(self.user, userBan, dest)
                                QMessageBox.about(self, "Sucess", "{} excluido com sucesso do grupo {}".format(userBan, dest))
                            else:
                                QMessageBox.about(self, "attention", "Informe o nome de 1 usuario")
                        if msg == "/sair":
                            server.sairDoGrupo(self.user,dest)
                            QMessageBox.about(self, "Sucess", "Você saiu do grupo {}".format(dest))
                        self.lineEdit.setText('')

                def carregaTelaGrupo(self):
                    group= Group(self.nome, self.user, self.cliente)
                    widget.addWidget(group)
                    widget.setCurrentIndex(widget.currentIndex()+1)

                def logOut(self):
                    server.logout(self.cliente.get_uri())
                    login = Login()
                    widget.addWidget(login)
                    widget.setCurrentIndex(widget.currentIndex()+1)
                
            class Group(QDialog):
                def __init__(self, nome, user, cliente):
                    super(Group,self).__init__()
                    self.nome = nome
                    self.user = user
                    self.cliente = cliente
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
                    chat = Chatbox(self.nome,self.user, self.cliente)
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
            

            



