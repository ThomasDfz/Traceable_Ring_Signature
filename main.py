import miscellaneous
import timeit
import Ring
from random import randint

q = 11      #Sophie Germain prime number
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
    g = g*g
    for qi in range(0, q):
        G.append(pow(g, qi, p)) #mod q ou mod p ?
    G = sorted(G)
    return G, g

def Sign(message, issue, publicKeys, user, G, g, userArray):

    n = len(publicKeys)
    i = user.id

    ####  etape 1  ####

    sigma = [None] * n
    hashed = miscellaneous.Hash(issue, publicKeys, g, p, q) #ok
    sigma[i] = pow(hashed, user.x, p) #mod q ?

    ####  etape 2  ####

    A_0 = miscellaneous.HashPrime(issue, publicKeys, g, p, q, message) #ok aussi
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
    #pour tout nombre entier x, si x^q%p == 1 alors x appartient à G <- a verifier
    #regarder les livres crypto
    Zq = list(range(0, q))  #Liste des Z/Zq
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
    Hpp = miscellaneous.HashPrimePrime(issue, message, publicKeys, g, p, q, A_0, A_1, a, b)

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
    ######## test ########

    message = "all your base are belong to us"
    message2 = "je vote deux fois !"
    message3 = "message trois"
    issue = "sondageID"
    userNumber = 6
    id = 2
    id2 = 3

    errorCount = 0
    doubleErrorCount = 0
    listeDesFaux =  []
    listeDesVrai = []

    #500 tests
    for i in range (0, 500):

        G, g = buildG()
        ring, userArray = Ring.myCreateRing(userNumber, g, G, q)

        #On signe 3 messages différents par la même personne.
        signature =  Sign(message,  issue, ring.pKeys, userArray[id], G, g, userArray)
        signature2 = Sign(message2, issue, ring.pKeys, userArray[id], G, g, userArray)
        signature3 = Sign(message3, issue, ring.pKeys, userArray[id], G, g, userArray)

        #Si trace ne fonctionne pas correctement
        if(Trace(issue, ring.pKeys, g, G, message, signature, message2, signature2) == "linked"):
            listedesy = [userArray[0].y, userArray[1].y, userArray[2].y, userArray[3].y, userArray[4].y, userArray[5].y]
            listeDesFaux.append(sorted(listedesy))
            errorCount = errorCount +1
            if(Trace(issue, ring.pKeys, g, G, message, signature, message3, signature3) == "linked"):
                doubleErrorCount = doubleErrorCount+1

        #juste pour garder un vingtième des cas où ça a fonctionné, pour comparer
        if(randint(0, 20) == 0):
            listedesy = [userArray[0].y, userArray[1].y, userArray[2].y, userArray[3].y, userArray[4].y, userArray[5].y]
            listeDesVrai.append(sorted(listedesy))

    #On peut comparer les Y des 6 personnes pour les cas qui ont fonctionnés, et les cas où ça n'a pas fonctionné.
    print("liste des y pour lesquels ça n'a pas marché : {}".format(listeDesFaux))
    print("___________")
    print("liste des y pour lesquels ça a  marché      : {}".format(listeDesVrai))

    #Nombre d'erreurs = environ nb_test/q
    print(errorCount)
    #environ nb_tests/q²
    print(doubleErrorCount)

main()
