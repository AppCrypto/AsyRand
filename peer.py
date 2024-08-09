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

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
WHITE = "\033[37m"
RESET = "\033[0m"

ip = config["nodes"][ID]["ip"]
port = config["portBase"] + int(ID)
C_Plen = config["C_Plen"]
CTs = None

n=len(config["nodes"])
f=int((n -1)/3)

def init_dict(d, *keys):
    if len(keys) < 2:
        return
    for key in keys[:-2]:
        key=str(key)
        if key not in d:
            d[key] = {}
        d = d[key]
    key2=str(keys[-2])
    d[key2] = keys[-1]

def get_value(d, *keys):
    current = d
    for key in keys:
        key = str(key)
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None  
    return current

def get_value2(d, *keys):
    res= get_value(d,*keys) 
    if res == None:
        res = {}
    return res

def myprint(str):
    print(str)
    with open('log.txt', 'a') as f:
        print(str, file=f)



def callback(event, mynode, yournode, data):
    # global CTs
    thread_id = threading.get_ident()    
    if event == "node_message":        
        # print(data)
        tp = data['type']
        rv = json.loads(data['v'])
        yourid = yournode.id

        

        
        log=f"{mynode.id}-{yourid} thread {thread_id} start {tp}-"
        
        if tp in ["initial","echo", "ready"]:
            mynode.producerRecvSize+=len(str(base64.b64encode(zlib.compress(str(data).encode('utf-8'), 6) + b'zlib')))   
            # TODO
            # if mynode.curSeq[int(mynode.id)] >= rv['seqs'][0] + 10:
            #     print(f"node{mynode.id} {tp}-------------------------------------------------------{mynode.epoch} >= {rv['newepoch']}")
            #     return
            log+=str(rv['seqs'])
            for seq in rv['seqs']:   
                if get_value(mynode.sentTP,tp,rv['ld'],seq) == None:
                    init_dict(mynode.sentTP,tp,rv['ld'],seq,False)                
                
        elif tp in ["recon", "reconEcho", "reconReady"]:
            mynode.consumerRecvSize+=len(str(base64.b64encode(zlib.compress(str(data).encode('utf-8'), 6) + b'zlib')))   
            # TODO TEST
            # if mynode.epoch >= rv['newepoch']:
            #     print(f"node{mynode.id} {tp}-------------------------------------------------------{mynode.epoch} >= {rv['newepoch']}")
            #     return
        
            log+=str(rv['epoch'])
            # print(f"node{mynode.id}<-{yourid} at epoch:{rv['epoch']}, receive broadcast type {tp} thread:{thread_id}") 
            if get_value(mynode.sentTP,tp,rv['epoch']) == None:                
                init_dict(mynode.sentTP,tp,rv['epoch'],False)
        # print(f"{log} start")                  
                        
        if tp == "initial":
            comts = rv['comts']
            sv={}
            sv['seqs']=rv['seqs']
            sv['ld']=rv['ld']
            ld=rv['ld']

            for seq in comts:            
                comt = comts[seq]
                init_dict(mynode.msgs, tp,ld,seq,yourid,comt)                
                mynode.pvss.verify(comt["C"], comt["pi"])
            sv["comtsH"]=mynode.pvss.hash(rv['comts'])            
            sv['ts'] = rv['ts']
            for seq in comts:
                init_dict(mynode.msgs, "echo", mynode.id,seq,mynode.id,sv['comtsH'])
            mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})  
        elif tp == "echo":
            sv = {}
            comtsH = rv['comtsH']
            seqs=rv['seqs']
            sv['ld']=rv['ld']
            ld=rv['ld']
            for seq in seqs:
                init_dict(mynode.msgs, tp, ld,seq,yourid,comtsH)
            
            sv['comtsH']=comtsH
            sv['seqs'] = seqs            
            sv['ts'] = rv['ts']
            
            # print(mynode.id, "recieve echo from",yourid, seq, comtsH,len(mynode.msgs["echo"][seq]))
            echoSenders = get_value2(mynode.msgs, "echo",ld, seqs[0])
            readySenders = get_value2(mynode.msgs, "ready",ld, seqs[0])
            if (len(echoSenders) > 2*f) or (len(readySenders) > f):
                for seq in seqs:
                    if get_value(mynode.sentTP,tp,ld,seq):
                        return                                
                    init_dict(mynode.sentTP,tp,ld,seq,True)
                    init_dict(mynode.msgs, 'ready',ld,seq,mynode.id,sv['comtsH'])
                mynode.send_to_nodes({"type": "ready", "v": json.dumps(sv)}) 

        elif tp == "ready":
            comtsH = rv['comtsH']
            seqs=rv['seqs']
            ld=rv['ld']
            for seq in seqs:
                init_dict(mynode.msgs, tp,ld,seq,yourid,comtsH)
            readySenders = get_value2(mynode.msgs, "ready",ld, seqs[0])
            if len(readySenders) > 2*f: 
                for seq in seqs:
                    if get_value(mynode.sentTP,tp,ld,seq):
                        return
                    init_dict(mynode.sentTP,tp,ld,seq,True)                    
                    myprint(f"{mynode.id} ({mynode.curSeq[int(mynode.id)]}/{mynode.seq}) reaches consensus on " +
                        f"leader {ld}'s {seq}th commitment, {WHITE}%.2fs{RESET}/PVSS commitment"%(time.time()-rv['ts']))
                                
        elif tp == "recon":
            epoch = rv['epoch']            
            seq = rv['seq']
            Re_1=rv['Re_1']
            newepoch = rv['newepoch']
            L=rv['L']
            LQ = rv['LQ']
            Re_1=rv['Re_1']                        
            

            comt = get_value(mynode.msgs,"initial",L,seq,L)# initial message is from L
            if get_value(mynode.sentTP,tp,epoch):#to accerlate in case another thread is running
                init_dict(mynode.cis,tp,epoch,yourid,{'ci':rv['c_i'], 'check':False})  
                return    
            flag=False
            if comt != None:
                flag= mynode.pvss.vrfRecon(comt['C']["C1"][yourid], yourid, rv['c_i'])
            init_dict(mynode.cis,tp,epoch,yourid,{'ci':rv['c_i'], 'check':flag})  

            reconSenders = get_value2(mynode.cis,tp,epoch)
            if comt!=None and len(reconSenders) > f:
                if get_value(mynode.sentTP,tp,epoch):
                    return
                cis={}
                ci2k=get_value(mynode.cis,tp,epoch).copy()
                for yid in ci2k:
                    if get_value(mynode.sentTP,tp,epoch):#to accerlate in case another thread is running
                        return    
                    if get_value(mynode.cis,tp,epoch,yourid,'check')\
                        or mynode.pvss.vrfRecon(comt['C']["C1"][yid], yid, ci2k[yid]["c_i"]):
                            cis[yid]=ci2k[yid]                    
                if len(cis.keys())<=f:
                    return
                init_dict(mynode.sentTP,tp,epoch,True)
                gs = mynode.pvss.recon(comt['C'], cis, False)                
                beaconV = int(mynode.pvss.hash(str(Re_1)+str(gs)))                
                sv={}        
                sv['beaconV']=beaconV
                for field in ['epoch','seq','newepoch','L','LQ','Re_1']:
                    sv[field] = rv[field]
                                   
                init_dict(mynode.cis,"reconEcho",epoch,mynode.id,sv)
                mynode.send_to_nodes({"type": "reconEcho", "v": json.dumps(sv)})
        elif tp == "reconEcho":   
            epoch = rv['epoch']                     
            init_dict(mynode.cis,tp,epoch,yourid,rv)

            reconReadySenders=get_value2(mynode.cis,"reconReady",epoch)
            reconEchoSenders=get_value2(mynode.cis,"reconEcho",epoch)            
            # print(f"=========node{mynode.id},{tp}, {mynode.cis[tp]}")
            if len(reconEchoSenders) > 2*f or len(reconReadySenders) > f:                
                if get_value(mynode.sentTP,tp,epoch): 
                    return                                 
                init_dict(mynode.sentTP,tp,epoch,True)

                sv={}
                for field in ['beaconV','epoch','seq','newepoch','L','LQ','Re_1']:
                    sv[field] = rv[field]
                
                init_dict(mynode.cis,"reconReady",epoch,mynode.id,sv)
                # print(f"\nnode{mynode.id} at epoch:{epoch}, broadcast 'reconReady'") 
                mynode.send_to_nodes({"type": "reconReady", "v": json.dumps(sv)})
            # else:
            #     print(f"node{mynode.id} at {tp}, epoch: {epoch} {reconEchoSenders.keys()}, 'reconReady', {reconReadySenders.keys()}") 
        elif tp == "reconReady":
            epoch = rv['epoch']            
            init_dict(mynode.cis,"reconReady",epoch,yourid,rv)
            
            reconReadySenders=get_value2(mynode.cis,"reconReady",epoch)
            # print(f"\n=========node{mynode.id},{tp}, {mynode.cis[tp]}\n")
            if len(reconReadySenders) > 2*f: 
                if get_value(mynode.sentTP,tp,epoch): 
                    return                     
                
                init_dict(mynode.sentTP,tp,epoch,True)
                            
                if mynode.epoch >= rv['newepoch']:
                    print("node{mynode.id} {tp}-------------------------------------------------------mynode.epoch >= rv['newepoch']")
                    return
            
                
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
                newL = keys[int(beaconV) % len(keys)]
                mynode.Re_1 = beaconV                
                mynode.epoch=rv['newepoch']
                mynode.L=L
                mynode.newL = newL

                proSendSize=mynode.producerSentSize
                proRcvSize=mynode.producerRecvSize
                conSendSize=mynode.consumerSentSize
                conRcvSize=mynode.consumerRecvSize
                printStr = f"%s(%s/%s) {time.time()} epoch:%s"% (mynode.id,mynode.curSeq[int(mynode.id)], mynode.seq, epoch)
                printStr = printStr+ f" Leader from{L}->{newL} consuming, value: ***{beaconV%100000} " +\
                f"({RED}%.2fs{RESET}, {BLUE}%2.fkB{RESET})/beacon"% ( (time.time()-mynode.starttime)/mynode.epoch, (proSendSize+proRcvSize+conSendSize+conRcvSize)/mynode.epoch/1024.)
                
                myprint(printStr) 


                # leaderID = mynode.L
                # leaderSeq=mynode.curSeq[leaderID]
                # for tpi in ["initial","echo", "ready"]:
                #     for j in range(10,20):
                #         del mynode.msgs[tpi][str(leaderID)][str(leaderSeq-j)]
                # for tpi in ["recon", "reconEcho", "reconReady"]:
                #     for j in range(10,20):
                #         del mynode.cis[tpi][str(epoch-j)]
                        
                


class BaseThread(threading.Thread):
    def __init__(self, ID, node):
        super().__init__()
        self.ID = ID
        self.node = node

    def run(self):
        raise NotImplementedError("Subclasses must implement this method")



class Producer(BaseThread):
    def run(self):              
        mynode=self.node   
        while True:
            if len(node.nodes_outbound)+len(node.nodes_inbound) == n-1:
                break
            time.sleep(0.5)
        time.sleep(5)
        print(f"{mynode.id} producer starts")
        
        while True:        
            sv={}
            sv['seqs']=[]
            sv['ld']=mynode.id
            comts={}
            for i in range(0, C_Plen):
                comts[mynode.seq]=json.loads(json.dumps(mynode.pvss.share()))
                sv['seqs'].append(mynode.seq) 
                mynode.seq+=1          
                # print("mynode.seq+=1 in ready")                  
            
            sv['comts']=comts
            sv['ts'] = time.time()      
            ld=mynode.id                       
            
            # mynode.sentTP[tp][ld][seqs[0]]=True
            comtsH = mynode.pvss.hash(sv['comts'])                                
            for seq in comts:
                init_dict(mynode.msgs, "initial",ld,seq,mynode.id,comts[seq])
                init_dict(mynode.msgs, "echo",ld,seq,mynode.id,comtsH)                                             
            sv['ld']=ld
            mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)})                 
            sv['comtsH'] = comtsH                
            # print(f"node{mynode.id} send initial message of seq:{mynode.seq}")  
            del sv['comts']
            mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})                     
            
            while True:
                # if mynode.seq - config["C_Ptimes"]* C_Plen > mynode.curSeq[int(mynode.id)] :            
                if mynode.seq - 3 > mynode.curSeq[int(mynode.id)] :            
                    time.sleep(1)
                else:
                    break
                # else:
                #     if random.random()>0.7:
                #         break
                #     else:
                #         time.sleep(1)



class Consumer(BaseThread):
    def start(self):
        sentDict={}
        
        keys = list(node.CL.keys())
        node.newL = keys[node.Re_1 % len(node.CL)]                        
        
        while True:
            if len(node.nodes_outbound)+len(node.nodes_inbound) == n-1:
                break
            time.sleep(0.5)
        time.sleep(10)
        print("Node %s consumer starts"%node.id)
        node.starttime=time.time()
        lastReconn = time.time()
        while True:
            if len(node.nodes_outbound)+len(node.nodes_inbound) < n-1:                
                if time.time() - lastReconn > 5:
                    print(f"node:{node.id} reconnect_nodes: {len(node.nodes_outbound)+len(node.nodes_inbound)}, then reconnection")
                    node.reconnect_nodes()    
                    lastReconn = time.time()                    
                    
            time.sleep(config['consumerSleep'])            
            if(node.newL == node.L):
                print("node.newL == node.L",node.L)
                continue
            if node.newL not in node.curSeq:
                print("node.newL not in node.curSeq")
                continue
            
            seq = node.curSeq[node.newL]

            sent2 = "mynode_%sseq_%d"%(node.newL,seq)
            if sent2 in sentDict:           
                # print(f"node {node.id} has {sent2} in sentDict at epoch:{node.epoch}")
                # time.sleep(10)
                continue
            
            comt = get_value(node.msgs,"initial",node.newL,seq,node.newL)
            # print(f"node{node.id}'s ld:{node.newL} initial conent: {get_value(node.msgs,'initial',node.newL,seq,node.newL)}")
            if comt !=None:    
                sentDict[sent2]=True
                sv = {}
                sv['c_i']=node.pvss.preRecon(comt['C'], node.id)                
                sv['epoch'] = node.epoch
                sv['newepoch'] = node.epoch+1
                sv['L'] = node.newL
                sv['LQ']=list(node.LQ.all())               
                sv['seq'] = seq
                sv['Re_1'] = node.Re_1                
                
                init_dict(node.cis,'recon',sv['epoch'],node.id, sv['c_i'])
                # print(f"node{node.id} at epoch:{node.epoch}, broadcast 'recon'") 
                node.send_to_nodes({"type": "recon", "v": json.dumps(sv)})

            # else:
            #     # get_value(node.msgs,"initial",node.newL,seq)!=None:    
            #     print(f"node:{node.id} waits for initial message of seq:{seq}")                    
            
           
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
    node = Node(ip, port, ID, callback)    
    node.setDaemon(True)    
    node.start()   
    time.sleep(10)# ssh remotestart.sh
    for j in range(int(ID)+1, n+1):
        node.connect_with_node(config["nodes"][str(j)]["ip"],config["portBase"]+j)
        print("Connceting  Node %s <----> %d (%s:%d)"%(ID, j, config["nodes"][str(j)]["ip"], config["portBase"]+j))           
    
    
    for i in range(1, n+1):
        node.pvss.setPK(i, config["keys"][str(i)]["pk"])
    node.pvss.setKey(config["keys"][node.id])
    

    consumer = Consumer(ID,node)
    consumer.setDaemon(True)
    producer=Producer(ID,node)
    producer.setDaemon(True)
    

    producer.start()
    consumer.start()
    producer.join()
    consumer.join()
    node.join()

    # app = MyThread(peer.node)
    # app.start()
    
    