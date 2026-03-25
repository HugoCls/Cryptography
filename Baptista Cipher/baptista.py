import random as rd
import time

def encrypt(data, x0, r, xmin, xmax, p):
    t = time.time()

    n = len(data)
    ep = (xmax - xmin) / 256
    x = x0
    c = [0] * n

    # Ignore initial transient
    for _ in range(100):
        x = r * x * (1 - x)
    
    m = n
    # Main loop
    for i in range(m): # Loop on each caracter
        while True:
            #print(n,i, int((x - 0.2) * 256 / 0.6), data[i])
            # rand() in mapl code is a random int between 0 and 10^12 excluded,
            # here rd.random() is between 0 and 1 excluded, we do not have to divide
            if int((x - 0.2) * 256 / 0.6) == data[i] and rd.random() > p:
                break
            x = r * x * (1 - x)
            c[i] += 1
    print(f"Elapsed time: {int(time.time()-t)}s, Required time: {round(((time.time()-t) * n/m) / 3600, 2)} hours")
    return c


def decrypt(data, n, x0, r, xmin, xmax):
    ep = (xmax - xmin) / 256
    x = x0
    p = [0] * n

    for _ in range(100):
        x = r * x * (1 - x)

    # Main loop
    for i in range(n): # Loop on each caracter
        #print(n,i)
        for _ in range(data[i]): # Number of operations on x to cipher the ith caracter

            x = r * x * (1 - x)

        p[i] = int((x - 0.2) * 256 / 0.6) # After N operations we should have int((x - 0.2) * 256 / 0.6) == s[i]
    
    return p