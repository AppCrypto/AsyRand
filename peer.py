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
                
                
            
                # sv={'C_P': json.loads(json.dumps(mynode.pvss.share(n,f+1)))}
                sv={'C_Ps': [json.loads(json.dumps(mynode.pvss.share(n,f+1))) for i in range(0, C_Plen)]}
                sv['epoch'] = epoch
                sv['ts'] = time.time()
                sv['ts1'] = time.time()                            
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
                
                time.sleep(10)
                print("Node %s producer starts"%(mynode.id))
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
                mynode.pvss.verify(rv['C_Ps'][i]["C"], rv['C_Ps'][i]["proof_sw"])
            sv = {"hC_Ps":mynode.pvss.hash(rv['C_Ps'])}            
            sv['epoch'] = epoch
            sv['seq'] = seq   
            sv['ts'] = rv['ts']
            sv['ts1'] = time.time()
            seqLatest = int(seq.split("_")[1])
            # time.sleep(0.2)
            time.sleep(mynode.sendingCnt / 80.)

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
            sv['ts'] = rv['ts']
            sv['ts1'] = rv['ts1']
            
            # print(mynode.id, "recieve echo from",yourid, seq, rv['hC_Ps'],len(mynode.msgs["echo"][seq]))
            if len(mynode.msgs["echo"][seqistr]) > 2*f or (seqistr in mynode.msgs["ready"] and len(mynode.msgs["ready"][seqistr]) > f):                
                if not mynode.msgs[sentProducer]:
                     mynode.msgs[sentProducer] = True
                else:
                    return                
                sv['ts2'] = time.time() 
                time.sleep(0.2)               
                # time.sleep(mynode.sendingCnt  * random.random() / 40.)
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
                
                # if mynode.epoch % 10 == 0:
                ts = time.time()
                
                if CTs == None:
                    CTs = [json.loads(json.dumps(mynode.pvss.share(n,f+1))) for i in range(0, C_Plen)] 
                # CTs = [json.loads(json.dumps(mynode.pvss.share(n,f+1))) for i in range(0, C_Plen)] 

                sv={'C_Ps': CTs}                
                sv['epoch'] = epoch
                sv['ts'] = time.time()
                sv['ts1'] = time.time()
                for i in range(0, C_Plen):
                    seqi = mynode.seq+i                    
                    seqistr = 'seq_%d'%seqi      
                    if seqistr not in mynode.msgs["initial"]:
                        mynode.msgs["initial"][seqistr]={}
                    if mynode.id not in mynode.msgs["initial"][seqistr]:
                        mynode.msgs["initial"][seqistr][mynode.id]=sv['C_Ps'][i]
                mynode.seq += C_Plen
                sv['seq'] = "seq_%d"%(mynode.seq)

                print("%s sendingCnt:%d consensus at %s, initial time: %.2f, echo time: %.2f, ready time: %.2f"%( mynode.id,mynode.sendingCnt, rv['seq'], ts-rv['ts'],  ts-rv['ts1'],  ts-rv['ts2']) )
                
                # print(mynode.seq, mynode.seq, mynode.curSeq[int(mynode.id)] + C_Plen)
                if mynode.seq - config["C_Ptimes"]* C_Plen > mynode.curSeq[int(mynode.id)]:
                    time.sleep(config["sleep1"]*(mynode.seq-mynode.curSeq[int(mynode.id)]-2) + mynode.sendingCnt / 5)
                else:
                    time.sleep(config["sleep2"]+ mynode.sendingCnt / 40) 


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

            
            # print(mynode.id, tp, epoch, len(mynode.cis[tp][epoch]))
            if len(mynode.cis[tp][epoch]) > f and str(L) in mynode.msgs["initial"][seq]:
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return
                time.sleep(0.05) 
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
                sv['LQ']=rv['LQ']
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
            
            flag=False
            if len(mynode.cis["reconReady"][epoch]) > f:
                cis_tp_epoch =mynode.cis["reconReady"][epoch].copy()
                values = {}  
                for yid in cis_tp_epoch:
                    lqHash = mynode.pvss.hash(cis_tp_epoch[yid])
                    if lqHash not in values:
                        values[lqHash] = 0
                    values[lqHash] += 1
                for lqHash in values:
                    if values[lqHash] > f:
                        flag=True

            
            if len(mynode.cis[tp][epoch]) > 2*f or flag:
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return         
                time.sleep(0.05)                
                sv = {"beaconV":rv['beaconV']}
                sv['epoch'] = epoch
                sv['seq'] = seq            
                sv['newepoch'] = rv['newepoch']  
                sv['L'] = rv['L']                
                sv['Re_1'] = rv['Re_1']      
                sv['LQ'] = rv['LQ']
                sv['ts'] = rv['ts']
                sv['ts1'] = rv['ts1']
                sv['ts2'] = rv['ts2']
                sv['ts3'] = time.time()
                
                if epoch not in mynode.cis["reconReady"]:
                    mynode.cis["reconReady"][epoch]={}
                if mynode.id not in mynode.cis["reconReady"][epoch]:
                    mynode.cis["reconReady"][epoch][mynode.id]={"beaconV":rv['beaconV'],"LQ":rv['LQ'],'L':rv['L'], 'Re_1':rv['Re_1'],'newepoch':rv['newepoch']}
                # print("node %s send reconReady ct: %s"%(mynode.id, sv))
                mynode.send_to_nodes({"type": "reconReady", "v": json.dumps(sv)})
        elif tp == "reconReady":

            mynode.cis[tp][epoch][yourid] = {"beaconV":rv['beaconV'],"LQ":rv['LQ'],'L':rv['L'], 'Re_1':rv['Re_1'],'newepoch':rv['newepoch']}
            if len(mynode.cis[tp][epoch]) > 2*f: 

                cis_tp_epoch =mynode.cis[tp][epoch].copy()
                values = {}  
                for yid in cis_tp_epoch:
                    lqHash = mynode.pvss.hash(cis_tp_epoch[yid])
                    if lqHash not in values:
                        values[lqHash] = 0
                    values[lqHash] += 1

                if values[mynode.pvss.hash(mynode.cis[tp][epoch][yourid])] <= 2*f:
                    print("node%s reconReady------------------------------------------------------- valid <= 2*f"%(mynode.id), values[mynode.pvss.hash(mynode.cis[tp][epoch][yourid])])
                    return

                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return

                if mynode.epoch >= rv['newepoch']:
                    print("node%s reconReady-------------------------------------------------------mynode.epoch >= rv['newepoch']"%(mynode.id))
                    return
                time.sleep(0.05) 
                with threading.Lock():
                    beaconV = rv['beaconV']
                    L = rv['L']                
                    Re_1 = rv['Re_1']
                    mynode.curSeq[L]+=1                    
                    mynode.LQ.setQueue(list(rv['LQ']));      
                    if mynode.LQ.full():
                        oldestL = mynode.LQ.get()     
                    mynode.LQ.put(L)                         
                    mynode.CL={i:True for i in range(1, n+1)}
                    for j in mynode.LQ.all():
                        if j in mynode.CL:
                            del mynode.CL[j]
                    keys = list(mynode.CL.keys())
                    newL = keys[int(beaconV) % len(mynode.CL)]
                    # endtime = time.time()
                    
                    if mynode.epoch == 10:
                        print("%s(%s/%s) epoch:%s Node%s's %s, value: %s %.2fs/beacon %.2fs %.2fs %.2fs per LQ:%s"%(mynode.id,mynode.curSeq[int(mynode.id)], mynode.seq, epoch, L, seq, beaconV%100000,(time.time()-rv['ts'])/2/mynode.epoch, time.time()-rv['ts1'],time.time()-rv['ts2'],time.time()-rv['ts3'], mynode.LQ.all() ), len(str(mynode.msgs))/mynode.seq/1024., len(str(mynode.cis))/mynode.epoch/1024.)
                    else:
                        print("%s(%s/%s) epoch:%s Node%s's %s, value: %s %.2fs/beacon %.2fs %.2fs %.2fs per LQ:%s"%(mynode.id,mynode.curSeq[int(mynode.id)], mynode.seq, epoch, L, seq, beaconV%100000,(time.time()-rv['ts'])/2/mynode.epoch, time.time()-rv['ts1'],time.time()-rv['ts2'],time.time()-rv['ts3'], mynode.LQ.all()))
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

        time.sleep(10)

        for j in range(int(ID)+1, n+1):
            node.connect_with_node(config["nodes"][str(j)]["ip"],config["portBase"]+j)
            print("Node %s connect %d (%s:%d)"%(self.ID, j, config["nodes"][str(j)]["ip"], config["portBase"]+j))           
        time.sleep(int(ID)/3+10)
        v = {'pk':node.pvss.pk}
        v['epoch'] = -1
        v['seq'] = "seq_%d"%(-1) 
        node.send_to_nodes({"type": "pks", "v": json.dumps(v)})
        
        
        keys = list(node.CL.keys())
        node.newL = keys[node.Re_1 % len(node.CL)]
        
        print(node.id, "choose leader",node.newL)
        sentDict={}
        
        starttime = time.time()

        time.sleep(60)
        print("Node %s consumer starts"%node.id)
        while True:
            if node.epoch <= 2:
                starttime = time.time()

        #     # if "initial" in node.msgs and node.curSeq[node.L] in node.msgs["initial"]:
        #     #     print(len(node.msgs["initial"][node.curSeq[node.L]]))
            time.sleep(config['consumerSleep']+random.random()*0.4)            
            if(node.newL == node.L):
                print("node.newL == node.L",node.L)
                continue
            if node.newL not in node.curSeq:
                print("node.newL not in node.curSeq")
                continue
            
            seq = "seq_%d"%(node.curSeq[node.newL])
            sent = "sent_%s_%s"%("ready", seq)

            sent2 = "ld_%sseq_%d"%(node.newL,node.curSeq[node.newL])
            if sent2 in sentDict:           
                # print("%s has sent2 in sentDict"%node.id,getattr(node, "id"), sent2, node.epoch, seq, node.newL)
                continue
            
            # if sent in node.msgs and node.msgs[sent] and \        
            if "initial" in node.msgs and (seq in node.msgs["initial"] and \
                 str(node.newL) in node.msgs["initial"][seq]):# and \
                 # len(node.msgs["initial"][seq][str(node.newL)])>=1 :
                sentDict[sent2]=True

                EC = node.msgs["initial"][seq][str(node.newL)]
                # print(EC)
                sv = {'c_i': node.pvss.preRecon(EC['C'], self.ID)}
                sv['epoch'] = node.epoch
                sv['newepoch'] = node.epoch+1
                sv['L'] = node.newL
                sv['LQ']=list(node.LQ.all())               
                sv['seq'] = seq
                sv['Re_1'] = node.Re_1
                sv['ts'] = starttime
                sv['ts1'] = time.time()
                # print("%s start to consume %d's %dth ciphertext %s cost:%s"%(node.id, node.newL, node.curSeq[node.newL], int(node.pvss.hash(EC))%100000, time.time()-starttime))  
                if sv['epoch'] not in node.cis['recon']:
                    node.cis['recon'][sv['epoch']] = {}
                # if sv['epoch'] not in node.cis['reconEcho']:
                #     node.cis['reconEcho'][sv['epoch']] = {}
                # if sv['epoch'] not in node.cis['reconReady']:
                #     node.cis['reconReady'][sv['epoch']] = {}
                node.cis['recon'][sv['epoch']][node.id] = sv['c_i']
                node.send_to_nodes({"type": "recon", "v": json.dumps(sv)})
            # else:
                # if sent not in node.msgs :
                #     print(node.id,"wait for ",sent)
                # if seq not in node.msgs["initial"]:
                #     print(node.id,"wait for initial",seq)
                # else:
                #     if str(node.newL) not in node.msgs["initial"][seq] :
                #         print(node.id,"wait for newL", str(node.newL), seq)
                #     else:
                #         print(node.id,"wait for >1")
           
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
    