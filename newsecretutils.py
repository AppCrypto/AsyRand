'''
Contains all the auxillary functions to do linear secret sharing (LSS) over an access structure. Mainly, we represent the
access structure as a binary tree. This could also support matrices for representing access structures.
'''
from charm.core.math.pairing import ZR
from charm.toolbox.pairinggroup import *
# from .newpolicytree import *
import sys,random
import time

class SecretUtil:
    def __init__(self, groupObj, verbose=True):
        self.group = groupObj

    #        self.parser = PolicyParser()
        
    def P(self, coeff, x):
        share = coeff[0]
        newx = self.group.init(ZR, x)
        # evaluate polynomial
        for j in range(1, len(coeff)):
            # print("j::  "+str(j))
            i = self.group.init(ZR, j)
            share += coeff[j] * (newx ** i)
        return share

    def genShares(self, secret, k, n):
        if (k <= n):
            rand = self.group.random
            a = []  # will hold polynomial coefficients
            for i in range(0, k):
                if (i == 0):
                    a.append(secret)  # a[0]
                else:
                    a.append(rand(ZR))
            shares = { i:self.P(a, i) for i in range(0,n+1) }    
            # shares = [self.P(a, i) for i in range(0, n + 1)]
            # print(shares)
            # print([self.P(a, i) for i in range(0, n + 1)])
        return shares

    # shares is a dictionary
    def recoverCoefficients(self, list):
        tmp={}
        coeff = {}
        list2 = [self.group.init(ZR, i) for i in list]
        for i in list2:
            # starttime= time.time()
            result = 1
            for j in list2:
                if i != j:
                    if i-j not in tmp:
                        tmp[i-j]= 1 / (i - j)
                        tmp[j-i]= self.group.order() - tmp[i-j]
                    result *= (0 - j)*tmp[i-j]
            # print("coeff '%d' => '%s'" % (i, result))
            coeff[int(i)] = result
            # print(len(list2), time.time()-starttime)
            # print(type(coeff[int(i)]), self.group.order())
        return coeff
    
    

    def recoverCoefficients2(self, list):
        """recovers the coefficients over a binary tree."""
        coeff = {}
        list2 = [self.group.init(ZR, i) for i in list]
        for i in list2:
            result = 1
            for j in list2:
                if not (i == j):
                    # lagrange basis poly
                    result *= (0 - j) * self.group.init(ZR, mod_inverse(int(i-j), self.group.order()))
            # print("coeff '%d' => '%s'" % (i, result))
            coeff[int(i)] = result
            # print(type(coeff[int(i)]), self.group.order())
        return coeff



    
def tInNrandom(t, n) :
    T=[i for i in range(1, n+1)]
    random.shuffle(T)
    T = T[:t]
    return T

# TODO: add test cases here for SecretUtil
if __name__ == "__main__":
    # import random as mathrandom
    import time
    group = PairingGroup('MNT159')
    a = SecretUtil(group, False)
    t=13
    n=20
    # print(tInNrandom(t,n)) 
    # ts=time.time()
    x = a.genShares(group.random(), t, n)
    # print("generate shares",time.time()-ts)
    indexArr = tInNrandom(t,n)
    print(indexArr)

    ts=time.time()
    y = a.recoverCoefficients(indexArr)
    
    z=0
    for i in indexArr:
        z += x[i]*y[i]
    # z = x[1]*y[1]+x[3]*y[3]
    print(z==x[0],time.time()-ts)

