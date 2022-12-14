from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from datetime import datetime
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
                senha = user[1].split('|')[0]

                usuario = Usuario(nome, senha)
                
                msgs = user[1].split('|')[1:]
                for msg in msgs:
                    if msg != '\n':
                        usuario.mensagens.add(msg)
            
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
    
    def mandarMensagem(self, id_manda, id_rec, msg):
        usuario_manda = self.procuraUsuario(id_manda)
        usuario_rec = self.procuraUsuario(id_rec)

        horario = datetime.now()
        horario_str = horario.strftime('%d/%m/%Y %H:%M')

        arq_nome = usuario_manda.nome + usuario_rec.nome
        arq_nome = md5(arq_nome.encode())
        arq_nome = arq_nome.hexdigest()
        arq_nome = arq_nome + '.log'

        arq_nome1 = usuario_rec.nome + usuario_manda.nome 
        arq_nome1 = md5(arq_nome1.encode())
        arq_nome1 = arq_nome1.hexdigest()
        arq_nome1 = arq_nome1 + '.log'

        print("AAA")

        if self.vrfHash(usuario_manda.nome, arq_nome):
            with open(arq_nome, 'a') as file:
                file.write(horario_str + '|' + usuario_manda.nome + '|' + msg + '\n')


        elif self.vrfHash(usuario_manda.nome, arq_nome1):
            with open(arq_nome1, 'a') as file:
                file.write(horario_str + '|' + usuario_manda.nome + '|' + msg + '\n')

        else:
            usuario_manda.mensagens.add(arq_nome)
            usuario_rec.mensagens.add(arq_nome)

            with open('users.dat', 'r') as file:
                for linha in file.readlines():
                    if linha.split(':')[0] == usuario_manda.nome:
                        file.write('|' + arq_nome + '|')

    def vrfHash(self, id, hsh_recebido):
        
        print('inic fun verifica hash')
        with open('users.dat', 'r') as file:
            for linha in file.readlines():
                if linha.split(':')[0] == id:
                    linha = linha.split('|')[1:]
                    for hsh in linha:
                        if hsh == hsh_recebido:
                            return True
        
        print('inic fun verifica hash')

        return False

    def procuraUsuario(self, id, users = usuarios):
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
    