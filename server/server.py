from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from hashlib import md5
import threading

class Usuario():

    def __init__(self, nome, senha) -> None:
        self.nome = nome
        self.senha = senha
        self.mensagens = set()
        self.uri = None

    def set_uri(self, uri):
        self.uri = uri
  
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
                senha = user[1]

                usuario = Usuario(nome, senha)
                usuario.set_uri(Daemon().register(usuario))
                list_user.append(usuario)
            
            return list_user
    except FileNotFoundError:
        return list()

@expose
class Servidor():
    
    usuarios = carregarUsuarios()

    def cadastrar_usuario(self, nome, senha):
        usuario = Usuario(nome, senha)
        usuario.set_uri(daemon.register(usuario))
        

        with open('users.dat', 'r') as file:
            for linha in file.readlines():
                if linha.split(':')[0] == nome:
                    return False

        with open('users.dat', 'a') as file:
            file.write(nome + ':' + senha + '\n')
        Servidor.usuarios.append(usuario)

        print(f"[+] Usuario {nome} criado")

    def show_users(self, users = usuarios):
        print('--------------------USERS-----------------------')
        for user in users:
            print('-------------------------------------------')
            print(user.nome)
            print(user.senha)
            print(user.mensagens)
            print(user.uri)
    
    def mandarMensagem(self, id_manda, id_rec, msg):
        usuario_manda = self.procura(id_manda)
        usuario_rec = self.procura(id_rec)

        arq_nome = usuario_manda.nome + usuario_rec.nome
        arq_nome = md5(arq_nome.encode())
        arq_nome = arq_nome.hexdigest()
        arq_nome = arq_nome + '.log'

        with open(arq_nome, 'w') as file:
            file.write(msg)
        
        usuario_manda.mensagens.add(arq_nome)
        usuario_rec.coversas.add(arq_nome)

    def procura(self, id, users = usuarios):
        for user in users:
            if id == user.nome:
                return user

    def login(self, nome, senha, users = usuarios):
        for user in users:
            if nome == user.nome and senha == user.senha:
                return user.mensagens
        return False

with Daemon() as daemon:
    print("[+] Starting server")
    ns = locateNS()
    server = Servidor()
    uri = daemon.register(server)
    ns.register("RMI", uri)

    print(uri)

    daemon.requestLoop()
    