import Pyro4

ns = Pyro4.locateNS()

uri = ns.lookup('obg')

o = Pyro4.Proxy(uri)

print(o)