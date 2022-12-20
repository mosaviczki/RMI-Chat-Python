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

        cliente = None
        user = None

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
                
            ############ CADASTRO DE NOVO USUARIO ############
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
                    self.cliente = cliente 
                    loadUi("../view/chat.ui",self)
                    self.user.setText(nome)
                    self.listarUser()
                    self.grupos()
                    self.pushButton_2.clicked.connect(self.logOut)
                    self.buttonGroup.clicked.connect(self.carregaTelaGrupo)
                
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
                    usuarioDest = itm.text()
                    self.carregaMensagem(usuarioDest)
                    self.message(usuarioDest)
                    
                    
                def carregaMensagem(self, usuarioDest):
                    user = Proxy(self.cliente.uriUser)
                    if usuarioDest is not False:
                        self.usuarioDest = usuarioDest
                        aux = [self.nome, self.usuarioDest]
                        aux.sort()
                        aux = aux[0] + aux[1]
                        aux = md5(aux.encode())
                        aux = aux.hexdigest()
                        aux = aux + '.log'
                        existe = os.path.exists('../server/{}'.format(aux))
                        print(existe)
                        if existe == True:
                            for arq in user.get_mensagens():
                                self.chatBox.setText('')
                                msgs = server.carregarMensagens(aux)
                                if msgs:
                                    for x in range(len(msgs)):          
                                        self.chatBox.append(msgs[x])
                
                def carregaMsgGrupo(self, usuarioDest):
                    user = Proxy(self.cliente.uriUser)
                    if usuarioDest is not False:
                        self.usuarioDest = usuarioDest
                        existe = os.path.exists('../server/{}'.format(self.usuarioDest))
                        if existe == True:
                            for arq in user.get_mensagens():
                                self.chatBox.setText('')
                                msgs = server.carregarMensagens(self.usuarioDest)
                                if msgs:
                                    for x in range(len(msgs)):          
                                        self.chatBox.append(msgs[x])
            
                def grupos(self):
                    callback = self.cliente
                    grupos = server.meusGrupos(callback.uri)
                    for id in grupos:
                        grp = id.split(":")
                        self.listWidget_2.addItem(grp[0])
                    self.listWidget_2.itemClicked.connect(self.getItemGroup)
                
                def verifica(self, nomeGrupo):
                    arq = open("../server/groups.dat", "r")
                    for i in arq:
                        if nomeGrupo in i:
                            lista = i.split("|")
                            self.carregaMsgGrupo(lista[1])
                        else:
                            pass

                def getItemGroup(self, itm):
                    grupo = itm.text()
                    #self.carregaMensagem(usuarioDest)
                    self.verifica(grupo)
                    self.messageGroup(grupo)

                def message(self, usuarioDest):
                    msg = self.lineEdit.text()
                    
                    callback = self.cliente
                    if msg:
                        print("MSG1: ",msg)
                        self.chatBox.append(self.nome +": "+msg)
                        server.mandarMensagem(callback.uri, usuarioDest, msg)
                
                def messageGroup(self, grupo):
                    msg = self.lineEdit.text()
                    callback = self.cliente
                    if msg:
                        print(msg)
                        self.chatBox.append(self.nome +": "+msg)
                        server.mandarMensagem(callback.uri, grupo, msg)
                        if msg == "/delete":
                            server.excluirGrupo(callback.uri, grupo)
                            QMessageBox.about(self, "Sucess", "Grupo excluido com sucessoo!")
                        if "/ban" in msg:
                            msgUser = msg.split(' ')
                            user = msgUser[1]
                            server.excluirUsuario(user, grupo)
                            QMessageBox.about(self, "Sucess", "{} excluido com sucesso do grupo {}".format(user, grupo))      
                        #if "/add" in msg:
                        #    msgUser = msg.split(' ')
                        #    user = msgUser[1]
                        #    server.excluirUsuario(user, grupo)


                def carregaTelaGrupo(self):
                    group= Group(self.nome, self.cliente)
                    widget.addWidget(group)
                    widget.setCurrentIndex(widget.currentIndex()+1)

                def logOut(self):
                    login = Login()
                    widget.addWidget(login)
                    widget.setCurrentIndex(widget.currentIndex()+1)

            class Group(QDialog):
                def __init__(self, nome, cliente):
                    super(Group,self).__init__()
                    self.nome = nome
                    self.cliente = cliente 
                    widget.setFixedWidth(570)
                    widget.setFixedHeight(406)
                    loadUi("../view/grupo.ui",self)
                    self.pushButton.clicked.connect(self.createGroup)

                def createGroup(self):
                    nomeGrupo = self.lineEdit.text()
                    nUsuario = self.lineEdit_2.text()
                    listaUsuario = nUsuario.split(',')
                    callback = self.cliente
                    server.criaGrupo(callback.uri, listaUsuario, nomeGrupo)
                
                def voltar(self):
                    chat = Chatbox()
                    widget.addWidget(chat(self.nome,self.cliente))
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
            print("--------------------------------")
            print("1-Login")
            print('2-Registrar')
            print('3-Mandar mesagem')
            print('4-Cria Grupo')
            print('5-Add no grupo')
            print('6-ban usuario')
            print('7-Sair do grupo')
            print('8-Excluir Grupo')
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
            
            if option == 2:

                nome = input("Digite seu nome: ")
                senha = input("Digite sua senha: ")

                senha = md5(senha.encode())
                senha = senha.hexdigest()   #Transformando em string 

                server.cadastrar_usuario(nome, senha)

            if option == 3:
                
                para = input("Digite para quem vai a msg: ")
                msg = input('Digite a msg: ')
                
                server.mandarMensagem(user, para, msg)

            if option == 4:
                nome = input("Digite o nome do Grupo: ")
                server.criaGrupo(user, False, [], nome)

            if option == 5:
                nome_grupo = input("Digite o nome do Grupo: ")
                nome = input("Digite o nome que vai add: ")
                server.addNoGrupo(user, nome, nome_grupo)

            if option == 6:
                nome_grupo = input("Digite o nome do Grupo: ")
                nome = input("Digite o nome que vai ban: ")
                server.banDoGrupo(user, nome, nome_grupo)

            if option == 7:
                nome_grupo = input("Digite o nome do Grupo: ")
                server.sairDoGrupo(user, nome_grupo)

            if option == 8:
                nome_grupo = input("Digite o nome do Grupo: ")
                server.excluirGrupo(user, nome_grupo)

            if option == 10:
                server.printAllUsers()

            if option == 11:
                server.printAllGroup()
                """