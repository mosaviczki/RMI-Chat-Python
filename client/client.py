from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from hashlib import md5
import threading, time
from PyQt5 import uic, QtWidgets
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

def showP2P(p2p):
    print('P2P')

    for user in p2p:
        layout.listWidget.addItem(user)

def showMeusGrupos(grupos):
    print('MeusGrupo')

    for user in grupos:
        layout.listWidget_2.addItem(user)

def showUsuarios():
    print('All User')
    for aux in server.showUsers():
        layout.listWidget_3.addItem(aux)

def showGrupos():
    print('All Grupos')
    for aux in server.showGroups():
        layout.listWidget_4.addItem(aux)

def carregarConversaP2P():
    usuarioDest = layout.listWidget.currentItem().text()

    print(usuarioDest)
    layout.label_6.setText(usuarioDest)

    aux_dict = user.get_p2p()

    linhas = server.carregarMensagem(aux_dict[usuarioDest])

    layout.listWidget_5.clear()

    for linha in linhas:
        layout.listWidget_5.addItem(linha)

def carregarConversaGrupo():
    usuarioDest = layout.listWidget_2.currentItem().text()

    print(usuarioDest)
    layout.label_6.setText(usuarioDest)

    aux_dict = user.get_grupos()

    linhas = server.carregarMensagem(aux_dict[usuarioDest])

    layout.listWidget_5.clear()

    for linha in linhas:
        layout.listWidget_5.addItem(linha)

def mandarMensagem():
    usuarioDest = layout.label_6.text()
    print(usuarioDest)

    msg = layout.lineEdit.text()
    print(msg)

    server.mandarMensagem(user, usuarioDest, msg)
    
    layout.lineEdit.setText('')

with Daemon() as daemon:
        
    with Proxy("PYRONAME:RMI") as server:

        global cliente
        global user

        app = QtWidgets.QApplication([])
        layout = uic.loadUi('main.ui')

        #server.printAllUsers()

        #while True: 
        print("--------------------------------")
        print("1-Login")
        '''
        print('2-Registrar')
        print('3-Mandar mesagem')
        print('4-Cria Grupo')
        print('5-Add no grupo')
        print('6-ban usuario')
        print('7-Sair do grupo')
        print('8-Excluir Grupo')
            #option = int(input(""))
            
            #if option == 1:
        '''
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

            layout.label.setText('Olá, ' + user.get_nome())

            showP2P(user.get_p2p())
            showMeusGrupos(user.get_grupos())
            showUsuarios()
            showGrupos()

            print(user)

            
            layout.listWidget.itemClicked.connect(carregarConversaP2P)
            layout.listWidget_2.itemClicked.connect(carregarConversaGrupo)
            layout.pushButton.clicked.connect(mandarMensagem)


            layout.show()
            app.exec()

            server.logout(cliente.get_uri())

        
        '''
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
            '''
            
