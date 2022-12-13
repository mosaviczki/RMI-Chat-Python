from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
from hashlib import md5
import threading, time
@expose
class Cliente(object):
    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha
        self.mensagens = None
        self.uri = ""

    def get_nome(self):
        return self.nome

    def get_senha(self):
        return self.senha
    
    def get_uri(self):
        return self.uri

    def request_loop(self, daemon):
        daemon.requestLoop()
        time.sleep(2)
    

with Daemon() as daemon:
        
    with Proxy("PYRONAME:RMI") as server:

        while True: 
            print("--------------------------------")
            print("1-Login\n2-Registrar")
            option = int(input(""))
            """
            if option == 1:
                nome = input("Nome: ")
                senha = input("Senha: ")

                user = server.login(nome, senha)

                print(user)
            """
            if option == 2:

                nome = input("Digite seu nome: ")
                senha = input("Digite sua senha: ")

                senha = md5(senha.encode())
                senha = senha.hexdigest()   #Transformando em string 

                server.cadastrar_usuario(nome, senha)

            if option == 3:
                server.show_users()
    