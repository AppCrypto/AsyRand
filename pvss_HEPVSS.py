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
    def elenc(self, Ai, pki, rhoi):
        return (self.g**rhoi, Ai * (pki**rhoi))

    def proveEnc(self, shares, rho, pks, A, C):
        PfSh={}
        sp=self.group.random(ZR)        
        sharesp = self.util.genShares(sp, t, N)
        Ap=[0]
        Ap.extend([self.g ** sharesp[i]  for i in range(1, N+1)])
        rhop=[0]
        rhop.extend([self.group.random(ZR) for i in range(1, N+1)])
        
        # print(len(Ap),len(pks),len(rhop),len(rho))
        for i in range(1, N+1):            
            a=self.elenc(Ap[i],pks[i],rhop[i])
            e=self.hash((C[i],a))
            z=(Ap[i] * (A[i]**e), rhop[i]+(rho[i]*e))
            PfSh[i]=(e,z)
        return PfSh
    def add(self, a, b):
        return (a[0]*b[0], a[1]*b[1])
    def mul(self, a, e):
        return (a[0]**e, a[1]**e)

    def verifyEnc(self, C, PfSh):    
        for i in range(1, N+1): 
            e=PfSh[i][0]
            z=PfSh[i][1]
            fz=self.elenc(z[0],self.pks[i], z[1])
            _ex=self.mul(C[i], -e)
            fz_ex=self.add(fz, _ex) 
            if e!=self.hash((C[i],fz_ex)):
                return False
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
        A.extend([self.g ** shares[i]  for i in range(1, N+1)])
        rho=[0]
        rho.extend([self.group.random(ZR) for i in range(1, N+1)])
        
        C=[0]
        C.extend([self.elenc(A[i], self.pks[i], rho[i]) for i in range(1, N+1)])
                
        PfSh= self.proveEnc(shares, rho, self.pks, A, C)
            
        dist={"C":C,"PfSh":PfSh}
        print("HEPVSS distribute cost %.3fs, size %.2fkB"%(time.time()- starttime, len(str(dist))/1024.))
        return dist


    def proveDec(self,sk):
        skp=self.group.random(ZR)
        a=self.g**skp
        e=self.hash((self.pk,a))
        z=skp+e*sk
        return (e,z)

    def verify(self,dist):
        starttime = time.time()
        res = self.verifyEnc(dist["C"],dist["PfSh"])
        print(f"HEPVSS verification ({res}) cost %.3fs"%(time.time()- starttime))
        return True

    def preRecon(self, Ci, i):
        Ai= (Ci[0]**self.sks[i])
        skp=self.group.random(ZR)        
        a=Ci[0]**skp
        e=self.hash((self.pks[i],a))
        # print(i, a, e)
        z=skp+e*self.sks[i]
        # print(i, Ci[0]**z/(Ai**e), e)
        return (Ai,e,z)
        

    def reconstruct(self, dist):
        recon={}
        C=dist["C"]
        for i in range(1, N+1):
            recon[i] = self.preRecon(C[i],i)            
        
        starttime = time.time()     
        for i in range(1, N+1):
            Ai,e,z = recon[i]
            Aiz= (C[i][0]**z)
            if e != self.hash((self.pks[i], Aiz/(Ai**e))):
                print("HEPVSS fail to proveDec", i)
                return
           

        indexArr = [i for i in range(1,N+1)]
        random.shuffle(indexArr)
        indexArr=indexArr[0:t]
        y = self.util.recoverCoefficients(indexArr)
        z=self.group.init(G1,1)
        for i in indexArr:    
            Ai= C[i][1]/C[i][0]**self.sks[i]
            z *= Ai**y[i]    
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
    dhp.reconstruct(dist)
