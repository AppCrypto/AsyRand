import sys,os
import time
import hashlib,random
from node import Node
# sys.path.insert(0, '..') # Import the files where the modules are located
import newjson as json,threading,multiprocessing
from multiprocessing import Process, Manager 
import zlib, bz2, lzma, base64


from config import config

ID = sys.argv[1]

        
ip = config["nodes"][ID]["ip"]
port = config["portBase"] + int(ID)
C_Plen = config["C_Plen"]
CTs = None

n=len(config["nodes"])
f=int((n -1)/3)



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

            seqStart = int(seq.split("seq_")[1])        

        if tp in ["pks", "initial","echo", "ready"]:            
            if tp!="pks":
                mynode.producerRecvSize+=len(str(base64.b64encode(zlib.compress(str(data).encode('utf-8'), 6) + b'zlib')))   

            leaderID = seq.split("ld_")[1].split("seq_")[0]
            for i in range(0, C_Plen):
                seqistr = 'ld_%sseq_%d'%(leaderID, seqStart + i )      
                if seqistr not in mynode.msgs[tp]:
                    mynode.msgs[tp][seqistr]={}

        if tp in ["recon", "reconEcho", "reconReady"]:
            mynode.consumerRecvSize+=len(str(base64.b64encode(zlib.compress(str(data).encode('utf-8'), 6) + b'zlib')))   
            # print(tp, len(str(base64.b64encode(zlib.compress(str(data).encode('utf-8'), 6) + b'zlib')))  )

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
                time.sleep(10)
                print("Node %s producer starts"%(mynode.id))    
            
                # sv={'C_P': json.loads(json.dumps(mynode.pvss.share()))}
                sv={'C_Ps': [json.loads(json.dumps(mynode.pvss.share())) for i in range(0, C_Plen)]}
                sv['epoch'] = epoch
                sv['ts'] = time.time()
                # sv['ts1'] = time.time()                     
                sv['seq'] = "ld_%sseq_%d"%(mynode.id,mynode.seq)       
                # mynode.msgs[sentProducer] = True
                hC_Ps = mynode.pvss.hash(sv['C_Ps'])                                
                for i in range(0, C_Plen):
                    seqi = mynode.seq+i                    
                    seqistr = 'ld_%sseq_%d'%(mynode.id,seqi)
                    if seqistr not in mynode.msgs["initial"]:
                        mynode.msgs["initial"][seqistr]={}
                    if mynode.id not in mynode.msgs["initial"][seqistr]:
                        mynode.msgs["initial"][seqistr][mynode.id]=sv['C_Ps'][i]
                    if seqistr not in mynode.msgs["echo"]:
                        mynode.msgs["echo"][seqistr]={}
                    if mynode.id not in mynode.msgs["echo"][seqistr]:
                        mynode.msgs["echo"][seqistr][mynode.id]=hC_Ps

                mynode.seq += C_Plen
                         
                mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)}) 

                sv['hC_Ps'] = hC_Ps
                del sv['C_Ps']
                mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})                     
        elif tp == "initial":
            
            seqStart = int(seq.split("seq_")[1])
            seqistr=seq
            for i in range(0, C_Plen):
                seqi = seqStart + i 
                seqistr = 'ld_%sseq_%d'%(leaderID, seqi)
                mynode.msgs[tp][seqistr][yourid] = rv['C_Ps'][i]
                mynode.pvss.verify(rv['C_Ps'][i]["C"], rv['C_Ps'][i]["pi"])
            sv = {"hC_Ps":mynode.pvss.hash(rv['C_Ps'])}            
            sv['epoch'] = epoch
            sv['seq'] = seq   
            sv['ts'] = rv['ts']
            # sv['ts1'] = time.time()
            seqStart = int(seq.split("seq_")[1])
            # time.sleep(0.2)
            if mynode.sendingCnt > 0:
                time.sleep(mynode.sendingCnt / 500.)

            for i in range(0, C_Plen):
                seqi = seqStart + i 
                seqistr = 'ld_%sseq_%d'%(leaderID,seqi)
                if seqistr not in mynode.msgs["echo"]:
                    mynode.msgs["echo"][seqistr]={}
                if mynode.id not in mynode.msgs["echo"][seqistr]:
                    mynode.msgs["echo"][seqistr][mynode.id]=sv['hC_Ps']
                # mynode.msgs[tp][seqistr][yourid] = rv['C_Ps'][i]
            # print("%s echo ct= %s at %s"%(mynode.id, sv['hC_Ps'], sv['seq']), len(mynode.msgs["echo"][seqistr]))
            mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})  
        elif tp == "echo":
            
            seqStart = int(seq.split("seq_")[1])
            seqistr=seq
            for i in range(0, C_Plen):
                seqistr = 'ld_%sseq_%d'%(leaderID, seqStart + i )
                mynode.msgs[tp][seqistr][yourid] = rv['hC_Ps']
            sv = {"hC_Ps":rv['hC_Ps']}
            sv['epoch'] = epoch
            sv['seq'] = seq            
            sv['ts'] = rv['ts']
            # sv['ts1'] = rv['ts1']
            
            # print(mynode.id, "recieve echo from",yourid, seq, rv['hC_Ps'],len(mynode.msgs["echo"][seq]))
            if len(mynode.msgs["echo"][seqistr]) > 2*f or (seqistr in mynode.msgs["ready"] and len(mynode.msgs["ready"][seqistr]) > f):                
                if not mynode.msgs[sentProducer]:
                     mynode.msgs[sentProducer] = True
                else:
                    return                
                # sv['ts2'] = time.time() 
                # time.sleep(0.2) 
                if mynode.sendingCnt > 0: 
                    time.sleep(mynode.sendingCnt / 500)         
                
                
                seqStart = int(seq.split("seq_")[1])
                for i in range(0, C_Plen):
                    seqistr = 'ld_%sseq_%d'%(leaderID,seqStart  + i )
                    if seqistr not in mynode.msgs["ready"]:
                        mynode.msgs["ready"][seqistr]={}
                    if mynode.id not in mynode.msgs["ready"][seqistr]:
                        mynode.msgs["ready"][seqistr][mynode.id]=sv['hC_Ps']
                # print("node %s send ready ct: %s"%(mynode.id, sv['hC_Ps']))
                mynode.send_to_nodes({"type": "ready", "v": json.dumps(sv)}) 

        elif tp == "ready":
            
            # mynode.msgs[tp][seq][yourid] = rv['hC_Ps']
            seqStart = int(seq.split("seq_")[1])
            seqistr=seq
            for i in range(0, C_Plen):
                seqistr = 'ld_%sseq_%d'%(leaderID, seqStart + i )
                mynode.msgs[tp][seqistr][yourid] = rv['hC_Ps']

            if len(mynode.msgs["ready"][seqistr]) > 2*f:
                
                if not mynode.msgs[sentProducer]:
                     mynode.msgs[sentProducer] = True
                     for i in range(0, C_Plen):
                        seqistr = 'ld_%sseq_%d'%(leaderID, seqStart + i )
                        sentProducer = 'sent_%s_%s'%(tp, seqistr)
                        mynode.msgs[sentProducer] = True
                else:
                    return

                ts = time.time()
                print("%s (%s/%s) consensus on %s, initial time: %.2f, sendingCnt:%s"%\
                    ( mynode.id, mynode.curSeq[int(mynode.id)], mynode.seq, seq, ts-rv['ts'] ,mynode.sendingCnt) )
                # time.sleep(100)
                # print(seq, seqistr, mynode.msgs[tp][seqistr])
                if seq.startswith("ld_%sseq_"%(mynode.id)):
                    
                    while mynode.seq - config["C_Ptimes"]* C_Plen > mynode.curSeq[int(mynode.id)] :
                        time.sleep(1)

                    if CTs == None:
                        CTs = [json.loads(json.dumps(mynode.pvss.share())) for i in range(0, C_Plen)] 
                    # CTs = [json.loads(json.dumps(mynode.pvss.share())) for i in range(0, C_Plen)] 

                    sv={'C_Ps': CTs}        
                    sv['seq'] = "ld_%sseq_%d"%(mynode.id, mynode.seq)        
                    sv['epoch'] = epoch
                    sv['ts'] = time.time()
                    # sv['ts1'] = time.time()
                    hC_Ps = mynode.pvss.hash(sv['C_Ps'])
                    for i in range(0, C_Plen):
                        seqi = mynode.seq +i                    
                        seqistr = 'ld_%sseq_%d'%(leaderID, seqi)
                        if seqistr not in mynode.msgs["initial"]:
                            mynode.msgs["initial"][seqistr]={}
                        if mynode.id not in mynode.msgs["initial"][seqistr]:
                            mynode.msgs["initial"][seqistr][mynode.id]=sv['C_Ps'][i]
                        if seqistr not in mynode.msgs["echo"]:
                            mynode.msgs["echo"][seqistr]={}
                        if mynode.id not in mynode.msgs["echo"][seqistr]:
                            mynode.msgs["echo"][seqistr][mynode.id]=hC_Ps
                        
                    mynode.seq += C_Plen
                    mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)})  
                    print("node%s start to initial at seq:%s"%(mynode.id, mynode.seq))
                    sv['hC_Ps'] = hC_Ps
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
            if len(mynode.cis[tp][epoch]) > f:
                if str(L) not in mynode.msgs["initial"][seq]:
                    print("node %s str(L) not in mynode.msgs['initial'][seq]"%(mynode.id))
                    return
                if not mynode.cis[sentConsumer]:
                     mynode.cis[sentConsumer] = True
                else:
                    return
                # time.sleep(0.05) 
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
                # sv['ts1'] = rv['ts1']
                # sv['ts2'] = time.time()
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
                # time.sleep(0.05)                
                sv = {"beaconV":rv['beaconV']}
                sv['epoch'] = epoch
                sv['seq'] = seq            
                sv['newepoch'] = rv['newepoch']  
                sv['L'] = rv['L']                
                sv['Re_1'] = rv['Re_1']      
                sv['LQ'] = rv['LQ']
                sv['ts'] = rv['ts']
                # sv['ts1'] = rv['ts1']
                # sv['ts2'] = rv['ts2']
                # sv['ts3'] = time.time()
                
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
            
                # time.sleep(0.05) 
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
                
                printStr = "%s(%s/%s) epoch:%s"% (mynode.id,mynode.curSeq[int(mynode.id)], mynode.seq, epoch)
                printStr = printStr+ " Leader%s->%s %s, value: %s %.2fs/beacon per sendingCnt:%s "% (L, newL, seq, beaconV%100000,(time.time()-rv['ts'])/mynode.epoch, mynode.sendingCnt)
                printStr = printStr+ " producer SEND:%.2f"%(mynode.producerSentSize/(mynode.epoch+(n*config["C_Ptimes"]))/1024.)
                printStr = printStr+ " producer RCV:%.2f"%(mynode.producerRecvSize/(mynode.epoch+(n*config["C_Ptimes"]))/1024.)
                printStr = printStr+ " consumer SEND:%.2f"%(mynode.consumerSentSize/mynode.epoch/1024.)
                printStr = printStr+ " consumer RCV:%.2f"%(mynode.consumerRecvSize/mynode.epoch/1024.)
                
                
                print(printStr)
                     
                mynode.Re_1 = beaconV                
                mynode.epoch=rv['newepoch']
                mynode.L=L
                mynode.newL = newL
            
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

        for j in range(int(self.ID)+1, n+1):
            node.connect_with_node(config["nodes"][str(j)]["ip"],config["portBase"]+j)
            print("Node %s connect %d (%s:%d)"%(self.ID, j, config["nodes"][str(j)]["ip"], config["portBase"]+j))           
        time.sleep(int(ID)/3+10)
        v = {'pk':node.pvss.pk}
        v['epoch'] = -1
        v['seq'] = "ld_%sseq_%d"%(self.ID, -1) 
        node.send_to_nodes({"type": "pks", "v": json.dumps(v)})
        
        
        keys = list(node.CL.keys())
        node.newL = keys[node.Re_1 % len(node.CL)]
        
        print(node.id, "choose leader",node.newL)
        sentDict={}
        
        starttime = time.time()

        time.sleep(config['pkswait'])
        print("Node %s consumer starts"%node.id)
        lastReconn = time.time()
        while True:

            if len(node.nodes_outbound)+len(node.nodes_inbound) < n-1:                
                if time.time() - lastReconn > 5:
                    node.reconnect_nodes()    
                    lastReconn = time.time()
                # time.sleep(0.5)
                # print("node%s connections %d node.reconnect_nodes()==========================================="%(node.id, len(node.nodes_outbound)+len(node.nodes_inbound)))

            if node.epoch <= 2:
                starttime = time.time()

        #     # if "initial" in node.msgs and node.curSeq[node.L] in node.msgs["initial"]:
        #     #     print(len(node.msgs["initial"][node.curSeq[node.L]]))
            time.sleep(config['consumerSleep'])            
            if(node.newL == node.L):
                print("node.newL == node.L",node.L)
                continue
            if node.newL not in node.curSeq:
                print("node.newL not in node.curSeq")
                continue
            
            seq = "ld_%sseq_%d"%(node.newL, node.curSeq[node.newL])
            # print("node%s consume "%node.id, seq)
            sent = "sent_%s_%s"%("ready", seq)

            sent2 = "mynode_%sseq_%d"%(node.newL,node.curSeq[node.newL])
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
                # sv['ts1'] = time.time()
                # print("%s start to consume %d's %dth ciphertext %s cost:%s"%(node.id, node.newL, node.curSeq[node.newL], int(node.pvss.hash(EC))%100000, time.time()-starttime))  
                if sv['epoch'] not in node.cis['recon']:
                    node.cis['recon'][sv['epoch']] = {}
                # if sv['epoch'] not in node.cis['reconEcho']:
                #     node.cis['reconEcho'][sv['epoch']] = {}
                # if sv['epoch'] not in node.cis['reconReady']:
                #     node.cis['reconReady'][sv['epoch']] = {}
                node.cis['recon'][sv['epoch']][node.id] = sv['c_i']
                node.send_to_nodes({"type": "recon", "v": json.dumps(sv)})
            else:
                # if sent not in node.msgs :
                #     print(node.id,"wait for ",sent)
                if seq not in node.msgs["initial"]:
                    print(node.id,"wait for initial",seq, "connected nodes:%s"%(len(node.nodes_outbound)+len(node.nodes_inbound)))                    
                else:
                    if str(node.newL) not in node.msgs["initial"][seq] :
                        print(node.id,"wait for newL", str(node.newL), seq, "connected nodes:%s"%(len(node.nodes_outbound)+len(node.nodes_inbound)))                    
                    else:
                        print(node.id,"wait for >1", "connected nodes:%s"%(len(node.nodes_outbound)+len(node.nodes_inbound)))                    
           
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
    