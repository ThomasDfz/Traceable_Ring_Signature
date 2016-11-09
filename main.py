import miscellaneous
import Ring
from random import randint

q = 11     #Sophie Germain prime number
p = 2*q+1   #prime too

def buildG():
    primfac = [2, q] #décomposition en facteurs premiers de p-1 = 2*q
    generatorFound = False
    x = 1
    while not generatorFound :  #while pour chercher le premier generateur x
        generatorFound = True
        x = x+1
        for pi in primfac:
            if (pow(x,int((p-1)/pi), p) == 1) :
                generatorFound = False
    generators = [x]
    coprimeList = miscellaneous.findCoprimeList(p-1)
    for qi in coprimeList:
        generators.append(pow(x, qi, p))
    generators = sorted(generators)   #cela FONCTIONNE
    G = []
    g = generators[1]
    for qi in range(0, q):
        G.append(pow(g, qi, p)) #mod q ou mod p ?
    G = sorted(G)
    print(G)
    return G, g

def Sign(message, issue, publicKeys, user, G, g):

    n = len(publicKeys)
    i = user.id

    ####  etape 1  ####

    sigma = [None] * n
    hashed = miscellaneous.Hash(issue, publicKeys, g, p, q) #ok

    sigma[i] = pow(hashed, user.x, p) #mod q ?

    ####  etape 2  ####

    A_0 = miscellaneous.HashPrime(issue, publicKeys, g, p, q, message) #ok aussi

    A_1 = pow(pow(sigma[i] * pow(A_0, p-2 , p), 1, p), pow(i, p-2 , p), p)

    ####  etape 3  ####

    for j in range(0, n):
        if(j != i):
            sigma[j] = A_0 * pow(A_1, j)

    #### etape 4  ####
    ## a ##
    w_i = randint(0, q-1)
    a, b = [None] * n, [None] * n
    a[i] = pow(g, w_i, p)
    b[i] = pow(hashed, w_i, p)

    ## b ##
    z, c = [None]*n, [None]*n
    for j in range(0, n):
        if(j != id):
            z[j] = randint(0, q-1)
            c[j] = randint(0, q-1)
            a[j] = divmod(pow(g, z[j], p) * pow(user.y, c[j], p), p)[1]
            b[j] = divmod(pow(hashed, z[j], p) * pow(int(sigma[j]), c[j], p), p)[1] #enlever le int(sigma) quand pb resolu

    ## c ##
    c_solo = miscellaneous.HashPrimePrime(issue, publicKeys, g, p, q, A_0, A_1, a, b)

    ## d ##
    sum = 0
    for j in range(0, n):
        if(j != user.id):
            sum = sum + c[j]
    c[i] = (c_solo - sum)%q
    z[i] = (w_i - c[i]*user.x)%q

    return [A_1, c, z]



def Verify(issue, publicKeys, message, signature, G, g, userArray):
    A_1, c, z = signature
    n = len(publicKeys)
    ## etape 1 ##
    if(g not in G):
        return False
    if(A_1 not in G):
        return False
    Zq = list(range(0, q-1))  #Liste des Z/Zq

    for i in range(0, n):
        if(c[i] not in Zq or z[i] not in Zq):
            return False
        if(userArray[i].y not in G):
            return False

    hashed = miscellaneous.Hash(issue, publicKeys, g, p, q)
    A_0 = miscellaneous.HashPrime(issue, publicKeys, g, p, q, message)
    sigma = [None]*n
    for i in range(0, n):
        sigma[i] = A_0*pow(A_1, i)

    ## etape 2 ##

    a, b = [None]*n, [None]*n
    for i in range(0, n):
        a[i] = pow(g, z[i]) * pow(userArray[i].y, c[i])
        b[i] = pow(hashed, z[i]) * pow(sigma[i], c[i])

    ## etape 3 ##

    sum = 0
    for i in range(0, n):
        sum = sum + c[i]
    if(abs(miscellaneous.HashPrimePrime(issue, publicKeys, g, p, q, A_0, A_1, a, b) - sum)%q != 0):
        return False

    ## etape 4 ##
    return True

def Trace(issue, publicKeys, g, G, message, signature, messageb, signatureb):
    A_1, c, z = signature
    A_1b, cb, zb = signatureb
    n = len(publicKeys)

    ## etape 1 ##
    hashed = miscellaneous.Hash(issue, publicKeys, g, p, q)
    A_0 = miscellaneous.HashPrime(issue, publicKeys, g, p, q, message)
    A_0b = miscellaneous.HashPrime(issue, publicKeys, g, p, q, messageb)

    sigma = [None] * n
    sigmab = [None] * n
    for i in range(0, n):
        sigma[i] = pow(A_0 * pow(A_1, i), 1, p)
        sigmab[i] = pow(A_0b * pow(A_1b, i), 1, p)

    ## etape 2 ##

    TList = []
    for i in range(0, n):
        if(sigma[i] == sigmab[i]):
            TList.append(publicKeys[i])

    ## etape 3 ##

    if(len(TList) == 1):
        return TList[0]
    elif(len(TList) == n):
        return "linked"
    else:
        return "indep"




def main():
    ######## test ########
    message = "all your base are belong to us"
    issue = "sondageID"
    userNumber = 6
    id = 2

    G, g = buildG()
    ring, userArray = Ring.myCreateRing(userNumber, g, G, q)

    signature = Sign(message, issue, ring.pKeys, userArray[id], G, g)

    print(Verify(issue, ring.pKeys, message, signature, G, g, userArray))



main()
