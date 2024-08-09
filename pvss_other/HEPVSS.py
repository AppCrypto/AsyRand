from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from newsecretutils import SecretUtil
import newjson as json
from charm.toolbox.ABEnc import ABEnc, Input, Output
import random
import time,sys
from config import config
N = int(sys.argv[1])
t=int((N -1)/3+1)


class HEPVSS():
    def elenc(self, M, pk):
        r=self.group.random(ZR)
        return (self.g**r, M * (pk**r))

    def proveEnc(self, w, x, pk):        
        r=self.group.random(G1)
        a=self.elenc(r,pk)
        e=self.hash((x,a))
        z=r*(w**e)
        return (e,z,a)
    def add(self, a, b):
        return (a[0]*b[0], a[1]*b[1])
    def mul(self, a, e):
        return (a[0]**e, a[1]**e)

    def verifyEnc(self, Ci, PfShi,pk,sk):    
        e=PfShi[0]
        z=PfShi[1]
        a=PfShi[2]
        fz=self.elenc(z, pk)
        _ex=self.mul(Ci, -e)
        fz_ex=self.add(fz, _ex)#the ElGamal CT of r
        # fz_ex and a are the same ciphertext of r
        res0=self.add(fz_ex, self.mul(a,-1))
        print(res0[1])
        # print(res0[1]/(res0[0]**sk))
        # assert(e==self.hash((Ci,fz_ex)))
        return True
    def proveDec(self):
        r=self.group.random(ZR)
        a=self.g**r
        e=self.hash((pk,a))
        z=r+e*self.sks[i]
        return (e,z)
    def verifyDec(self,A,PfDec):
        # for i in range(1,N+1):
        #     e=PfDec[i][0]
        #     z=PfDec[i][1]
        #     x=pk
        #     assert(e==self.hash((x,z-self.add(z, x*))))
        return True
        
    def hash(self,obj):
        return self.group.hash(str(obj), ZR)

    def __init__(self, groupObj):        
        global util, group
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj
        
        self.g= json.loads(config['g'])
    
        self.sks=[self.group.random(ZR) for i in range(0,N+1)]
        self.pks=[self.g**self.sks[i] for i in range(0,N+1)]
        self.S=self.group.random(G1)
        self.codeword = [self.group.init(ZR, 1)]
        for i in range(1, N + 1):
            vi = self.group.init(ZR, 1)
            for j in range(1, N + 1):
                if i != j:
                    vi = vi * 1 / (i - j)
            self.codeword.append(self.group.init(ZR, vi))
        self.index=1

    def distribute(self):
        starttime = time.time()
        s=self.group.random(ZR)        
        self.S=self.g**s
        
        shares = self.util.genShares(s, t, N)
        # print(s,shares,len(shares))
        A=[0]
        A.extend([self.g ** shares[i] for i in range(1, N+1)])
        # print(shat)
        C=[0]
        C.extend([self.elenc(A[i], self.pks[i]) for i in range(1, N+1)])
        
        PfSh=[0]
        for i in range(1,N+1):
            PfSh.append(self.proveEnc(A[i],C[i], self.pks[i]))
        dist={"C":C,"PfSh":PfSh}
        print("HEPVSS distribute cost %.3fs, size %.2fkB"%(time.time()- starttime, len(str(dist))/1024.))
        return dist


    def verify(self,dist):
        starttime = time.time()
        for i in range(1,N+1):
            self.verifyEnc(dist["C"][i],dist["PfSh"][i],self.pks[i],self.sks[i])
        print("HEPVSS verification cost %.3fs"%(time.time()- starttime))
        return True

    def preRecon(self, Ci, i):
        Ai= Ci[1]/(Ci[0]**self.sks[i])
        PfDec=[0]
        for i in range(1,N+1):
            PfSh.append(self.proveDec(Ci))
        
        reconi={"Ai":Ai,"PfDec":PfDec}
        return reconi
        

    def reconstruct(self, recon, C):
        starttime = time.time()
        for i in recon:
            reconi = recon[i]
            c = self.group.hash(str(self.pks[self.index])+str(C[i]-reconi["Ai"]), ZR)       
            
            if reconi["PfDec"][0] != (self.g**reconi["PfDec"][2]) * (self.pks[self.index]**c) or \
                reconi["PfDec"][1] != ((self.pks[i])**reconi["PfDec"][2]) * ((C[i]-reconi["Ai"])**c):
                print("fail to verify")
                return False
        
        indexArr = [i for i in range(1,N+1)]

        # random.shuffle(indexArr)
        indexArr=indexArr[0:t]
        y = self.util.recoverCoefficients(indexArr)
        z=self.group.init(G1,1)
        for i in indexArr:    
            z *= recon[i]["Ai"]**y[i]    
        print("HEPVSS reconstruction cost %.3fs size: %.2fkB"%((time.time()- starttime), len(str(recon))/1024.))
        if self.S!=z: 
            print("HEPVSS fail to reconstruct")
            return -2
        return 1





if __name__ == "__main__":    
    
    N = int(sys.argv[1])
    t=int((N -1)/3+1)
    groupObj = PairingGroup("MNT159")

    dhp = HEPVSS(groupObj)    
    dist = dhp.distribute()
    dhp.verify(dist)
    # dhp.reconstruct(dist)
