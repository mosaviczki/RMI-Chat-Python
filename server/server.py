from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from serpent import tobytes
from datetime import datetime
from hashlib import md5
from os import mkdir, remove
import threading

daemon = Daemon()

@expose
class Usuario():

    def __init__(self, nome, senha) -> None:
        self.uri = None
        self.nome = nome
        self.senha = senha
        self.p2p = dict()
        self.grupos = dict()


    def set_uri(self, uri):
        self.uri = uri
    
    def get_uri(self):
        return self.uri

    def get_nome(self):
        return self.nome

    def get_senha(self):
        return self.senha
    
    def set_p2p(self, p2p):
        self.p2p = p2p

    def get_p2p(self):
        return self.p2p

    def set_grupos(self, grupos):
        self.grupos = grupos

    def get_grupos(self):
        return self.grupos

    def hello(self):
        return "hello"

@expose
class Grupo():
    def __init__(self, nome):
        self.nome = nome
        self.uri = None
        self.adm = None
        self.membros = set()
        self.dir = None

    def set_membros(self, user):
        self.membros.add(user)

    def update_membros(self, membros):
        self.membros = membros

    def set_uri(self, uri):
        self.uri = uri

    def set_adm(self, user):
        self.adm = user

    def set_dir(self, dir):
        self.dir = dir

    def get_nome(self):
        return self.nome
        
    def get_dir(self):
        return self.dir

    def get_adm(self):
        return self.adm

    def get_membros(self):
        return self.membros
    
@expose
class Servidor(object):
    
    usuarios = []
    grupos = []

    def cadastrar_usuario(self, nome, senha):

        usuario = Usuario(nome, senha)
        uri = daemon.register(usuario)
        usuario.set_uri(uri)
        
        self.usuarios.append(usuario)

    def login(self, callback):

        cliente = Proxy(callback)

        nome = cliente.get_nome()
        senha = cliente.get_senha()
        
        for user in self.usuarios:
            user.senha = user.senha.replace('\n', '')

            if nome == user.nome and senha == user.senha:
                cliente.set_uriUser(user.uri)

    def printAllUsers(self):
        for user in self.usuarios:
            self.printUsuario(user)
    
    def printUsuario(self, usuario):
        print('-------------------------')
        print('URI: ', usuario.get_uri())
        print('Nome: ', usuario.get_nome())
        print('Senha: ', usuario.get_senha())
        print('P2P: ', usuario.get_p2p())
        print('GRUPOS: ', usuario.get_grupos())
    
print("[+] Starting server")
ns = locateNS()
server = Servidor()
uri = daemon.register(server)
ns.register("RMI", uri)

print(uri)

daemon.requestLoop()
    