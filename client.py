from Pyro4 import Daemon, Proxy, expose, oneway, callback, locateNS
import threading, time
@expose
class Cliente(object):
    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha
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
    
    nome = input("Digite seu nome: ")
    senha = input("Digite sua senha: ")


    callback = Cliente(nome, senha)
    callback.uri = daemon.register(callback)

    loop_thread = threading.Thread(target=callback.request_loop, args=(daemon, ))
    loop_thread.daemon = False
    loop_thread.start()

        
    with Proxy("PYRONAME:RMI") as server:
        # Cadastro do usuário
        server.cadastrar_cliente(callback.uri)
        server.show_users()