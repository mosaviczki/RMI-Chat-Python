from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from serpent import tobytes
from datetime import datetime
from hashlib import md5
from os import mkdir, remove
import threading

daemon = Daemon()

def salvarUsuario(usuario):
    with open('users.dat', 'a') as file:
        line = usuario.get_nome() + ':' + usuario.get_senha() + '|'

        aux = usuario.get_p2p()

        for user in aux:
            line = line + user + ':' + aux[user] + ';'

        line = line + '|'

        aux = usuario.get_grupos()

        for grupos in aux:
            line = line + grupos + ':' + aux[grupos] + ';'

        line = line + '\n'
        file.write(line)

def carregarUsuario():
    try:
        with open('users.dat', 'r') as file:
            if len(file.read()) == 0: #Não ha nada no arquivo
                return list()
        
            file.seek(0)
    
            list_user = []

            for line in file.readlines():
                line = line.split('|')
                user = line[0]
                p2p = line[1]
                groups = line[2]

                ########## Nome e Senha ##########
                user = user.split(':') 
                usuario = Usuario(user[0], user[1])
                uri = daemon.register(usuario)
                usuario.set_uri(uri)

                ########## P2P ##########
                if p2p != '':   #caso nao seja vazio
                    p2p = p2p.split(';')

                    for user in p2p:
                        user = user.split(':')

                        if len(user) != 1:  #Verifica se não é vazio
                            usuario.update_p2p(user[0], user[1])

                ########## GRUPOS ##########
                if groups != '\n':  #Caso nao pertença a nenhum grupo
                    groups = groups.split(';')

                    for grupo in groups:
                        grupo = grupo.split(':')

                        if len(grupo) != 1:  #Verifica se não é vazio
                            usuario.update_grupo(grupo[0], grupo[1])

                list_user.append(usuario)
                print(line, user, p2p, groups)

        return list_user

    except FileNotFoundError:
        return list()



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

    def update_grupo(self, key, log):
        self.grupos[key] = log

    def get_grupos(self):
        return self.grupos

    def hello(self):
        return "hello"

@expose
class Grupo():
    def __init__(self, nome, opt):
        self.uri = None
        self.nome = nome
        self.excluir = opt
        self.dir = None
        self.adm = None
        self.membros = set()
        

    def update_membros(self, user):
        self.membros.add(user)

    def set_membros(self, membros):
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
    
    usuarios = carregarUsuario()
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
        horario = datetime.now()
        horario_str = horario.strftime('%d/%m/%Y %H:%M')

        usuario_recebe = self.procuraUsuario(nome_recebe)

        if usuario_recebe == None:  #Tenta achar o grupo caso nao ache o usuario
            ####################### GRUPO #######################
            usuario_recebe = self.procuraGrupo(nome_recebe)

            if (usuario_recebe == None) or (usuario_manda.get_nome() == nome_recebe):  # O destino nao existe OU esta mandando msg pra ele msg
                return None

            if usuario_recebe.get_nome() in usuario_manda.get_grupos(): #Verifica se o usuario faz parte do grupo
                dict_aux = usuario_manda.get_grupos()

                with open(dict_aux[usuario_recebe.get_nome()], 'a') as file:
                    file.write(horario_str + '|' + usuario_manda.get_nome() + '|' + mensagem + '\n')
            else:   #Nao esta no grupo
                return None


        ####################### P2P ####################### 

        elif usuario_recebe.get_nome() in usuario_manda.get_p2p():    #Já existe mensagens
            dict_aux = usuario_manda.get_p2p()

            with open(dict_aux[usuario_recebe.get_nome()], 'a') as file:
                file.write(horario_str + '|' + usuario_manda.get_nome() + '|' + mensagem + '\n')

        else: #Primeira mensagem
            hash_msg = md5((usuario_manda.get_nome() + usuario_recebe.get_nome() + horario_str).encode())
            hash_msg = hash_msg.hexdigest()
            hash_msg = hash_msg + '.log'

            with open(hash_msg, 'w') as file:
                file.write(horario_str + '|' + usuario_manda.get_nome() + '|' + mensagem + '\n')
            
            usuario_manda.update_p2p(usuario_recebe.get_nome(), hash_msg)
            usuario_recebe.update_p2p(usuario_manda.get_nome(), hash_msg)

    def criaGrupo(self, usuario, opt, lista_membros, nome_grupo):
        horario = datetime.now()
        horario_str = horario.strftime('%d/%m/%Y %H:%M')

        grupo = Grupo(nome_grupo, opt)

        hash_dir = md5((nome_grupo + horario_str).encode())
        hash_dir = hash_dir.hexdigest()
        hash_dir = hash_dir + '.log'

        grupo.set_dir(hash_dir)
        grupo.set_adm(usuario.get_nome())
        usuario.update_grupo(grupo.get_nome(), grupo.get_dir())

        for membro in lista_membros:
            self.addNoGrupo(usuario, membro, grupo.get_nome())

        self.grupos.append(grupo)

    def addNoGrupo(self, adm, usuario_nome, grupo_nome):
        grupo = self.procuraGrupo(grupo_nome)
        if grupo == None:   #Verifica se o grupo existe
            return None

        if grupo.get_adm() == adm.get_nome():   #Verifica se é o adm que esta chamando a funcao
            usuario = self.procuraUsuario(usuario_nome)
            if usuario != None: #Caso o usuario exista
                grupo.update_membros(usuario.get_nome())
                usuario.update_grupo(grupo.get_nome(), grupo.get_dir())

    


    def procuraUsuario(self, id):
        for user in self.usuarios:
            if id == user.nome:
                return user
        return None

    def procuraGrupo(self, nome_grupo):
        for grupo in self.grupos:
            if nome_grupo == grupo.get_nome():
                return grupo
        return None

    def printAllUsers(self):
        print("================USUARIOS===============")
        for user in self.usuarios:
            self.printUsuario(user)
    
    def printAllGroup(self):
        print("==============GRUPOS=================")
        for grupo in self.grupos:
            self.printGrupo(grupo)

    def printUsuario(self, usuario):
        print('-------------------------')
        print('URI: ', usuario.get_uri())
        print('Nome: ', usuario.get_nome())
        print('Senha: ', usuario.get_senha())
        print('P2P: ', usuario.get_p2p())
        print('GRUPOS: ', usuario.get_grupos())
    
    def printGrupo(self, grupo):
        print('=========================')
        print('Nome: ', grupo.get_nome())
        print('Dir: ', grupo.get_dir()) 
        print('ADM: ', grupo.get_adm())
        print('Mebros: ', grupo.get_membros())
         
    

print("[+] Starting server")
ns = locateNS()
server = Servidor()
uri = daemon.register(server)
ns.register("RMI", uri)

daemon.requestLoop()

print('\n[+] Salvando usuarios')
try:    #Apagando DB antigo
    remove('users.dat')
    remove('groups.dat')
except:
    pass
for user in server.usuarios:
    salvarUsuario(user)