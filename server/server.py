from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
import threading


f = open("users.txt", "w")

class Usuario():

    def __init__(self, nome, senha, uri) -> None:
        self.nome = nome
        self.senha = senha
        self.uri = uri
        print(f"Usuario {nome} criado")

@expose
class Servidor(object):
    usuarios = []

    def cadastrar_cliente(self, callback):
        cliente = Proxy(callback)
        usuario = Usuario(cliente.get_nome(), cliente.get_senha(),callback)
        Servidor.usuarios.append(usuario)
        f.write(usuario.nome + ":" + usuario.senha)

    def show_users(self, users = usuarios):
        for user in users:
            print(user.nome, user.senha)

    def login(self, nome, senha, users = usuarios):
        for user in users:
            if nome == user.nome and senha == user.senha:
                return dict()
        return False


with Daemon() as daemon:
    print("Starting server")
    ns = locateNS()
    server = Servidor()
    uri = daemon.register(server)
    ns.register("RMI", uri)

    print(uri)

    daemon.requestLoop()
    