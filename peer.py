import sys,os
import time
import hashlib,requests
from node import Node
# sys.path.insert(0, '..') # Import the files where the modules are located
import newjson as json,threading,multiprocessing
from multiprocessing import Process, Manager 
 


from config import config

ID = sys.argv[1]

n=len(config["nodes"])
f=int((len(config["nodes"]) -1)/3)
        
ip = config["nodes"][ID]["ip"]
port = config["portBase"] + int(ID)

CT = None


# EP = 1

def callback(event, mynode, yournode, data):
    global CT
    if event == "node_message":        
        
        tp = data['type']
        rv = json.loads(data['v'])
        epoch = rv['epoch']        
        seq = rv['seq']
        yourid = yournode.id
        # print("node:%s recieve type:%s from mode:%s"%(mynode.id, tp, yournode.id))
        sentProducer = "sent_%s_%s"%(tp, seq)
        sentConsumer = "sent_%s_%s"%(tp, epoch)
        if tp in ["pks", "initial","echo", "ready"]:
            if tp not in mynode.msgs:
                mynode.msgs[tp]={}      
            if seq not in mynode.msgs[tp]:
                mynode.msgs[tp][seq] = {}           
            
            if sentProducer not in mynode.msgs:
                mynode.msgs[sentProducer] = False
                        
        if tp in ["recon","reconEcho", "reconReady"]:
            if epoch not in mynode.cis[tp]:
                mynode.cis[tp][epoch]={}

            if sentConsumer not in mynode.cis:
                mynode.cis[sentConsumer] = False

        if tp == "pks":
            mynode.pvss.setPK(int(yourid), rv['pk'])
            # print("node:%s's pks length:%d"%(mynode.id, len(mynode.pvss.pks)))
            if len(mynode.pvss.pks) == len(config['nodes']):                      
                time.sleep(5)
                # print(mynode.pvss.pks)
                # time.sleep(100)

                sv={'C_P': json.loads(json.dumps(mynode.pvss.share(n,f+1)))}
                sv['epoch'] = epoch
                mynode.seq += 1 
                sv['seq'] = "seq_%d"%mynode.seq
                
                mynode.msgs[tp][sv['seq']]={}
                mynode.msgs[tp][sv['seq']][mynode.id]=sv['C_P']
                # mynode.msgs[sentProducer] = True

                if "initial" not in mynode.msgs:
                    mynode.msgs["initial"]={}
                if sv['seq'] not in mynode.msgs["initial"]:
                    mynode.msgs["initial"][sv['seq']]={}
                if mynode.id not in mynode.msgs["initial"][sv['seq']]:
                    mynode.msgs["initial"][sv['seq']][mynode.id]=sv['C_P']
                
                # print("%s initial ct= %s at %s"%(mynode.id, mynode.pvss.hash(sv['C_P']), sv['seq']))
                mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)}) 
        elif tp == "initial":
            mynode.msgs[tp][seq][yourid] = rv['C_P']
            # mynode.msgs[tp][seq][mynode.id]=rv['C_P']
            # TODO pvss.verify
            sv = {"hC_P":mynode.pvss.hash(rv['C_P'])}            
            sv['epoch'] = epoch
            sv['seq'] = seq           
            # time.sleep(0.1)         
            if "echo" not in mynode.msgs:
                mynode.msgs["echo"]={}
                if seq not in mynode.msgs["echo"]:
                    mynode.msgs["echo"][seq]={}
                if mynode.id not in mynode.msgs["echo"][seq]:
                    mynode.msgs["echo"][seq][mynode.id]=sv['hC_P']
                
            mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})  
        elif tp == "echo":            
            mynode.msgs[tp][seq][yourid] = rv['hC_P']
            sv = {"hC_P":rv['hC_P']}
            sv['epoch'] = epoch
            sv['seq'] = seq            
            if len(mynode.msgs["echo"][seq]) > 2*f or ("ready" in mynode.msgs and seq in mynode.msgs["ready"] and len(mynode.msgs["ready"][seq]) > f):                
                if not mynode.msgs[sentProducer]:
                     mynode.msgs[sentProducer] = True
                else:
                    return                
                # time.sleep(0.1)
                if "ready" not in mynode.msgs:
                    mynode.msgs["ready"]={}
                    if seq not in mynode.msgs["ready"]:
                        mynode.msgs["ready"][seq]={}
                    if mynode.id not in mynode.msgs["ready"][seq]:
                        mynode.msgs["ready"][seq][mynode.id]=sv['hC_P']
                # print("node %s send ready ct: %s"%(mynode.id, sv['hC_P']))
                mynode.send_to_nodes({"type": "ready", "v": json.dumps(sv)}) 

        elif tp == "ready":
            mynode.msgs[tp][seq][yourid] = rv['hC_P']
            sv = {"hC_P":rv['hC_P']}
            sv['epoch'] = epoch
            sv['seq'] = seq
            
            if len(mynode.msgs["ready"][seq]) > 2*f:
                # mynode.reconnect_nodes()
                
                if not mynode.msgs[sentProducer]:
                     mynode.msgs[sentProducer] = True
                else:
                    return
                # time.sleep(0.1)
                # if "initial" in mynode.msgs:
                #     print("node %s reach consensus on %s"%(mynode.id, mynode.msgs["initial"][seq][mynode.id]))
                # template
                if CT == None:
                    CT= json.loads(json.dumps(mynode.pvss.share(n,f+1)))
                
                sv={'C_P': CT}
                sv['epoch'] = epoch
                mynode.seq += 1 
                sv['seq'] = "seq_%d"%mynode.seq
                
                # print("%s initial ct= %s at %s"%(mynode.id, int(mynode.pvss.hash(sv['C_P']))%100000, sv['seq']))

                if "initial" not in mynode.msgs:
                    mynode.msgs["initial"]={}
                if sv['seq'] not in mynode.msgs["initial"]:
                    mynode.msgs["initial"][sv['seq']]={}
                if mynode.id not in mynode.msgs["initial"][sv['seq']]:
                    mynode.msgs["initial"][sv['seq']][mynode.id]=sv['C_P']
                mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)})  
        elif tp == "recon":
            if epoch not in mynode.cis[tp]:
                mynode.cis[tp][epoch] = {}                
            mynode.cis[tp][epoch][yourid] = rv['c_i']            
            L = rv['L']
            seq = rv['seq']
            Re_1=rv['Re_1']
            
            if len(mynode.cis[tp][epoch]) > f:#TODO f
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return

                C=mynode.msgs["initial"][seq][str(L)]['C']
                starttime = time.time()
                cis=mynode.cis[tp][epoch].copy()
                gs = mynode.pvss.recon(C, cis)
                
                beaconV = int(mynode.pvss.hash(str(Re_1)+str(gs)))

                sv = {"beaconV":beaconV}            
                sv['epoch'] = epoch                
                sv['seq'] = seq
                sv['newepoch'] = rv['newepoch']
                sv['L'] = rv['L']                
                sv['Re_1'] = rv['Re_1']
                sv['ts'] = rv['ts']
                # time.sleep(0.1)         
                if epoch not in mynode.cis["reconEcho"]:
                    mynode.cis["reconEcho"][epoch]={}
                if mynode.id not in mynode.cis["reconEcho"][epoch]:
                    mynode.cis["reconEcho"][epoch][mynode.id]=sv['beaconV']
                
                mynode.send_to_nodes({"type": "reconEcho", "v": json.dumps(sv)})
        elif tp == "reconEcho":
            mynode.cis[tp][epoch][yourid] = rv['beaconV']
            sv = {"beaconV":rv['beaconV']}
            sv['epoch'] = epoch
            sv['seq'] = seq            
            sv['newepoch'] = rv['newepoch']  
            sv['L'] = rv['L']                
            sv['Re_1'] = rv['Re_1']      
            sv['ts'] = rv['ts']
            if len(mynode.cis[tp][epoch]) > 2*f or (epoch in mynode.cis["reconReady"] and len(mynode.cis["reconReady"][epoch]) > f ):#TODO f            
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return                
                # time.sleep(0.1)
                if epoch not in mynode.cis["reconReady"]:
                    mynode.cis["reconReady"][epoch]={}
                if mynode.id not in mynode.cis["reconReady"][epoch]:
                    mynode.cis["reconReady"][epoch][mynode.id]=sv['beaconV']
                # print("node %s send reconReady ct: %s"%(mynode.id, sv['hC_P']))
                mynode.send_to_nodes({"type": "reconReady", "v": json.dumps(sv)})
        elif tp == "reconReady":
            mynode.cis[tp][epoch][yourid] = rv['beaconV']
            if len(mynode.cis[tp][epoch]) > 2*f:                
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return
                beaconV = rv['beaconV']
                L = rv['L']                
                Re_1 = rv['Re_1']
                mynode.curSeq[L]+=1
                if mynode.LQ.full():
                    oldestL = mynode.LQ.get()                    
                mynode.LQ.put(L)
                mynode.CL={i:True for i in range(1, n+1)}
                for j in mynode.LQ.all():
                    del mynode.CL[j]
                keys = list(mynode.CL.keys())
                newL = keys[int(beaconV) % len(mynode.CL)]
                # endtime = time.time()
                print("%s in %s consume %s's %s/%s, output beacon: %s throughput: %ss per "%(mynode.id, epoch, L, seq, mynode.curSeq[L], beaconV%100000,(time.time()-rv['ts'])/epoch ))
                mynode.Re_1 = beaconV                
                mynode.epoch=rv['newepoch']
                mynode.L=L
                mynode.newL = newL
                # print("new leader", mynode.newL, mynode.LQ.all(), mynode.CL)
            
class Peer(threading.Thread):    
    def __init__(self, ID):
        self.ID= ID
        self.config = config
        
        node = Node(ip, port, ID, callback)
        node.start()

        time.sleep(3)
        for j in range(int(ID)+1, n+1):
            node.connect_with_node(ip,config["portBase"]+j)
            print("Node %s connect %d"%(self.ID, j))           
        time.sleep(5)  
        v = {'pk':node.pvss.pk}
        v['epoch'] = -1
        v['seq'] = "seq_%d"%(-1) 
        node.send_to_nodes({"type": "pks", "v": json.dumps(v)})
        
        
        keys = list(node.CL.keys())
        node.newL = keys[node.Re_1 % len(node.CL)]
        
        print(node.id, "choose leader",node.newL)
        sentDict={}
        
        starttime = time.time()
        while True:
            if node.epoch==1:
                starttime = time.time()

        #     # if "initial" in node.msgs and node.curSeq[node.L] in node.msgs["initial"]:
        #     #     print(len(node.msgs["initial"][node.curSeq[node.L]]))
            time.sleep(0.1)            
            if(node.newL == node.L):
                print("node.newL == node.L",node.L)
                continue
            if node.newL not in node.curSeq:
                # print("node.newL not in node.curSeq:")
                continue
            
            seq = "seq_%d"%(node.curSeq[node.newL])
            sent = "sent_%s_%s"%("ready", seq)

            sent2 = "ld_%sseq_%d"%(node.newL,node.curSeq[node.newL])
            if sent2 in sentDict:           
                continue
        #     # print(sent in node.msgs and node.msgs[sent], (seq in node.msgs["initial"]),seq, str(node.newL) in node.msgs["initial"][seq])
            if sent in node.msgs and node.msgs[sent] and \
                (seq in node.msgs["initial"] and \
                 str(node.newL) in node.msgs["initial"][seq]) and \
                 len(node.msgs["initial"][seq][str(node.newL)])>1 :
                sentDict[sent2]=True

                EC = node.msgs["initial"][seq][str(node.newL)]
                sv = {'c_i': node.pvss.preRecon(EC['C'], self.ID)}
                sv['epoch'] = node.epoch
                sv['newepoch'] = node.epoch+1
                sv['L'] = node.newL
                sv['seq'] = seq
                sv['Re_1'] = node.Re_1
                sv['ts'] = starttime
        #         print("%s start to consume %d's %dth ciphertext %s cost:%s"%(node.id, node.newL, node.curSeq[node.newL], int(node.pvss.hash(EC))%100000, time.time()-starttime))  
                if node.epoch not in node.cis['recon']:
                    node.cis['recon'][node.epoch] = {}
                node.cis['recon'][node.epoch][node.id] = sv['c_i']
                node.send_to_nodes({"type": "recon", "v": json.dumps(sv)})
                
                


if __name__ == '__main__':    
    peer = Peer(ID)
    peer.start()
    peer.join()
    