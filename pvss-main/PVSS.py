# realize fig1
# -*- coding: utf-8 -*-
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from utils.newsecretutils import SecretUtil
from functools import reduce
import utils.newjson as newjson
from charm.toolbox.ABEnc import ABEnc, Input, Output
import random
import time, sys
import setting

ret = {}
keyV = 1
assertExe = True

N = setting.N
t = setting.t


class PVSS():
    def random_scalar(self):
        return self.group.random(ZR)


    def __init__(self, groupObj):
        # global util, group
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj
        self.g, self.h = self.group.random(G1), self.group.random(G1)
        self.sks={i: self.random_scalar() for i in range(0, N+1)}
        self.pks={i: self.h ** self.sks[i] for i in range(0, N+1)}
        # print(self.sks)

    # PVSS——share
    def share(self, s=None):
        ts = time.time()

        w = self.group.random(ZR)        
        Pis =  self.util.genShares(w, t, N)
        if s == None:
            s = self.group.random(ZR)
        
        Com = (self.h ** w) * (self.g ** s)
        print(self.g ** s)
        # print(self.h ** w)
        C1 = {}
        for j in range(1, N+1):
            C1[j] = self.pks[j] ** Pis[j]
            #print(C1[j])

        C = {"Com": Com, "C1": C1}        
        # # create a NIZK proofs
        # proof_sw = self.nizkabe.createproofs(C, access_policy)
        # generate the proofs
        _s, _w = self.group.random(ZR), self.group.random(ZR)
        # choose a ploy(x)
        _pi = self.util.genShares(_w, t, N)
        _C0 = (self.h ** _w) * (self.g ** _s)
        _C1 = {}
        for j in range(1, N + 1):
            _C1[j] = self.pks[j] ** _pi[j]
        #print(_C1[1])
        Cp = {"_C0": _C0, "_C1": _C1}
        # self.Cp = Cp
        c = self.group.hash(str(C) + str(Cp), ZR)
        _s1 = _s - c * s
        _w1 = _w - c * w
        _pi1 = {}
        for i in range(1, N+1):
            _pi1[i] = _pi[i] - c * Pis[i]
        NIZK_proofs = {"Cp": Cp, "c": c, "_s1": _s1, "_w1": _w1, "_pi1": _pi1}
        return {'C': C, 'proof_sw': NIZK_proofs}
        # return { 'Com':Com,'C1':C1}


    def ver(self, Com, proofs):
        ver_result = True
        if proofs["Cp"]["_C0"] != ((self.g ** proofs["_s1"]) * (self.h ** proofs["_w1"])) * (Com["Com"] ** proofs["c"]):
            ver_result = False
        # COMPLIE The verify of step 1
        #print(proofs["Cp"]["_C1"])
        for i in range(1, N+1):
            #print(proofs["_pi1"])
            #print(proofs["Cp"]["_C1"][i])
            #if proofs["Cp"]["_C1"][i] != (self.pks[i] ** proofs["_pi1"][i]) * (Com["C1"][i] ** proofs["c"]):
            if proofs["Cp"]["_C1"][i] != (self.pks[i] ** proofs["_pi1"][i]) * (Com["C1"][i] ** proofs["c"]):
                ver_result = False
            #else:
                #print("the verify of _C1%d is true" % i)

        _gs = self.g ** proofs['_s1']
        #print((_gs))

        T = [i for i in range(1, N + 1)]
        random.shuffle(T)
        T = T[:t]
        # T=[i for i in range(1, t+1)]
        _cis = {}
        for i in T:
            _cis[i] = self.h ** proofs["_pi1"][i]
        _mui = self.util.recoverCoefficients(list(_cis.keys()))
        _hw = self.group.init(G1, 1)
        for i in _cis:
            _hw = _hw * (_cis[i]** _mui[i])

        gs_ver = (proofs["Cp"]["_C0"]/(Com["Com"] ** proofs["c"])) / _hw
        #print(gs_ver)
        if _gs != gs_ver:
            ver_result = False
            #print("step3 is false!!")
        print("the verification of proofs has been completed!!")
        return ver_result

    def preRecon(self, C, ski, i):
        # print(C["C1"][i]**(1/ski))
        return C["C1"][i]**(1/ski)

    
    def recon(self, C, cis):
        for i in cis:
            assert pair(cis[i], self.pks[i]) == pair(self.h, C["C1"][i])

        mui=self.util.recoverCoefficients(list(cis.keys()))

        hw = self.group.init(G1, 1)
        for i in cis:
            hw = hw * (cis[i]** mui[i])
        # print(hw)
        gs = C["Com"] / hw
        return gs



if __name__ == "__main__":
    groupObj = PairingGroup(setting.curveName)
    
    pvss = PVSS(groupObj)
    print("N=%d,t=%d" % (N, t))
    dist = pvss.share()
    # print("dis message size:",len(str(trans)))
    #print(dist["proof_sw"])
    ver_C = dist["C"]
    ver_proof = dist["proof_sw"]
    ver_result = pvss.ver(ver_C, ver_proof)
    if not ver_result:
        print("the verify is false")
        exit(0)

    T=[i for i in range(1, N+1)]
    random.shuffle(T)
    T = T[:t]
    # T=[i for i in range(1, t+1)]

    cis={}
    for i in T:
        cis[i] = pvss.preRecon(dist["C"], pvss.sks[i],i)
    
    test_gs = pvss.recon(dist["C"], cis)
    print(test_gs)
