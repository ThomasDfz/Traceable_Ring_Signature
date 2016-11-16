from math import gcd
from crypto import *
import hashlib

#def createTag(issue, publicKeys):

def Hash(issue, publicKeys, g, p, q):
    s = issue
    for keys in publicKeys:
        s = s + str(keys['g']) + str(keys['y']) + str(keys['G'])
    binary = ''.join(format(ord(x), 'b') for x in s)
    hashed = int(hashlib.sha1(binary.encode()).hexdigest(), 16)
    hashed = pow(g, hashed%q, p)
    return hashed

def HashPrime(issue, publicKeys, g, p, q, m):
    s = issue
    for keys in publicKeys:
        s = s + str(keys['g']) + str(keys['y']) + str(keys['G'])
    s = s+m
    binary = ''.join(format(ord(x), 'b') for x in s)
    hashed = int(hashlib.sha1(binary.encode()).hexdigest(), 16)
    hashed = pow(g, hashed % (q - 1), p)
    return hashed

def HashPrimePrime(issue, publicKeys, g, p, q, A_0, A_1, a, b):
    s = issue
    for keys in publicKeys:
        s = s + str(keys['g']) + str(keys['y']) + str(keys['G'])
    s = s + str(A_0)
    s = s + str(A_1)
    for n in a + b:
        s = s + str(n)
    binary = ''.join(format(ord(x), 'b') for x in s)
    hashed = int(hashlib.sha1(binary.encode()).hexdigest(), 16)
    hashed = pow(hashed, 1, q)
    return hashed

def findCoprimeList(n):
    coprimeList = []
    for i in range(2, n):
        if(gcd(i, n) == 1):
            coprimeList.append(i)
    return coprimeList
