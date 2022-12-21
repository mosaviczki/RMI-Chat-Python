import threading

def f1(x):
    x=0
    while x<10000000000:
        x += 1
        print(x)

aux =1

a = threading.Thread(target=f1(aux), name='F1')
print(a.is_alive())
exit()