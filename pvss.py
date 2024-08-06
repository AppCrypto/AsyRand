# realize fig1
# -*- coding: utf-8 -*-
import time, sys, os
sys.path.append('..') 
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from newsecretutils import SecretUtil
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

    def __init__(self, ID, N, t):
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj
        self.g, self.h = json.loads(config['g']), json.loads(config['h'])#self.group.random(G1),self.group.random(G1)
        self.g2 = json.loads(config['g2'])
        # self.pks={}        
        # print(json.dumps({"g":self.g, "h":self.h,"g2":self.g2}))
        self.ID=ID
        self.sk=random_scalar()
        self.pk=[self.g ** self.sk, self.g2**self.sk]
        self.pks={int(ID):self.pk}
        self.N=N
        self.t=t
        self.coeff = self.util.recoverCoefficients([i for i in range(1, N+1)])
        

    def setPK(self, i, pk):
        self.pks[i]=pk

    def hash(self,obj):
        return self.group.hash(str(obj), ZR)

    # PVSS——share
    def share(self, s=None):
        ts = time.time()

        if s == None:
            s = self.group.random(ZR)
        
        Pis =  self.util.genShares(s, self.t, self.N)
        
        C1 = {}
        # print(self.pks)
        for j in range(1, self.N+1):
            C1[j] = self.pks[j][0] ** Pis[j]
            #print(C1[j])

        C = {"C1": C1}        
        _s = self.group.random(ZR)
        # choose a ploy(x)
        _pi = self.util.genShares(_s, self.t, self.N)
        
        _C1 = {}
        for j in range(1, self.N + 1):
            _C1[j] = self.pks[j][0] ** _pi[j]
        #print(_C1[1])
        Cp = {"_C1": _C1}
        c = self.group.hash(str(C) + str(Cp), ZR)
        stidle = _s - c * s        
        pitidle = {}
        for i in range(1, self.N+1):
            pitidle[i] = _pi[i] - c * Pis[i]

        
        NIZK_proofs = {"Cp": Cp, "c": c, "stidle": stidle, "pitidle": pitidle}
        return {'C': C, 'pi': NIZK_proofs}


    def verify(self, C, proofs):        
        starttime = time.time()
        for i in proofs["Cp"]["_C1"]:        
            if int(i) not in self.pks:
                 print(self.ID, "verify error not in self.pks========================",i)
            if (proofs["Cp"]["_C1"][i] != (self.pks[int(i)][0] ** proofs["pitidle"][i]) * (C["C1"][i] ** proofs["c"])):
                print(self.ID, "verify error========================",i)
                break
        # print("pvss.verify1 with cost %.3fs"%( time.time()- starttime))

        starttime = time.time()
        stidle = proofs['stidle']        
        indexArr = [i for i in range(1, self.N+1)]
        # y = self.util.recoverCoefficients(indexArr)
        
        # print("pvss.verify1.1 with cost %.3fs"%( time.time()- starttime))

        z = 0
        for i in proofs["pitidle"]:
            z += proofs["pitidle"][i]*self.coeff[int(i)]
    
        assert(z == stidle)            
        # print("pvss.verify2 with cost %.3fs"%( time.time()- starttime))
        return True

    def preRecon(self, C, i, ski=None):
        if ski == None:
            ski = self.sk

        ci= C["C1"][i]**(1/ski)
        # assert(pair(ci, self.pks[int(i)]) == pair(self.g2, C["C1"][i]))
        return ci

    # def testPreRecon(self, C, i, ci):
    
    def recon(self, C, cis):
        # print(cis)
        mycis= {}
        for i in cis:
            
            if pair(cis[i], self.pks[int(i)][1]) == pair(self.g2, C["C1"][i]):
                mycis[i] = cis[i]
            else:
                print("recon error=========================================================",i, cis[i],C["C1"][i],self.g2)

        mui=self.util.recoverCoefficients([int(i) for i in list(mycis.keys())])

        gs = self.group.init(G1, 1)
        for i in mycis:
            # print(type(i),i,mui)
            gs = gs * (mycis[i]** mui[int(i)])
        
        return gs



if __name__ == "__main__":    
    
    N = len(config['nodes'])
    if len(sys.argv)>1:
        N = int(sys.argv[1])
    t=int((N -1)/3+1)
    sks={i: random_scalar() for i in range(0, N+1)}
    
    #print(sks)
    pvss = PVSS('3',N,t)
    starttime = time.time()
    g1 = pvss.g ** random_scalar()
    print("exponetiation cost %.3f"%(time.time()- starttime))

    # starttime = time.time()
    # inv = 1/(groupObj.init(ZR, 2) - groupObj.init(ZR, 200))
    # print("inverse() cost %.3f"%(time.time()- starttime))
    
    # g2 = pvss.g2 ** random_scalar()
    # starttime = time.time()
    # pair(g1,g2)
    # print("pairing cost %.3f"%(time.time()- starttime))
    
    [pvss.setPK(i, [pvss.g ** sks[i], pvss.g2 ** sks[i]]) for i in range(1, N+1)]
    print("N=%d,t=%d" % (N, t))

    s = groupObj.random(ZR)
    # s= groupObj.init(ZR, 1)
    starttime = time.time()
    dist = pvss.share(s)
    print("pvss.share with cost %.3fs, size: %.2fkB"%(time.time()- starttime, len(str(dist))/1024.))
    # print("dis message size:",len(str(trans)))
    #print(dist["pi"])    
    starttime = time.time()    
    ver_result = pvss.verify(dist["C"], dist["pi"])    
    print("pvss.verify with cost %.3fs"%( time.time()- starttime))
    
    # print(ver_result)
        
    T=[i for i in range(1, N+1)]
    random.shuffle(T)
    T = T[:t]
    # T=[i for i in range(1, t+1)]

    cis={}
    for i in T:
        cis[i] = pvss.preRecon(dist["C"],i, sks[i])
        # print(len(str(cis[i])))

    starttime = time.time()    
    gs = pvss.recon(dist["C"], cis)    
    print("pvss.reconstruct with cost %.3fs, size: %.2fkB"%(time.time()- starttime, len(str(cis))/1024.))
    
    
    if pvss.g ** s != gs:
       print("pvss fail to reconstruct")
