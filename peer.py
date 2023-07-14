import sys,os
import time
import hashlib,random
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
C_Plen = config["C_Plen"]
CTs = None


# EP = 1

def callback(event, mynode, yournode, data):
    global CTs
    if event == "node_message":        
        # print(data.length)
        tp = data['type']
        rv = json.loads(data['v'])
        epoch = rv['epoch']        
        seq = rv['seq']
        yourid = yournode.id
        # print("node:%s recieve type:%s from node:%s"%(mynode.id, tp, yournode.id), seq, epoch)
        sentProducer = "sent_%s_%s"%(tp, seq)
        sentConsumer = "sent_%s_%s"%(tp, epoch)
        
        

        for tpi in ["pks", "initial","echo", "ready"]:
            
            if tpi not in mynode.msgs:
                mynode.msgs[tpi]={}     

            if seq not in mynode.msgs[tpi]:
                mynode.msgs[tpi][seq] = {}           
            
            if sentProducer not in mynode.msgs:
                mynode.msgs[sentProducer] = False

            seqLatest = int(seq.split("_")[1])        

        if tp in ["pks", "initial","echo", "ready"]:
            for i in range(0, C_Plen):
                seqistr = 'seq_%d'%(seqLatest - C_Plen + i )      
                if seqistr not in mynode.msgs[tp]:
                    mynode.msgs[tp][seqistr]={}

                        
        for tpi in ["recon", "reconEcho", "reconReady"]:
            if tpi not in mynode.cis:
                mynode.cis[tpi]={}
            if epoch not in mynode.cis[tpi]:
                mynode.cis[tpi][epoch]={}

            if sentConsumer not in mynode.cis:
                mynode.cis[sentConsumer] = False

        
        if tp == "pks":
            mynode.pvss.setPK(int(yourid), rv['pk'])
            # print("node:%s's pks length:%d"%(mynode.id, len(mynode.pvss.pks)))
            if len(mynode.pvss.pks) == len(config['nodes']):                      
                time.sleep(3)
                # print(mynode.pvss.pks)
            
                # sv={'C_P': json.loads(json.dumps(mynode.pvss.share(n,f+1)))}
                sv={'C_Ps': [json.loads(json.dumps(mynode.pvss.share(n,f+1))) for i in range(0, C_Plen)]}
                sv['epoch'] = epoch
                            
                # mynode.msgs[sentProducer] = True
                                         
                for i in range(0, C_Plen):
                    seqi = mynode.seq+i                    
                    seqistr = 'seq_%d'%seqi                    
                    if seqistr not in mynode.msgs["initial"]:
                        mynode.msgs["initial"][seqistr]={}
                    if mynode.id not in mynode.msgs["initial"][seqistr]:
                        mynode.msgs["initial"][seqistr][mynode.id]=sv['C_Ps'][i]

                mynode.seq += C_Plen
                sv['seq'] = "seq_%d"%(mynode.seq)
                
                # print("%s initial ct= %s at %s"%(mynode.id, int(mynode.pvss.hash(sv['C_Ps']))%100000, sv['seq']))
                # if mynode.id == "1":                
                mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)}) 

                sv['hC_Ps'] = mynode.pvss.hash(sv['C_Ps'])
                del sv['C_Ps']
                mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})                     
        elif tp == "initial":
            seqLatest = int(seq.split("_")[1])
            seqistr=seq
            for i in range(0, C_Plen):
                seqi = seqLatest - C_Plen + i 
                seqistr = 'seq_%d'%seqi      
                mynode.msgs[tp][seqistr][yourid] = rv['C_Ps'][i]
                # TODO verify
                mynode.pvss.verify(rv['C_Ps'][i]["C"], rv['C_Ps'][i]["proof_sw"])
            sv = {"hC_Ps":mynode.pvss.hash(rv['C_Ps'])}            
            sv['epoch'] = epoch
            sv['seq'] = seq   
            seqLatest = int(seq.split("_")[1])
            time.sleep(0.2)
            

            for i in range(0, C_Plen):
                seqi = seqLatest - C_Plen + i 
                seqistr = 'seq_%d'%seqi                    
                if seqistr not in mynode.msgs["echo"]:
                    mynode.msgs["echo"][seqistr]={}
                if mynode.id not in mynode.msgs["echo"][seqistr]:
                    mynode.msgs["echo"][seqistr][mynode.id]=sv['hC_Ps']
                # mynode.msgs[tp][seqistr][yourid] = rv['C_Ps'][i]
            # print("%s echo ct= %s at %s"%(mynode.id, sv['hC_Ps'], sv['seq']), len(mynode.msgs["echo"][seqistr]))
            mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})  
        elif tp == "echo":
            seqLatest = int(seq.split("_")[1])
            seqistr=seq
            for i in range(0, C_Plen):
                seqistr = 'seq_%d'%(seqLatest - C_Plen + i )
                mynode.msgs[tp][seqistr][yourid] = rv['hC_Ps']
            sv = {"hC_Ps":rv['hC_Ps']}
            sv['epoch'] = epoch
            sv['seq'] = seq            
            
            # print(mynode.id, "recieve echo from",yourid, seq, rv['hC_Ps'],len(mynode.msgs["echo"][seq]))
            if len(mynode.msgs["echo"][seqistr]) > 2*f or (seqistr in mynode.msgs["ready"] and len(mynode.msgs["ready"][seqistr]) > f):                
                if not mynode.msgs[sentProducer]:
                     mynode.msgs[sentProducer] = True
                else:
                    return                
                time.sleep(0.2)               
                seqLatest = int(seq.split("_")[1])
                for i in range(0, C_Plen):
                    seqistr = 'seq_%d'%(seqLatest - C_Plen + i )
                    if seqistr not in mynode.msgs["ready"]:
                        mynode.msgs["ready"][seqistr]={}
                    if mynode.id not in mynode.msgs["ready"][seqistr]:
                        mynode.msgs["ready"][seqistr][mynode.id]=sv['hC_Ps']
                # print("node %s send ready ct: %s"%(mynode.id, sv['hC_Ps']))
                mynode.send_to_nodes({"type": "ready", "v": json.dumps(sv)}) 

        elif tp == "ready":
            # mynode.msgs[tp][seq][yourid] = rv['hC_Ps']
            seqLatest = int(seq.split("_")[1])
            seqistr=seq
            for i in range(0, C_Plen):
                seqistr = 'seq_%d'%(seqLatest - C_Plen + i )
                mynode.msgs[tp][seqistr][yourid] = rv['hC_Ps']

            if len(mynode.msgs["ready"][seqistr]) > 2*f:
                # time.sleep(0.1 * random.random())
                if not mynode.msgs[sentProducer]:
                     mynode.msgs[sentProducer] = True
                     for i in range(0, C_Plen):
                        seqistr = 'seq_%d'%(seqLatest - C_Plen + i )
                        sentProducer = 'sent_%s_%s'%(tp, seqistr)
                        mynode.msgs[sentProducer] = True
                else:
                    return
                cnt= 0
                # while mynode.seq - C_Plen > mynode.curSeq[int(mynode.id)]:
                #     # print(mynode.id, mynode.seq, mynode.epoch, mynode.curSeq[int(mynode.id)],mynode.newL)
                #     cnt+=1
                #     time.sleep(5+random.random())

                    # if cnt>20:
                    #     break

                # print(mynode.seq, mynode.seq, mynode.curSeq[int(mynode.id)] + C_Plen)
                if mynode.seq - 2* C_Plen > mynode.curSeq[int(mynode.id)]:
                    time.sleep(config["sleep1"]) 
                else:
                    time.sleep(config["sleep2"]) 

                # if CTs == None:
                #     CTs = [json.loads(json.dumps(mynode.pvss.share(n,f+1))) for i in range(0, C_Plen)] 
                CTs = [json.loads(json.dumps(mynode.pvss.share(n,f+1))) for i in range(0, C_Plen)] 
                
                sv={'C_Ps': CTs}                
                sv['epoch'] = epoch
                
                for i in range(0, C_Plen):
                    seqi = mynode.seq+i                    
                    seqistr = 'seq_%d'%seqi      
                    if seqistr not in mynode.msgs["initial"]:
                        mynode.msgs["initial"][seqistr]={}
                    if mynode.id not in mynode.msgs["initial"][seqistr]:
                        mynode.msgs["initial"][seqistr][mynode.id]=sv['C_Ps'][i]
                mynode.seq += C_Plen
                sv['seq'] = "seq_%d"%(mynode.seq)

                # if seqLatest % 11 == 0:
                #     print("%s initial ct= %s at %s"%(mynode.id, int(mynode.pvss.hash(sv['C_Ps']))%100000, sv['seq']), len(mynode.msgs["initial"]['seq_%d'%(mynode.seq- C_Plen )][mynode.id]),len(mynode.msgs["initial"]['seq_%d'%(mynode.seq- C_Plen -1)][mynode.id]))
                # if mynode.id == "1":
                mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)})  

                sv['hC_Ps'] = mynode.pvss.hash(sv['C_Ps'])
                del sv['C_Ps']
                mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})                     
        elif tp == "recon":
            if epoch not in mynode.cis[tp]:
                mynode.cis[tp][epoch] = {}                
            mynode.cis[tp][epoch][yourid] = rv['c_i']            
            L = rv['L']
            seq = rv['seq']
            Re_1=rv['Re_1']
        
            # if mynode.newL in mynode.curSeq:
            #     print(mynode.id, tp, mynode.newL, mynode.epoch, mynode.curSeq[mynode.newL], len(mynode.cis[tp][mynode.epoch]))
            # else:
            #     print(mynode.id, tp, mynode.newL, "mynode.newL in mynode.curSeq")
        
            # if mynode.epoch not in mynode.cis[tp]:
            #     print(mynode.id, tp, mynode.epoch, "mynode.epoch not in mynode.cis[tp]")

            # print(mynode.id, tp, epoch, len(mynode.cis[tp][epoch]))
            if len(mynode.cis[tp][epoch]) > f and str(L) in mynode.msgs["initial"][seq]:
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return
                time.sleep(0.01) 
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
                sv['ts1'] = rv['ts1']
                sv['ts2'] = time.time()
                # time.sleep(0.05)
                if epoch not in mynode.cis["reconEcho"]:
                    mynode.cis["reconEcho"][epoch]={}
                if mynode.id not in mynode.cis["reconEcho"][epoch]:
                    mynode.cis["reconEcho"][epoch][mynode.id]=sv['beaconV']
                
                mynode.send_to_nodes({"type": "reconEcho", "v": json.dumps(sv)})

        elif tp == "reconEcho":            
            mynode.cis[tp][epoch][yourid] = rv['beaconV']
            
            
            if len(mynode.cis[tp][epoch]) > 2*f or len(mynode.cis["reconReady"][epoch]) > f:
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return         
                time.sleep(0.01)                
                sv = {"beaconV":rv['beaconV']}
                sv['epoch'] = epoch
                sv['seq'] = seq            
                sv['newepoch'] = rv['newepoch']  
                sv['L'] = rv['L']                
                sv['Re_1'] = rv['Re_1']      
                sv['ts'] = rv['ts']
                sv['ts1'] = rv['ts1']
                sv['ts2'] = rv['ts2']
                sv['ts3'] = time.time()
                
                if epoch not in mynode.cis["reconReady"]:
                    mynode.cis["reconReady"][epoch]={}
                if mynode.id not in mynode.cis["reconReady"][epoch]:
                    mynode.cis["reconReady"][epoch][mynode.id]=sv['beaconV']
                # print("node %s send reconReady ct: %s"%(mynode.id, sv))
                mynode.send_to_nodes({"type": "reconReady", "v": json.dumps(sv)})
        elif tp == "reconReady":
            # print(rv, "beaconV" in rv)
            
            mynode.cis[tp][epoch][yourid] = rv['beaconV']
            if len(mynode.cis[tp][epoch]) > 2*f:                
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return
                time.sleep(0.01) 
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
                print("%s(%s/%s) in %s consume %s's %s, output value: %s %.2fs/beacon %.2fs %.2fs %.2fs per"%(mynode.id,mynode.curSeq[int(mynode.id)], mynode.seq, epoch, L, seq, beaconV%100000,(time.time()-rv['ts'])/epoch, time.time()-rv['ts1'],time.time()-rv['ts2'],time.time()-rv['ts3'] ), threading.current_thread().ident)
                mynode.Re_1 = beaconV                
                mynode.epoch=rv['newepoch']
                mynode.L=L
                mynode.newL = newL
                # print("new leader", mynode.newL, mynode.LQ.all(), mynode.CL)
            
class Peer(threading.Thread):
    def __init__(self, ID):
        super(Peer, self).__init__()
        self.ID= ID
        self.config = config
        node = Node(ip, port, ID, callback)
        self.node = node

    def start(self):
        node = self.node
        self.node.start()

        time.sleep(3)
        for j in range(int(ID)+1, n+1):
            node.connect_with_node(config["nodes"][str(j)]["ip"],config["portBase"]+j)
            print("Node %s connect %d (%s:%d)"%(self.ID, j, config["nodes"][str(j)]["ip"], config["portBase"]+j))           
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
            if node.epoch <= 2:
                starttime = time.time()

        #     # if "initial" in node.msgs and node.curSeq[node.L] in node.msgs["initial"]:
        #     #     print(len(node.msgs["initial"][node.curSeq[node.L]]))
            time.sleep(0.01)            
            if(node.newL == node.L):
                print("node.newL == node.L",node.L)
                continue
            if node.newL not in node.curSeq:
                print("node.newL not in node.curSeq")
                continue
            
            seq = "seq_%d"%(node.curSeq[node.newL])
            # sent = "sent_%s_%s"%("ready", seq)

            sent2 = "ld_%sseq_%d"%(node.newL,node.curSeq[node.newL])
            if sent2 in sentDict:           
                # print("%s has sent2 in sentDict"%node.id,getattr(node, "id"), sent2, node.epoch, seq, node.newL)
                continue
            
            # if sent in node.msgs and node.msgs[sent] and \
            if   (seq in node.msgs["initial"] and \
                 str(node.newL) in node.msgs["initial"][seq]):# and \
                 # len(node.msgs["initial"][seq][str(node.newL)])>=1 :
                sentDict[sent2]=True

                EC = node.msgs["initial"][seq][str(node.newL)]
                # print(EC)
                sv = {'c_i': node.pvss.preRecon(EC['C'], self.ID)}
                sv['epoch'] = node.epoch
                sv['newepoch'] = node.epoch+1
                sv['L'] = node.newL
                sv['seq'] = seq
                sv['Re_1'] = node.Re_1
                sv['ts'] = starttime
                sv['ts1'] = time.time()
                # print("%s start to consume %d's %dth ciphertext %s cost:%s"%(node.id, node.newL, node.curSeq[node.newL], int(node.pvss.hash(EC))%100000, time.time()-starttime))  
                if node.epoch not in node.cis['recon']:
                    node.cis['recon'][node.epoch] = {}
                # if node.epoch not in node.cis['reconEcho']:
                #     node.cis['reconEcho'][node.epoch] = {}
                # if node.epoch not in node.cis['reconReady']:
                    node.cis['reconReady'][node.epoch] = {}
                node.cis['recon'][node.epoch][node.id] = sv['c_i']
                node.send_to_nodes({"type": "recon", "v": json.dumps(sv)})
            else:
                # if sent not in node.msgs :
                #     print(node.id,"wait for ",sent)
                if seq not in node.msgs["initial"]:
                    print(node.id,"wait for initial",seq)
                else:
                    if str(node.newL) not in node.msgs["initial"][seq] :
                        print(node.id,"wait for newL", str(node.newL), seq)
                    else:
                        print(node.id,"wait for >1")
           
# from flask import Flask, render_template,request,jsonify,redirect,url_for,send_from_directory
# class MyThread(threading.Thread):
#     def __init__(self, node):
#         super(MyThread, self).__init__()
#         self.node = node

#     def run(self):        
#         app = Flask(__name__, template_folder = '.',static_folder='',static_url_path='')
        
#         @app.route('/',methods=["GET"])
#         def index():
#             attr = request.args.get("attr")
#             print(attr)
#             return jsonify({attr: json.dumps(getattr(self.node, attr))})
#         print("start flask server at", port+1000)
#         app.run('0.0.0.0', port+1000)


if __name__ == '__main__':    
    peer = Peer(ID)
    peer.setDaemon(True)
    # app = MyThread(peer.node)
    # app.start()
    peer.start()
    # peer.join()
    