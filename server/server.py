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

    def update_p2p(self, key, log):
        self.p2p[key] = log

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
        ######### Verificacao ######### 
        for user in self.usuarios:
            if nome == user.get_nome(): #Ja esta cadastrado este usuario
                return None

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


    def mandarMensagem(self, usuario_manda, nome_recebe, mensagem):
        usuario_recebe = self.procuraUsuario(nome_recebe)

        if usuario_recebe == None:  # O Usuario de destino nao existe
            return None
        
        horario = datetime.now()
        horario_str = horario.strftime('%d/%m/%Y %H:%M')

        if usuario_recebe.get_nome() in usuario_manda.get_grupos():    #Esta mandando msg para um grupo
            dict_aux = usuario_manda.get_grupos()

            with open(dict_aux[usuario_recebe.get_nome()], 'a') as file:
                file.write(horario_str + '|' + usuario_manda.get_nome() + '|' + mensagem + '\n')

        elif usuario_recebe.get_nome() in usuario_manda.get_p2p():    #Já existe mensagens
            dict_aux = usuario_manda.get_p2p()

            with open(dict_aux[usuario_recebe.get_nome()], 'a') as file:
                file.write(horario_str + '|' + usuario_manda.get_nome() + '|' + mensagem + '\n')

        else: #Primeira mensagem
            hash_msg = md5((usuario_manda.get_nome() + usuario_recebe.get_nome() + horario_str).encode())
            hash_msg = hash_msg.hexdigest()
            hash_msg = hash_msg + '.log'

            with open(hash_msg, 'a') as file:
                file.write(horario_str + '|' + usuario_manda.get_nome() + '|' + mensagem + '\n')
            
            usuario_manda.update_p2p(usuario_recebe.get_nome(), hash_msg)
            usuario_recebe.update_p2p(usuario_manda.get_nome(), hash_msg)

    def criaGrupo(self, usuario, lista_membros, nome_grupo):
        pass

    def procuraUsuario(self, id):
        for user in self.usuarios:
            if id == user.nome:
                return user
        return None

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

daemon.requestLoop()
    