from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from newsecretutils import SecretUtil
import newjson as json
from charm.toolbox.ABEnc import ABEnc, Input, Output
import random
import time,sys
from config import config

N = int(sys.argv[1])
t=int((N -1)/3+1)

class DHPVSS():
    def ElGamal(self, M, pk):
        r=self.group.random(ZR)
        return (self.g**r, M * (pk**r))
    def prove(self, w, x, f, pk):
        
        r=self.group.random(G1)
        a=self.ElGamal(r,pk)
        e=self.hash((x,a))
        # print(type(r))
        z=(a[0]*x[0], a[1]*x[1])
        return (e,z)

    def hash(self,obj):
        return self.group.hash(str(obj), ZR)

    def __init__(self, groupObj):        
        global util, group
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj
        
        self.g= json.loads(config['g'])
    
        self.sks=[self.group.random(ZR) for i in range(0,N+1)]
        self.pks=[self.g**self.sks[i] for i in range(0,N+1)]
        self.omega=[self.g**self.sks[i] for i in range(0,N+1)]
        self.S=self.group.random(G1)
        self.codeword = [self.group.init(ZR, 1)]
        for i in range(1, N + 1):
            vi = self.group.init(ZR, 1)
            for j in range(1, N + 1):
                if i != j:
                    vi = vi * 1 / (self.group.init(ZR, i) - j)                    
            self.codeword.append(vi)
        # print(self.codeword)
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
        C.extend([(self.pks[i] ** self.sks[self.index]) * A[i] for i in range(1, N+1)])
        
        mstar=self.group.init(ZR, 1)      #todo
        V=self.group.init(G1, 1)
        U=self.group.init(G1, 1)
        for i in range(1,  N+1):
            V = V* (C[i]**self.codeword[i])
            U = U* (self.pks[i]**self.codeword[i])
        
        w = self.group.random(ZR)        
        c = self.group.hash(str(U)+str(V), ZR)        
        z,a1,a2=self.g**w, U**w, w - self.sks[self.index] * c  
        PfSh=[z, a1, a2]
        dist={"C":C,"A":A,"PfSh":PfSh}
        print("DHPVSS distribute cost %.3fs, size %.2fkB"%(time.time()- starttime, len(str(dist))/1024.))
        return dist


    def verify(self,dist):
        starttime = time.time()
        mstar=self.group.init(ZR, 1)      #todo
        V=self.group.init(G1, 1)
        U=self.group.init(G1, 1)
        for i in range(1,  N+1):
            V = V* (dist["C"][i]**self.codeword[i])
            U = U* (self.pks[i]**self.codeword[i])

        # Check DLEQ proofs
        c = self.group.hash(str(U)+str(V), ZR)       
        
        if dist["PfSh"][0] != (self.g**dist["PfSh"][2]) * (self.pks[self.index]**c) or \
            dist["PfSh"][1] != (U**dist["PfSh"][2]) * (V**c):
            print("fail to verify")
            return False
               
        print("DHPVSS verification cost %.3fs"%(time.time()- starttime))
        
        return True

    def preRecon(self, Ci, i):
        Ai= Ci/(self.pks[self.index]**self.sks[i])
        w = self.group.random(ZR)        
        c = self.group.hash(str(self.pks[self.index])+str(Ci-Ai), ZR)        
        z,a1,a2=self.g**w, self.pks[i]**w, w - self.sks[self.index] * c  
        PfDec=[z, a1, a2]
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
        print("DHPVSS reconstruction cost %.3fs size: %.2fkB"%((time.time()- starttime), len(str(recon))/1024.))
        if self.S!=z: 
            print("DHPVSS fail to reconstruct")
            return -2
        return 1


if __name__ == "__main__":    
    
    
    groupObj = PairingGroup("MNT159")
    hep = DHPVSS(groupObj)
    # M=hep.group.random(G1)
    # hep.prove(M, hep.ElGamal(M, hep.pks[1]), hep.ElGamal, hep.pks[1])
    dist = hep.distribute()
    hep.verify(dist)
    recon={}
    for i in range(1, t+1):
        recon[i]=hep.preRecon(dist["C"][i],i)
    hep.reconstruct(recon, dist["C"])


