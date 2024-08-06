from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from newsecretutils import SecretUtil
import newjson
from charm.toolbox.ABEnc import ABEnc, Input, Output
import random
import time,sys


N = int(sys.argv[1])
t=int((N -1)/3+1)


class SCRAPE():
    # def dleq(self, g, y1, pks, y2, shares):
    #     """ DLEQ... discrete logarithm equality
    #     Proofs that the caller knows alpha such that y1[i] = x1[i]**alpha and y2[i] = x2[i]**alpha
    #     without revealing alpha.
    #     """
    #     w = self.group.random(ZR)
    #     z=[0 for i in range(0,len(y1))]
    #     a1=[0 for i in range(0,len(y1))]
    #     a2=[0 for i in range(0,len(y1))]
    #     c = self.group.hash(str(y1)+str(y2), ZR)
        
    #     for i in range(1, len(z)):
    #         a1[i] = g**w
    #         a2[i] = pks[i]**w        
    #         z[i] = w - shares[i] * c    
        
    #     return {"g":g, "y1":y1, "pks":pks, "y2":y2, "c":c, "a1":a1, "a2":a2, "z":z}


    # def dleq_verify(self, g, y1, pks, y2, c, a1, a2, z):
    #     for i in range(1, N+1):
    #         if a1[i] != (g**z[i]) * (y1[i]**c) or a2 !=pks** z[i] * y2[i] **c:
    #             return False
    #     return True




    # setup()
    def __init__(self, groupObj):        
        global util, group
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj
        
        self.g, self.gp = self.group.random(G1), self.group.random(G2)
        # self.g.initPP(); gp.initPP()
        
        # shareholders are in [1, N]
        self.sks=[self.group.random(ZR) for i in range(0,N+1)]
        self.pks=[self.g**self.sks[i] for i in range(0,N+1)]
        self.S=self.group.random(G1)
        self.codeword=[self.group.init(ZR,1)]
        for i in range(1, N+1):            
            vi = self.group.init(ZR,1)
            for j in range(1,N+1):
                if i!=j:
                    vi=vi*1/(i-j)  
            self.codeword.append(self.group.init(ZR,vi))
        
    def distribute(self):
        starttime = time.time()
        s=self.group.random(ZR)        
        self.S=self.g**s
        
        shares = self.util.genShares(s, t, N)
        # print(s,shares,len(shares))
        vs=[0]
        vs.extend([self.g ** shares[i] for i in range(1, N+1)])
        # print(shat)
        shat=[0]
        shat.extend([self.pks[i]** shares[i] for i in range(1, N+1)])
        
        # DLEQ proofs
        w = self.group.random(ZR)
        z,a1,a2=[0 for i in range(0,len(shares))],[0 for i in range(0,len(shares))],[0 for i in range(0,len(shares))]
        c = self.group.hash(str(vs)+str(shat), ZR)
        
        for i in range(1, len(z)):
            a1[i] = self.g**w
            a2[i] = self.pks[i]**w        
            z[i] = w - shares[i] * c    
        
        dleqPrfs= {"c":c, "a1":a1, "a2":a2, "z":z}
        
        dist=dleqPrfs.copy()
        dist["shat"]=shat
        dist["vs"]=vs
        print("ScrapeDDH distribute cost %.3fs, size %.2fkB"%(time.time()- starttime, len(str(dist))/1024.))
        return dist


    def verify(self,dist):
        starttime = time.time()
        # Check DLEQ proofs
        c = self.group.hash(str(dist["vs"])+str(dist["shat"]), ZR)
        for i in range(1, N+1):
            if dist["a1"][i] != (self.g**dist["z"][i]) * (dist["vs"][i]**c)\
                or dist["a2"][i] !=self.pks[i]** dist["z"][i] * (dist["shat"][i] **c):
                print("return false")
                return False

        # reed solomon check
        starttime2 = time.time()
        v=self.group.init(G1,1)
        
        for i in range(1, N+1):
            v=v * (dist["vs"][i]**self.codeword[i])
        if v != self.group.init(G2,1):
            return False
        print("ScrapeDDH verification cost %.3fs"%(time.time()- starttime))
        # print("ScrapeDDH verification.codeword cost %.3fs"%(time.time()- starttime2))
        return True

    def reconstruct(self, dist):
        
        # DLEQ proofs by shareholders
        stidle=[self.group.init(G1,1)]
        for i in range(1, t+1):
            stidle.append(dist["shat"][i]**(1/self.sks[i]))
        
        w = self.group.random(ZR)
        z,a1,a2=[0 for i in range(0,len(self.sks))],[0 for i in range(0,len(self.sks))],[0 for i in range(0,len(self.sks))]
        c = self.group.hash(str(self.pks)+str(dist["shat"]), ZR)
        
        for i in range(1, t+1):
            a1[i] = self.g**w
            a2[i] = stidle[i]**w        
            z[i] = w - self.sks[i] * c    
        
        dleqPrfs= {"c":c, "a1":a1, "a2":a2, "z":z}        
        recon=dleqPrfs.copy()
        recon["stidle"]=stidle
        # print("rec message size:",len(str(recon))/1024.)        
        
        # Check DLEQ proofs by the recover
        starttime=time.time()
        c = self.group.hash(str(self.pks)+str(dist["shat"]), ZR)
        for i in range(1, t+1):
            if recon["a1"][i] != (self.g**recon["z"][i]) * (self.pks[i]**c)\
                or recon["a2"][i] !=stidle[i]** recon["z"][i] * (dist["shat"][i] **c):
                return -1
        

        indexArr = [i for i in range(1,N+1)]

        # random.shuffle(indexArr)
        indexArr=indexArr[0:t]
        y = self.util.recoverCoefficients(indexArr)
        z=self.group.init(G1,1)
        for i in indexArr:    
            z *= stidle[i]**y[i]    
        print("ScrapeDDH reconstruction cost %.3fs size: %.2fkB"%((time.time()- starttime), len(str(recon))/1024.))
        if self.S!=z: 
            print("ScrapeDDH fail to reconstruct")
            return -2
        return z

groupObj = PairingGroup("MNT159")
scrape = SCRAPE(groupObj)
print("N=%d,t=%d"%(N,t))
dis= scrape.distribute()
scrape.verify(dis)
scrape.reconstruct(dis)



