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
        self.g= json.loads(config['g'])#self.group.random(G1),self.group.random(G1)
        # self.g2 = self.group.random(G2)
        # self.pks={}        
        # print(json.dumps({"g":self.g, "h":self.h}))
        self.ID=ID
        self.sk= random_scalar()
        self.pk= self.g**self.sk
        self.pks={int(ID):self.pk}
        # self.N=0
        # self.t=0

    def setPK(self, i, pk):
        self.pks[i]=pk

    def hash(self,obj):
        return self.group.hash(str(obj), ZR)

    # PVSS——share
    def share(self,  N, t, s):
        self.N=N
        self.t=t
        #ts = time.time()

        #w = self.group.random(ZR)        
        Pis =  self.util.genShares(s, self.t, self.N)
        if s == None:
            s = self.group.random(ZR)
        #print(Pis)
        #Com = (self.h ** w) * (self.g ** s)
        # if self.ID == '4':
        #     print(self.g ** s)
        # print(self.h ** w)
        C = {}
        #print(Pis[1])
        #print(self.pks[1])
        # print(self.pks)
        for j in range(1, self.N+1):
            C[j]=self.pks[j] ** Pis[j]
            #print(C1[j])

        sp = self.group.random(ZR)
        Pis1 = self.util.genShares(sp, self.t, self.N)
        Cp = {}
        for j in range(1, self.N+1):
            Cp[j] = self.pks[j] ** Pis1[j]

        c = self.group.hash(str(C) + str(Cp), ZR)
        #print("c:",c)
        stidle = sp - c * s
        #wtidle = _w - c * w
        pitidle = {}
        for i in range(1, self.N+1):
            pitidle[i] = Pis1[i] - c * Pis[i]

        NIZK_proofs = {"Cp": Cp, "c": c, "stidle": stidle, "pitidle": pitidle}
        return {'C': C, 'proof_pi': NIZK_proofs}


    def verify(self, C, proofs):        
        #assert(proofs["Cp"]["_Com"] == ((self.g ** proofs["stidle"]) * (self.h ** proofs["wtidle"])) * (C["Com"] ** proofs["c"]))
        
        try:
            for i in proofs["Cp"]:        
                assert(proofs["Cp"][i] == (self.pks[int(i)] ** proofs["pitidle"][i]) * (C[i] ** proofs["c"]))
        except Exception as e:
            print("self.ID", e)
            open("error.txt", "a").write("self.ID " + json.dumps({"C":C, "proofs":proofs}))

        stidle = proofs['stidle']        
        indexArr = [i for i in range(1, self.N+1)]
        y = self.util.recoverCoefficients(indexArr)
        
        z = 0
        for i in proofs["pitidle"]:
            z += proofs["pitidle"][i]*y[int(i)]
        #print("verify_z:",z)
        assert(z == stidle) 
        return True

    def preRecon(self, C, i, ski=None):
        if ski == None:
            ski = self.sk

        Di= C[i]**(1/ski)
        # assert(pair(ci, self.pks[int(i)]) == pair(self.h, C["C1"][i]))
        return Di

    
    def recon(self, C, cis):
        # print(cis)
        mycis= {}
        """
        for i in cis:
            assert pair(cis[i], self.pks[int(i)]) == pair(self.g, C[i])
            if pair(cis[i], self.pks[int(i)]) == pair(self.g, C[i]):
                mycis[i] = cis[i]
            else:
                print("=========================================================",i, cis[i])
        """
        for i in cis:
            mycis[i] = cis[i]

        mui=self.util.recoverCoefficients([int(i) for i in list(mycis.keys())])

        gs = self.group.init(G1, 1)
        for i in mycis:
            # print(type(i),i,mui)
            gs = gs * (mycis[i]** mui[int(i)])
        #gs = C["Com"] / hw
        return gs



if __name__ == "__main__":
    
    
    N = len(config['nodes'])
    if len(sys.argv)>1:
        N = int(sys.argv[1])
    t=int((N -1)/3+1)
    sks={i: random_scalar() for i in range(0, N+1)}
    
    pvss = PVSS('3')
    starttime = time.time()
    g1 = pvss.g ** random_scalar()
    print("exponetiation cost %.5fs"%(time.time()- starttime))
    
    #g2 = pvss.g2 ** random_scalar()
    #starttime = time.time()
    #pair(g1,g2)
    #print("pairing cost %.3f"%(time.time()- starttime))
    
    [pvss.setPK(i, pvss.g ** sks[i]) for i in range(1, N+1)]
    print("N=%d,t=%d" % (N, t))

    s = groupObj.random(ZR)

    starttime = time.time()
    dist = pvss.share(N,t,s)
    print("pvss.share with %d nodes, cost %.5fs, size: %.2fkB"%(N, time.time()- starttime, len(str(dist))/1024.))
    ver_C = dist["C"]
    ver_proof = dist["proof_pi"]
    #print("stide:",ver_proof["stidle"])

    starttime = time.time()    
    ver_result = pvss.verify(ver_C, ver_proof)    
    print("pvss.verify with %d nodes, cost %.5fs"%(N, time.time()- starttime))
    
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
    print("pvss.reconstruct with %d nodes, cost %.5fs, size: %.2fkB"%(N, time.time()- starttime, len(str(cis))/1024.))

    assert(json.loads(config['g'])**s == testgstidle)
