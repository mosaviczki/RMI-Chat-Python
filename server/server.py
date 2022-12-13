from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
import threading

class Usuario():

    def __init__(self, nome, senha) -> None:
        self.nome = nome
        self.senha = senha
        self.uri = uri
        print(f"[+] Usuario {nome} criado")

    def set_uri(self, uri):
        self.uri = uri

@expose
class Servidor(object):


    def _carregarUsuarios():
        print("BB")
        with open('users.dat', 'r') as file:
            
            if len(file.read()) == 0: #Não ha nada no arquivo
                return list()
        
            file.seek(0)

            print("FOR")

            for user in file.readlines():
                
                print(user)
                user = user.split(':')
                print(user[0], user[1])
                
                #self.cadastrar_cliente(user[0], user[1])

        return list()   

    usuarios = _carregarUsuarios()
    print(usuarios)

    def cadastrar_usuario(self, nome, senha):
        usuario = Usuario(nome, senha)
        usuario.set_uri(daemon.register(usuario))

        Servidor.usuarios.append(usuario)

    def show_users(self, users = usuarios):
        print('--------------------USERS-----------------------')
        for user in users:
            print('-------------------------------------------')
            print(user.nome)
            print(user.senha)
            print(user.uri)

    def login(self, nome, senha, users = usuarios):
        for user in users:
            if nome == user.nome and senha == user.senha:
                return True
        return False


with Daemon() as daemon:
    print("[+] Starting server")
    ns = locateNS()
    server = Servidor()
    uri = daemon.register(server)
    ns.register("RMI", uri)

    print(uri)

    daemon.requestLoop()
    