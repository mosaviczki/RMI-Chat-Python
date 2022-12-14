import Pyro4

@Pyro4.expose
class User(object):
    def hello(self, name):
        return "Hello"


daemon = Pyro4.Daemon()                # make a Pyro daemon
uri = daemon.register(User)   # register the greeting maker as a Pyro object
print(uri)    # print the uri so we can use it in the client later

daemon.requestLoop()