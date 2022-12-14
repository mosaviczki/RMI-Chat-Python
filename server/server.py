from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from serpent import tobytes
from datetime import datetime
from hashlib import md5
from os import mkdir
import threading

daemon = Daemon()

@expose
class Usuario():

    def __init__(self, nome, senha) -> None:
        self.nome = nome
        self.senha = senha
        self.mensagens = set()
        self.uri = None

    def get_nome(self):
        return self.nome

    def set_uri(self, uri):
        self.uri = uri

    def get_uri(self):
        return self.uri
    
    def get_mensagens(self):
        return self.mensagens
    
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

    def set_uri(self, uri):
        self.uri = uri

    def set_adm(self, user):
        self.adm = user

    def set_dir(self, dir):
        self.dir: dir
    
        
  
def carregarUsuarios():
    try:
        with open('users.dat', 'r') as file:
            
            if len(file.read()) == 0: #Não ha nada no arquivo
                return list()
        
            file.seek(0)
    
            list_user = []


            for user in file.readlines():
                user = user.split(':')
                nome = user[0]
                senha = user[1].split('|')[0]

                usuario = Usuario(nome, senha)
                
                msgs = user[1].split('|')[1:]
                for msg in msgs:
                    if msg != '\n':
                        msg = msg.replace('\n', '')
                        usuario.mensagens.add(msg)
            
                ns = locateNS()

                uri = daemon.register(usuario)
                usuario.set_uri(uri)
                
                ns.register(usuario.nome, uri)

                try:
                    mkdir('./' + usuario.nome)
                except:
                    pass
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
    
            list_groups = []


            for group in file.readlines():
                group_list = group.split('|')

                nome = group_list[0]
                adm = group_list[2]
                membros = group_list[3:]
                diretorio = group_list[1]
                
                grupo = Grupo(nome)
                grupo.set_adm(adm)
                grupo.set_dir(diretorio)
                grupo.set_membros(membros)
                
                ns = locateNS()

                uri = daemon.register(grupo)
                grupo.set_uri(uri)
                
                ns.register(grupo.nome, uri)
                
                list_groups.append(grupo)
            
            return list_groups

    except FileNotFoundError:
        return list()

@expose
class Servidor(object):
    
    usuarios = carregarUsuarios()
    grupos = carregarGrupo()

    def cadastrar_usuario(self, nome, senha):
        ns = locateNS()

        usuario = Usuario(nome, senha)
        uri = daemon.register(usuario)
        usuario.set_uri(uri)
        
        ns.register(nome, uri)
        
        try:
            with open('users.dat', 'r') as file:
                for linha in file.readlines():
                    if linha.split(':')[0] == nome:
                        return False
        except FileNotFoundError:
            pass
        with open('users.dat', 'a') as file:
            file.write(nome + ':' + senha + '\n')
        Servidor.usuarios.append(usuario)

        print(f"[+] Usuario {nome} criado")

    def show_users(self, users = usuarios):
        print('--------------------USERS-----------------------')
        for user in users:
            print("Nome:", user.nome)
            print("Senha:", user.senha)
            print("Msg:", user.mensagens)
            print("URI:", user.uri)
            print('-----------------------------------------------')
    
    def mandarMensagem(self, callback, id_rec, msg):
        
        cliente = Proxy(callback)

        usuario_manda = self.procuraUsuario(cliente.get_nome())
        usuario_rec = self.procuraUsuario(id_rec)

        aux = list()
        aux.append(str(usuario_manda.nome))
        aux.append(str(usuario_rec.nome))
        aux.sort()

        horario = datetime.now()
        horario_str = horario.strftime('%d/%m/%Y %H:%M')

        arq_nome = aux[0] + aux[1]
        arq_nome = md5(arq_nome.encode())
        arq_nome = arq_nome.hexdigest()
        arq_nome = arq_nome + '.log'

        if self.vrfHash(usuario_manda.nome, arq_nome):
            with open(arq_nome, 'a') as file:
                file.write(horario_str + '|' + usuario_manda.nome + '|' + msg + '\n')

        else:
            usuario_manda.mensagens.add(arq_nome)
            usuario_rec.mensagens.add(arq_nome)

            for user in aux:
                
                file = open('users.dat', 'r')
                lines = file.readlines()
                i = 0
                for itens in lines:
                    if itens.split(':')[0] == user:
                        linhas = i
                        texto = itens

                    i+=1
                file.close()

                lines[linhas] = texto.replace('\n', '') + '|' + arq_nome +'\n'

                file = open('users.dat', 'w')
                file.writelines(lines)
                file.close()
            with open(arq_nome, 'w') as file:
                file.write(horario_str + '|' + usuario_manda.nome + '|' + msg + '\n')

    def criaGrupo(self, callback, ids_part, nome_grupo):
        
        cliente = Proxy(callback)
        grupo = Grupo(nome_grupo)

        for user in ids_part:
            user = self.procuraUsuario(user)
            grupo.set_membros(user)
        
        adm = self.procuraUsuario(cliente.get_nome())

        grupo.set_adm(adm)

        horario = datetime.now()
        horario_str = horario.strftime('%d/%m/%Y %H:%M')

        hash_grupo = md5((nome_grupo+horario_str).encode())
        hash_grupo = hash_grupo.hexdigest()
        hash_grupo = hash_grupo + '.log'

        grupo.set_dir(hash_grupo)

        
        with open('groups.dat', 'a') as file:
            file.write(grupo.nome + '|' + hash_grupo + '|' + adm.get_nome())
            for user in ids_part:
                user = self.procuraUsuario(user)
                file.write('|'+ user.get_nome())
            file.write('\n')

        Servidor.grupos.append(grupo)


    def vrfHash(self, id, hsh_recebido):  
        with open('users.dat', 'r') as file:
            for linha in file.readlines():
                if linha.split(':')[0] == id:
                    linha = linha.split('|')[1:]
                    for hsh in linha:
                        if hsh.replace('\n','') == hsh_recebido:
                            return True

        return False

    def procuraUsuario(self, id, users = usuarios):
        for user in users:
            if id == user.nome:
                return user

    def login(self, callback, users = usuarios):

        cliente = Proxy(callback)

        nome = cliente.get_nome()
        senha = cliente.get_senha()

        
        for user in users:
            user.senha = user.senha.replace('\n', '')

            if nome == user.nome and senha == user.senha:
                cliente.notificar("Logging...")
                cliente.set_uriUser(user.uri)
        

    def carregarMensagens(self, arq_nome):
        file = open(arq_nome, 'r')
        lines = file.readlines()
        return lines

    def enviarArquivo(self, callback, nome, buffer):      
        cliente = Proxy(callback)

        buffer = tobytes(buffer)

        arq = open('./'+ cliente.get_nome() + '/' + nome, 'wb')
        arq.write(buffer)
        arq.close()

        cliente.notificar('Arquivo enviado com sucesso!')


print("[+] Starting server")
ns = locateNS()
server = Servidor()
uri = daemon.register(server)
ns.register("RMI", uri)

print(uri)

daemon.requestLoop()
    