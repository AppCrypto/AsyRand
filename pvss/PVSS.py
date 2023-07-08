# realize fig1
# -*- coding: utf-8 -*-
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from utils.newsecretutils import SecretUtil
from functools import reduce
import utils.newjson as newjson
from charm.toolbox.ABEnc import ABEnc, Input, Output
import random
import time, sys, os
# import setting
import utils.newjson as json

ret = {}
keyV = 1
assertExe = True

# config = json.loads(open("../NodeConfiguration.json","r").read())
# N = len(config["nodes"])
# t=int(N/3)+1
groupObj = PairingGroup("SS512")

def random_scalar():
    return groupObj.random(ZR)

class PVSS():

    def __init__(self, groupObj, N, t):
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj
        self.g, self.h = self.group.random(G1), self.group.random(G1)
        self.pks={}
        self.N=N
        self.t=t
        self.sk=random_scalar()
        self.pk=self.h ** random_scalar()

    def setPK(self, i, pk):
        self.pks[i]=pk


    # PVSS——share
    def share(self, s=None):
        ts = time.time()

        w = self.group.random(ZR)        
        Pis =  self.util.genShares(w, self.t, self.N)
        if s == None:
            s = self.group.random(ZR)
        
        Com = (self.h ** w) * (self.g ** s)
        print(self.g ** s)
        # print(self.h ** w)
        C1 = {}
        for j in range(1, self.N+1):
            C1[j] = self.pks[j] ** Pis[j]
            #print(C1[j])

        C = {"Com": Com, "C1": C1}        
        _s, _w = self.group.random(ZR), self.group.random(ZR)
        # choose a ploy(x)
        _pi = self.util.genShares(_w, self.t, self.N)
        _Com = (self.h ** _w) * (self.g ** _s)
        _C1 = {}
        for j in range(1, self.N + 1):
            _C1[j] = self.pks[j] ** _pi[j]
        #print(_C1[1])
        Cp = {"_Com": _Com, "_C1": _C1}
        c = self.group.hash(str(C) + str(Cp), ZR)
        stidle = _s - c * s
        wtidle = _w - c * w
        pitidle = {}
        for i in range(1, self.N+1):
            pitidle[i] = _pi[i] - c * Pis[i]
        NIZK_proofs = {"Cp": Cp, "c": c, "stidle": stidle, "wtidle": wtidle, "pitidle": pitidle}
        return {'C': C, 'proof_sw': NIZK_proofs}


    def verify(self, Com, proofs):        
        assert(proofs["Cp"]["_Com"] == ((self.g ** proofs["stidle"]) * (self.h ** proofs["wtidle"])) * (Com["Com"] ** proofs["c"]))
            
        for i in range(1, self.N+1):
            assert(proofs["Cp"]["_C1"][i] == (self.pks[i] ** proofs["pitidle"][i]) * (Com["C1"][i] ** proofs["c"]))
            
        wtidle = proofs['wtidle']        
        indexArr = [i for i in range(1, self.N+1)]
        y = self.util.recoverCoefficients(indexArr)
        z = 0
        for i in indexArr:
            z += proofs["pitidle"][i]*y[i]
    
        assert(z == wtidle) 
        return True

    def preRecon(self, C, ski, i):
        return C["C1"][i]**(1/ski)

    
    def recon(self, C, cis):
        for i in cis:
            assert pair(cis[i], self.pks[i]) == pair(self.h, C["C1"][i])

        mui=self.util.recoverCoefficients(list(cis.keys()))

        hw = self.group.init(G1, 1)
        for i in cis:
            hw = hw * (cis[i]** mui[i])
        gs = C["Com"] / hw
        return gs



if __name__ == "__main__":

    pvss = PVSS(groupObj, 22, 7)
    sks={i: random_scalar() for i in range(0, pvss.N+1)}
    [pvss.setPK(i, pvss.h ** sks[i]) for i in range(1, pvss.N+1)]
    print("N=%d,t=%d" % (pvss.N, pvss.t))
    dist = pvss.share()
    # print("dis message size:",len(str(trans)))
    #print(dist["proof_sw"])
    ver_C = dist["C"]
    ver_proof = dist["proof_sw"]
    ver_result = pvss.verify(ver_C, ver_proof)
    if not ver_result:
        print("the verify is false")
        exit(0)

    T=[i for i in range(1, pvss.N+1)]
    random.shuffle(T)
    T = T[:pvss.t]
    # T=[i for i in range(1, t+1)]

    cis={}
    for i in T:
        cis[i] = pvss.preRecon(dist["C"], sks[i],i)
    
    testgstidle = pvss.recon(dist["C"], cis)
    print(testgstidle)
