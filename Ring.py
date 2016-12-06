import os, hashlib,  Crypto.PublicKey.RSA
from random import randint

class myRing:
    def __init__(self, pKeys):
        self.pKeys = pKeys
        self.n = len(pKeys)

class myUser:
    def __init__(self, id, g, G, q):
        self.x = randint(0, q-1)
        self.y = pow(g, self.x, 2*q+1) #mod p ou q  ? ne change rien
        self.Pkeys = {'g':g , 'y':self.y, 'G':G}
        self.Skeys = {'Pkey':self.Pkeys, 'x':self.x}
        self.id =id

def myCreateRing(n, g, G, q):
    pKeys =[None]*n
    userArray =[None]*n
    for i in range(n):
        user = myUser(i, g, G, q)
        pKeys[i]= user.Pkeys
        userArray[i] = user
    ring = myRing(pKeys)
    return ring, userArray