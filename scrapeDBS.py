from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from newsecretutils import SecretUtil
import newjson
from charm.toolbox.ABEnc import ABEnc, Input, Output
import random
import time,sys


N = int(sys.argv[1])
t=int((N -1)/3+1)


class SCRAPE():
    

    # setup()
    def __init__(self, groupObj):        
        global util, group
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj
        
        self.g, self.h = self.group.random(G1), self.group.random(G2)
        # self.g.initPP(); gp.initPP()
        
        # shareholders are in [1, N]
        self.sks=[self.group.random(ZR) for i in range(0,N+1)]
        self.pks=[self.h**self.sks[i] for i in range(0,N+1)]
        self.pksp=[self.g**self.sks[i] for i in range(0,N+1)]
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
        self.S=self.h**s

        
        shares = self.util.genShares(s, t, N)
        # print(s,shares,len(shares))
        vs=[0]
        vs.extend([self.g ** shares[i] for i in range(1, N+1)])
        # print(shat)
        shat=[0]
        shat.extend([self.pks[i]** shares[i] for i in range(1, N+1)])
        
        res={"shat":shat,"vs":vs}
        # print("GT",len(str(self.group.random(GT))))
        # print("G1",len(str(self.group.random(G1))))
        # print("G2",len(str(self.group.random(G2))))
        
        print("ScrapeDBS dis message size %.3fs, cost %.2fkB"%(time.time()-starttime, len(str(res))/1024.))
        return res


    def verify(self, dis):
        starttime = time.time()
        
        for i in range(1, N+1):
            if pair(self.g,dis["shat"][i]) != pair(dis["vs"][i],self.pks[i]):
                return False


        # reed solomon check        
        v=self.group.init(G1,1)
        
        for i in range(1, N+1):
            v=v * (dis["vs"][i]**self.codeword[i])
        if v != self.group.init(G1,1):
            return False
        print("ScrapeDBS verification cost %.3fs"%(time.time()- starttime))
        return True

    def reconstruct(self,dis):
        
        # g^s sent by shareholders
        stidle=[self.group.init(G2,1)]

        for i in range(1, t+1):
            stidle.append(dis["shat"][i]**(1/self.sks[i]))
        # print(len(str(stidle[1]))) 
        
        recon={}
        recon["stidle"]=stidle
        # print("ScrapeDBS rec message size %.2fkB"%(len(str(recon))/1024.))
        
        # Check Pairing by the recover
        
        starttime=time.time()
        for i in range(1, t+1):
            if pair(self.pksp[i], stidle[i]) != pair(self.g, dis["shat"][i]):
                return -1        

        indexArr = [i for i in range(1,t+1)]

        # random.shuffle(indexArr)

        indexArr=indexArr[0:t]
        y = self.util.recoverCoefficients(indexArr)
        z=self.group.init(G2,1)
        for i in indexArr:    
            z *= stidle[i]**y[i]    
        print("ScrapeDBS reconstruction cost %.3fs size %.2fkB"%(time.time()- starttime, (len(str(recon))/1024.)))
        if self.S!=z: 
            print("ScrapeDBS fail to reconstruct")
            return -2
        return z

groupObj = PairingGroup("MNT159")
scrape = SCRAPE(groupObj)
print("N=%d,t=%d"%(N,t))
dis= scrape.distribute()
# print(scrape.verify(dis["shat"], dis["vs"]))
scrape.verify(dis)
scrape.reconstruct(dis)


