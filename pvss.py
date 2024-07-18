# realize fig1
# -*- coding: utf-8 -*-
import time, sys, os
sys.path.append('..') 
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from newsecretutils import SecretUtil
from functools import reduce
import newjson as json
from charm.toolbox.ABEnc import ABEnc, Input, Output
import random
# import setting
# import utils.newjson as json


groupObj = PairingGroup("MNT159")
from config import config

def random_scalar():
    return groupObj.random(ZR)

class PVSS():

    def __init__(self, ID):
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj
        self.g, self.h = json.loads(config['g']), json.loads(config['h'])#self.group.random(G1),self.group.random(G1)
        self.g2 = self.group.random(G2)
        # self.pks={}        
        # print(json.dumps({"g":self.g, "h":self.h}))
        self.ID=ID
        self.sk=random_scalar()
        self.pk=[self.h ** self.sk, self.g2**self.sk]
        self.pks={int(ID):self.pk}
        # self.N=0
        # self.t=0

    def setPK(self, i, pk):
        self.pks[i]=pk

    def hash(self,obj):
        return self.group.hash(str(obj), ZR)

    # PVSS——share
    def share(self,  N, t, s=None):
        self.N=N
        self.t=t
        ts = time.time()

        w = self.group.random(ZR)        
        Pis =  self.util.genShares(w, self.t, self.N)
        if s == None:
            s = self.group.random(ZR)
        
        Com = (self.h ** w) * (self.g ** s)
        # if self.ID == '4':
        #     print(self.g ** s)
        # print(self.h ** w)
        C1 = {}
        # print(self.pks)
        for j in range(1, self.N+1):
            C1[j] = self.pks[j][0] ** Pis[j]
            #print(C1[j])

        C = {"Com": Com, "C1": C1}        
        _s, _w = self.group.random(ZR), self.group.random(ZR)
        # choose a ploy(x)
        _pi = self.util.genShares(_w, self.t, self.N)
        _Com = (self.h ** _w) * (self.g ** _s)
        _C1 = {}
        for j in range(1, self.N + 1):
            _C1[j] = self.pks[j][0] ** _pi[j]
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


    def verify(self, C, proofs):        
        assert(proofs["Cp"]["_Com"] == ((self.g ** proofs["stidle"]) * (self.h ** proofs["wtidle"])) * (C["Com"] ** proofs["c"]))
        
        try:
            for i in proofs["Cp"]["_C1"]:        
                assert(proofs["Cp"]["_C1"][i] == (self.pks[int(i)] ** proofs["pitidle"][i]) * (C["C1"][i] ** proofs["c"]))
        except Exception as e:
            print("self.ID", e)
            open("error.txt", "a").write("self.ID " + json.dumps({"C":C, "proofs":proofs}))
        wtidle = proofs['wtidle']        
        indexArr = [i for i in range(1, self.N+1)]
        y = self.util.recoverCoefficients(indexArr)
        
        z = 0
        for i in proofs["pitidle"]:
            z += proofs["pitidle"][i]*y[int(i)]
    
        assert(z == wtidle) 
        return True

    def preRecon(self, C, i, ski=None):
        if ski == None:
            ski = self.sk

        ci= C["C1"][i]**(1/ski)
        # assert(pair(ci, self.pks[int(i)]) == pair(self.h, C["C1"][i]))
        return ci

    # def testPreRecon(self, C, i, ci):
    
    def recon(self, C, cis):
        # print(cis)
        mycis= {}
        for i in cis:
            assert pair(cis[i], self.pks[int(i)][1]) == pair(self.g2, C["C1"][i])
            if pair(cis[i], self.pks[int(i)][1]) == pair(self.g2, C["C1"][i]):
                mycis[i] = cis[i]
            else:
                print("=========================================================",i, cis[i])

        mui=self.util.recoverCoefficients([int(i) for i in list(mycis.keys())])

        hw = self.group.init(G1, 1)
        for i in mycis:
            # print(type(i),i,mui)
            hw = hw * (mycis[i]** mui[int(i)])
        gs = C["Com"] / hw
        return gs



if __name__ == "__main__":
    
    
    N = len(config['nodes'])
    if len(sys.argv)>1:
        N = int(sys.argv[1])
    t=int((N -1)/3+1)
    sks={i: random_scalar() for i in range(0, N+1)}
    

    pvss = PVSS('3')
    starttime = time.time()
    g1 = pvss.h ** random_scalar()
    print("exponetiation cost %.3f"%(time.time()- starttime))
    
    g2 = pvss.g2 ** random_scalar()
    starttime = time.time()
    pair(g1,g2)
    print("pairing cost %.3f"%(time.time()- starttime))
    
    [pvss.setPK(i, [pvss.h ** sks[i], pvss.g2 ** sks[i]]) for i in range(1, N+1)]
    print("N=%d,t=%d" % (N, t))

    s = groupObj.random(ZR)
    starttime = time.time()
    dist = pvss.share(N,t,s)
    print("pvss.share with %d nodes, cost %.3fs, size: %.2fkB"%(N, time.time()- starttime, len(str(dist))/1024.))
    # print("dis message size:",len(str(trans)))
    #print(dist["proof_sw"])
    ver_C = dist["C"]
    ver_proof = dist["proof_sw"]
    starttime = time.time()    
    ver_result = pvss.verify(ver_C, ver_proof)    
    print("pvss.verify with %d nodes, cost %.2fs"%(N, time.time()- starttime))
    
    if not ver_result:
        print("the verify is false")
        exit(0)

    T=[i for i in range(1, N+1)]
    random.shuffle(T)
    T = T[:t]
    # T=[i for i in range(1, t+1)]

    cis={}
    for i in T:
        cis[i] = pvss.preRecon(dist["C"],i, sks[i])
        # print(len(str(cis[i])))
    starttime = time.time()    
    testgstidle = pvss.recon(dist["C"], cis)    
    print("pvss.reconstruct with %d nodes, cost %.2fs, size: %.2fkB"%(N, time.time()- starttime, len(str(cis))/1024.))
    
    assert(json.loads(config['g'])**s == testgstidle)
