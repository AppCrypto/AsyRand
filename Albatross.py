from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, GT, pair
from newsecretutils import SecretUtil
import newjson as newjson
from charm.toolbox.ABEnc import ABEnc, Input, Output
import random
import time, sys


N = int(sys.argv[1])
t=int((N -1)/3+1)

class PPVSS():

    # setup()
    def __init__(self, groupObj):
        global util, group
        self.util = SecretUtil(groupObj, verbose=False)
        self.group = groupObj

        self.g = self.group.random(G1)
        
        # shareholders are in [1, N]
        self.sks = [self.group.random(ZR) for i in range(0, N + 1)]
        self.pks = [self.g ** self.sks[i] for i in range(0, N + 1)]
        self.S = self.group.random(G1)
        self.codeword = [self.group.init(ZR, 1)]
        for i in range(1, N + 1):
            vi = self.group.init(ZR, 1)
            for j in range(1, N + 1):
                if i != j:
                    vi=vi*1/(self.group.init(ZR, i)-j)  
                    # print(vi,i,j)
            self.codeword.append(vi)
        # print(self.codeword)
    def distribute(self, j):
        ts = time.time()
        s = self.group.random(ZR)
        self.S = self.g ** s
        shares = self.util.genShares(s, t, N)
        # print(s,shares,len(shares))
        # vs = [0]
        # vs.extend([self.gp ** shares[i] for i in range(1, N + 1)])
        # print(shat)
        shat = [0]
        shat.extend([self.pks[i] ** shares[i] for i in range(1, N + 1)])

        # LDEI proofs
        r_s = self.util.genShares(0, t, N)
        # print(len(r_s),len(shares))
        ai_s = [0]
        ai_s.extend([self.pks[i] ** r_s[i] for i in range(1, N + 1)])
        e = self.group.hash(str(self.pks) + str(shat), ZR)
        z_s = [0]
        z_s.extend(e * shares[i] + r_s[i] for i in range(1, N+1))
        # print("verify:", (shat[1] ** e) * ai_s[1] == self.pks[1] ** z_s[1])
        LDEIpr = {"e": e, "ai_s": ai_s, "z_s": z_s}

        dist = LDEIpr.copy()
        dist["shat"] = shat
        # dist["vs"] = vs
        print("Albatross distribution cost %.2fs, size: %.2fkB" %(time.time()- ts, len(str(dist))/1024.))
        return dist

    def LDEI_verify(self, dist):
        starttime = time.time()
        # Check LDEI proofs
        c = self.group.hash(str(self.pks) + str(dist["shat"]), ZR)

        # Check LDEI proofs
        for i in range(1, N + 1):
            # Calculate ai_s raised to the power of c
            ai_s_c = (dist["shat"][i] ** c) * (dist["ai_s"][i])
            # Calculate g raised to the power of z_s[i]
            g_z_s = self.pks[i] ** dist["z_s"][i]
            # Check if ai_s^c equals g^z_s
            if ai_s_c != g_z_s:
                print(i)
                return {"result": False, "cost": 0}

        print("Albatross verification cost %.2fs"%(time.time() - starttime))
        # time_cost = time.time() - starttime
        # return {"result": True, "cost": time_cost}

    def local_LDEI(self,recon):
        v = self.group.init(G1, 1)
        
        _p = self.util.genShares(0, t, N)

        for i in range(1, N + 1):
            v = v * (recon["vs"][i] ** (self.codeword[i]*_p[i]))
        if v != self.group.init(G1, 1):
            return False
        return True

    def dleq_verify(self, recon):
        starttime = time.time()
            # Check DLEQ proofs
        c = self.group.hash(str(recon["vs"]) + str(recon["shat"]), ZR)
        for i in range(1, N + 1):
            if recon["a1"][i] != (self.g ** recon["z"][i]) * (self.pks[i] ** c) \
                    or recon["a2"][i] != recon["vs"][i] ** recon["z"][i] * (recon["shat"][i] ** c):
                return False
        return True



    def reconstruct(self, dist, j):

        # DLEQ proofs by shareholders
        stidle = [self.group.init(G1, 1)]
        for i in range(1, N + 1):
            stidle.append(dist["shat"][i] ** (1 / self.sks[i]))



        w = self.group.random(ZR)
        z, a1, a2 = [0 for i in range(0, len(self.sks))], \
                    [0 for i in range(0, len(self.sks))], \
                    [0 for i in range(0, len(self.sks))]
        c = self.group.hash(str(stidle) + str(dist["shat"]), ZR)

        for i in range(1, len(z)):
            a1[i] = self.g ** w
            a2[i] = stidle[i] ** w
            z[i] = w - self.sks[i] * c

        dleqPrfs = {"c": c, "a1": a1, "a2": a2, "z": z}
        recon = dleqPrfs.copy()
        recon["vs"] = stidle
        recon["shat"] = dist["shat"]
        
        starttime = time.time()
        DLEQ_verification = self.dleq_verify(recon)
        assert DLEQ_verification == True
        Locol_LDEI_verification = self.local_LDEI(recon)
        assert Locol_LDEI_verification == True
        # time_cost = time.time() - starttime
        # print("Albatross reconstruct verification cost %.3fs"%(time.time() - starttime))

        indexArr = [i for i in range(1, N + 1)]

        random.shuffle(indexArr)
        indexArr = indexArr[0:t]
        y = self.util.recoverCoefficients(indexArr)
        z = self.group.init(G1, 1)
        for i in indexArr:
            z *= stidle[i] ** y[i]
        if self.S != z:
            return -2
        print("Albatross reconstruction cost: %.3fs size: %.2fkB"%(time.time()- starttime,  len(str(recon))/1024.))
        # return time_cost


groupObj = PairingGroup("MNT159")
albatross = PPVSS(groupObj)
print("N=%d,t=%d" % (N, t))
ver_cost = 0
rec_cost = 0
n=1
for i in range(n):
    dis = albatross.distribute(i)
    albatross.LDEI_verify(dis)
    # if i == 1:
    #     print("Albatross verification result: ", ver_result["result"])
    # ver_cost += ver_result["cost"]
    albatross.reconstruct(dis, i)
# print("Albatross verification cost:", ver_cost/n)



# print(result)



