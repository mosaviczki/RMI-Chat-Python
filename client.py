import  Pyro4

o = Pyro4.Proxy('PYRO:obj_d135b791ae5f42bda5d1b9d72a466131@localhost:41345')

print(o.say())