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

def salvarGrupo(grupo):
    with open('groups.dat', 'a') as file:
        line = grupo.get_nome() + ':' + grupo.get_dir() + ':' + str(grupo.get_excluir()) +'|' + grupo.get_adm() + '|'
        for user in grupo.get_membros():
            line = line + user + ';'

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

        return list_user

    except FileNotFoundError:
        return list()

def carregarGrupo():
    try:
        with open('groups.dat', 'r') as file:
            if len(file.read()) == 0: #Não ha nada no arquivo
                return list()
        
            file.seek(0)
    
            list_group = []

            for line in file.readlines():
                line = line.split('|')
                group = line[0]
                adm = line[1]
                membros = line[2]

                ########## INIT ##########
                grupo = None
                group = group.split(':')

                if group[2] == 'True':
                    grupo = Grupo(group[0], True)
                else:
                    grupo = Grupo(group[0], False)
                
                grupo.set_dir(group[1])

                ########## ADM ##########
                grupo.set_adm(adm)

                ########## MEMBROS ##########
                if membros != '\n':
                    membros = membros.split(';')

                    for membro in membros:
                        if membro != '\n' and membro != '':
                            grupo.update_membros(membro)

                
                list_group.append(grupo)

        return list_group

    except FileNotFoundError:
        return list()

@expose
class Usuario():

    def __init__(self, nome, senha) -> None:
        self.uri = None
        self.nome = nome
        self.senha = senha
        self.loged = False
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

    def set_loged(self, opt):
        self.loged = opt

    def get_loged(self):
        return self.loged
    
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

    def get_excluir(self):
        return self.excluir

    def get_adm(self):
        return self.adm

    def get_membros(self):
        return self.membros
    
@expose
class Servidor(object):
    
    usuarios = carregarUsuario()
    grupos = carregarGrupo()

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
                user.set_loged(True)
                cliente.set_uriUser(user.uri)

    def logout(self, callback):
        cliente = Proxy(callback)
        cliente.set_uriUser(None)

        usuario = self.procuraUsuario(cliente.get_nome())
        usuario.set_loged(False)


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

        grupo = self.procuraGrupo(nome_grupo)
        if grupo != None:   #Um grupo ja existe com este nome
            return None

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
        self.mandarMensagem(usuario, grupo.get_nome(), 'Criou o Grupo!')

    def addNoGrupo(self, adm, usuario_nome, grupo_nome):
        grupo = self.procuraGrupo(grupo_nome)
        if grupo == None:   #Verifica se o grupo existe
            return None

        if grupo.get_adm() == adm.get_nome():   #Verifica se é o adm que esta chamando a funcao
            usuario = self.procuraUsuario(usuario_nome)
            if usuario != None: #Caso o usuario exista
                if usuario.get_nome() in grupo.get_membros():   # O usuario ja esta no grupo
                    return None

                grupo.update_membros(usuario.get_nome())
                usuario.update_grupo(grupo.get_nome(), grupo.get_dir())

                self.mandarMensagem(adm, grupo.get_nome(), 'Adicionou ' + usuario_nome)

    def banDoGrupo(self, adm, usuario_nome, grupo_nome):
        grupo = self.procuraGrupo(grupo_nome)

        if adm.get_nome() == usuario_nome: #O ADM nao pode se banir
            return None

        if adm.get_nome() == grupo.get_adm():   #Verifica se é ADM
            if usuario_nome in grupo.get_membros(): #Verifica se o usuario faz parte do grupo
                aux = grupo.get_membros() #AUX recebe todos os membros
                aux.remove(usuario_nome)
                grupo.set_membros(aux)

                ########### USUARIO ###########
                usuario = self.procuraUsuario(usuario_nome)
                aux = usuario.get_grupos()
                aux.pop(grupo.get_nome())
                usuario.set_grupos(aux)

                self.mandarMensagem(adm, grupo.get_nome(), 'Baniu ' + usuario_nome)

    def sairDoGrupo(self, usuario, grupo_nome):
        grupo = self.procuraGrupo(grupo_nome)

        if usuario.get_nome() == grupo.get_adm():   #O ADM esta saindo do grupo
            if grupo.get_excluir(): #Caso esteja configurada a opção excluir quando o ADM sair
                self.excluirGrupo(usuario, grupo.get_nome())
            
            else:   #Escolhe um novo ADM
                if grupo.get_membros(): #Verifica se ha algum membro
                    aux = list(grupo.get_membros())
                    grupo.set_adm(aux[0])   #Set ADM o primeiro da lista de membros
                    aux = set(aux)
                    aux.remove(grupo.get_adm())   #Remove a lista de membros o novo ADM

                    grupo.set_membros(aux)

                else:   #Caso não haver nenhum membro exclua o grupo
                    self.excluirGrupo(usuario, grupo.get_nome())
        else:   #Um membro esta saindo do grupo
            self.mandarMensagem(usuario, grupo.get_nome(), 'Saiu do grupo!')
            aux = usuario.get_grupos()
            aux.pop(grupo.get_nome())
            usuario.set_grupos(aux)

            aux = grupo.get_membros() 
            aux.remove(usuario.get_nome())
            grupo.set_membros(aux)


    def excluirGrupo(self, adm, grupo_nome):
        grupo = self.procuraGrupo(grupo_nome)

        if adm.get_nome() != grupo.get_adm():  #Não é o ADM que esta pedindo a exclusão
            return None

        for membro in grupo.get_membros():  # Removendo todos os membros
            ########### USUARIO ###########
            usuario = self.procuraUsuario(membro)
            aux = usuario.get_grupos()
            aux.pop(grupo.get_nome())
            usuario.set_grupos(aux)
        
        aux = adm.get_grupos()
        aux.pop(grupo.get_nome())
        adm.set_grupos(aux)

        remove(grupo.get_dir()) #Apaga o arquivo log

        self.grupos.remove(grupo)

    def carregarMensagem(self, arq_nome):
        file = open(arq_nome, 'r')
        lines = file.readlines()
        return lines
    
    def showUsers(self):
        lista = []
        for user in self.usuarios:
            lista.append(user.get_nome())

        return lista


    def showGroups(self):
        lista = []
        for grupo in self.grupos:
            lista.append(grupo.get_nome())

        return lista
        
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

    ############ ONLINE OU OFFLINE ############
    def showOnline(self):
        listaOn = []
        for user in self.usuarios:
            if user.get_loged():
                listaOn.append(user.get_nome())
        return listaOn
    
    def showOffline(self):
        listaOff = []
        for user in self.usuarios:
            if not user.get_loged():
                listaOff.append(user.get_nome())
        return listaOff
                

    #def showOfline(self):
         

print("[+] Starting server")
ns = locateNS()
server = Servidor()
uri = daemon.register(server)
ns.register("RMI", uri)

daemon.requestLoop()

try:    #Apagando DB antigo
    remove('users.dat')
    remove('groups.dat')
except:
    pass
print('\n[+] Salvando usuarios')
for user in server.usuarios:
    salvarUsuario(user)

print('[+] Salvando grupos')
for grupo in server.grupos:
    salvarGrupo(grupo)