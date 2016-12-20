import miscellaneous
import timeit
import Ring
from random import randint

q = 443      #Sophie Germain prime number
p = 2*q+1   #prime too

def buildG():
    start = timeit.default_timer()
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

    generators = sorted(generators)

    G = []
    g = generators[1]
    g = pow(g*g, 1, p)
    for qi in range(0, q):
        G.append(pow(g, qi, p))
    G = sorted(G)

    return G, g

def Sign(message, issue, publicKeys, user, G, g, userArray):

    n = len(publicKeys)
    i = user.id

    ####  etape 1  ####

    sigma = [None] * n
    hashed = miscellaneous.Hash(issue, publicKeys, g, p, q)
    sigma[i] = pow(hashed, user.x, p)

    ####  etape 2  ####

    A_0 = miscellaneous.HashPrime(issue, publicKeys, g, p, q, message)

    A_1 = pow(pow(sigma[i] * pow(A_0, p-2 , p), 1, p), pow(i, q-2 , q), p)

    ####  etape 3  ####

    for j in range(0, n):
        if(j != i):
            sigma[j] = pow(A_0 * pow(A_1, j, p), 1, p)

    #### etape 4  ####
    ## a ##
    w_i = randint(0, q-1)
    a, b = [None] * n, [None] * n
    a[i] = pow(g, w_i, p)
    b[i] = pow(hashed, w_i, p)
    ## b ##
    z, c = [None]*n, [None]*n
    for j in range(0, n):
        if(j != i):
            z[j] = randint(0, q-1)
            c[j] = randint(0, q-1)
            a[j] = pow(pow(g, z[j], p) * pow(userArray[j].y, c[j], p), 1,  p)
            b[j] = pow(pow(hashed, z[j], p) * pow(sigma[j], c[j], p), 1, p)
    ## c ##
    c_solo = miscellaneous.HashPrimePrime(issue, message, publicKeys, g, p, q, A_0, A_1, a, b)
    ## d ##
    sum = 0
    for j in range(0, n):
        if(j != i):
            sum = sum + c[j]
    sum = pow(sum, 1, q)

    c[i] = pow(c_solo - sum, 1, q)
    z[i] = pow(w_i - c[i]*user.x, 1, q)

    return [A_1, c, z]



def Verify(issue, publicKeys, message, signature, G, g, userArray):
    A_1, c, z = signature
    n = len(publicKeys)
    ## etape 1 ##
    if(g not in G):
        return False
    if(A_1 not in G):
        return False
    #pour tout nombre entier x, si x^q%p == 1 alors x appartient à G  !!
    Zq = list(range(0, q))
    for i in range(0, n):
        if(c[i] not in Zq):
            return False
        if(z[i] not in Zq):
            return False
        if(userArray[i].y not in G):
            return False
    hashed = miscellaneous.Hash(issue, publicKeys, g, p, q)

    A_0 = miscellaneous.HashPrime(issue, publicKeys, g, p, q, message)
    sigma = [None]*n
    for i in range(0, n):
        sigma[i] = pow(A_0*pow(A_1, i, p), 1, p)
    ## etape 2 ##
    a, b = [None]*n, [None]*n
    for i in range(0, n):
        a[i] = pow(pow(g, z[i], p) * pow(userArray[i].y, c[i], p), 1, p)
        b[i] = pow(pow(hashed, z[i], p) * pow(sigma[i], c[i], p), 1, p)
    ## etape 3 ##
    sum = 0
    for i in range(0, n):
        sum = sum + c[i]
    Hpp = miscellaneous.HashPrimePrime(issue,message, publicKeys, g, p, q, A_0, A_1, a, b)

    if(pow(Hpp, 1, q) != pow(sum, 1, q)):
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
        sigma[i] = pow(A_0 * pow(A_1, i, p), 1, p)
        sigmab[i] = pow(A_0b * pow(A_1b, i, p), 1, p)

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
    message = "salut"
    message2 = "toast"
    message3 = "salut"
    message4 = "bidon"
    issue = "2"
    userNumber = 3
    id = 1
    id2 = 2
    G, g = buildG()
    ring, userArray = Ring.myCreateRing(userNumber, g, G, q)
    signature = Sign(message, issue, ring.pKeys, userArray[id], G, g, userArray)
    signature2 = Sign(message2, issue, ring.pKeys, userArray[id2], G, g, userArray)
    signature3 = Sign(message3, issue, ring.pKeys, userArray[id], G, g, userArray)
    signature4 = Sign(message4, issue, ring.pKeys, userArray[id], G, g, userArray)

    #TESTS

    print("Verif of message and his signature : ")
    print(Verify(issue, ring.pKeys, message, signature, G, g, userArray))

    print("\nVerif of message2 and another signature : ")
    print(Verify(issue, ring.pKeys, message2, signature, G, g, userArray))

    print("\nVerif of message2 and his signature : ")
    print(Verify(issue, ring.pKeys, message2, signature2, G, g, userArray))

    print("\nTrace of different message by different people :")
    print(Trace(issue, ring.pKeys, g, G, message, signature, message2, signature2))

    print("\nTrace of same message by the same person :")
    print(Trace(issue, ring.pKeys, g, G, message, signature, message3, signature3))

    print("\nTrace of different message by the same person :")
    print(Trace(issue, ring.pKeys, g, G, message, signature, message4, signature4))
main()
