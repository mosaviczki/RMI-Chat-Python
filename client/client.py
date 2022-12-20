from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from hashlib import md5
import threading, time
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
            print("--------------------------------")
            print("1-Login")
            print('2-Registrar')
            print('3-Mandar mesagem')
            print('4-Cria Grupo')
            print('5-Add no grupo')
            print('6-ban usuario')
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
                server.criaGrupo(user, True, [], nome)

            if option == 5:
                nome_grupo = input("Digite o nome do Grupo: ")
                nome = input("Digite o nome que vai add: ")
                server.addNoGrupo(user, nome, nome_grupo)

            if option == 6:
                nome_grupo = input("Digite o nome do Grupo: ")
                nome = input("Digite o nome que vai ban: ")
                server.banDoGrupo(user, nome, nome_grupo)

            if option == 10:
                server.printAllUsers()

            if option == 11:
                server.printAllGroup()