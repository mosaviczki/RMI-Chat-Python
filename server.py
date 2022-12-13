import Pyro4

@Pyro4.expose
class Hello:
    def say(self):
        return 'Hello'


daemon = Pyro4.Daemon()

uri = daemon.register(Hello)

print(uri)

daemon.requestLoop()