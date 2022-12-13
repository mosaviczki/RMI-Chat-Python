from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
import threading


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

    def show_users(self, users = usuarios):
        for user in users:
            print(user.nome, user.senha)


with Daemon() as daemon:
    print("Starting server")
    ns = locateNS()
    server = Servidor()
    uri = daemon.register(server)
    ns.register("RMI", uri)

    print(uri)

    daemon.requestLoop()
    