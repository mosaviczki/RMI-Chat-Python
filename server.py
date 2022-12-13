import Pyro4

@Pyro4.expose
class Hello:
    def say(self):
        return 'Hello'


daemon = Pyro4.Daemon()

uri = daemon.register(Hello) # Regitra a class

ns = Pyro4.locateNS()   #Localiza endereço do server

ns.register('obg', uri)

print(uri)

daemon.requestLoop()