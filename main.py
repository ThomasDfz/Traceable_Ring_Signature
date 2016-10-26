import miscellaneous
import Ring
from random import randint

q = 29     #Sophie Germain prime number
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
    generators = sorted(generators)
    G = []
    g = generators[1]
    for qi in range(0, q-1):
        G.append(pow(g, qi, p))
    return G, g

def Sign(message, issue, publicKeys, user, G, g):

    n = len(publicKeys)
    i = user.id

    ####  etape 1  ####

    sigma = [None] * n
    hashed = miscellaneous.Hash(issue, publicKeys, g, p, q)
    sigma[i] = pow(hashed, user.x)

    ####  etape 2  ####

    A_0 = miscellaneous.HashPrime(issue, publicKeys, g, p, q, message)
    A_1 = pow(sigma[i]/A_0, 1/(i))

    ####  etape 3  ####

    for j in range(0, n):
        if(j != i):
            sigma[j] = A_0 * pow(A_1, j)

    #### etape 4  ####
    ## a ##
    w_i = randint(0, q-1)
    a, b = [None] * n, [None] * n
    a[i] = pow(g, w_i, p)  #pas sûr que ça soit modulo p
    b[i] = pow(hashed, w_i, p)

    ## b ##
    z, c = [None]*n, [None]*n
    for j in range(0, n):
        if(j != id):
            z[j] = randint(0, q-1)
            c[j] = randint(0, q-1)
            a[j] = divmod(pow(g, z[j], p) * pow(user.y, c[j], p), p)[1] #pas sûr que ça soit modulo p
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

    if(g not in G or A_1 not in G):
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

def main():
    ######## test ########
    message = "all your base are belong to us"
    issue = "sondageID"
    userNumber = 6
    id = 2

    G, g = buildG()
    ring, userArray = Ring.myCreateRing(userNumber, g, G, q)

    signature = Sign(message, issue, ring.pKeys, userArray[id], G, g)
    Verify(issue, ring.pKeys, message, signature, G, g, userArray)

main()
