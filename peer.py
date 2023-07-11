import sys,os
import time
import hashlib,requests
from node import Node
# sys.path.insert(0, '..') # Import the files where the modules are located
import newjson as json,threading,multiprocessing
from multiprocessing import Process, Manager 
 


from flask import Flask, render_template,request,jsonify,redirect,url_for,send_from_directory
from config import config
import queue

ID = sys.argv[1]

n=len(config["nodes"])
f=int((len(config["nodes"]) -1)/3)
        
ip = config["nodes"][ID]["ip"]
port = config["portBase"] + int(ID)


# EP = 1

def callback(event, mynode, yournode, data):
    if event == "node_message":        
        
        tp = data['type']
        rv = json.loads(data['v'])
        epoch = rv['epoch']        
        seq = rv['seq']
        yourid = yournode.id
        # print("node:%s recieve type:%s from mode:%s"%(mynode.id, tp, yournode.id))
        


        # if epoch not in mynode.msgs:
        #     mynode.msgs[epoch]={}
        # if yournode not in mynode.msgs[epoch]:
        #     mynode.msgs[epoch][yourid]={}

        if tp not in mynode.msgs:
            mynode.msgs[tp]={}      
        
        # key = "seq%d_node%s"%(seq, yournode.id)
        # if key not in mynode.msgs[tp]:
        #     mynode.msgs[tp][key]={}
        if seq not in mynode.msgs[tp]:
            mynode.msgs[tp][seq] = {}
        if epoch not in mynode.msgs[tp][seq]:
            mynode.msgs[tp][seq][epoch]={}
          
        # if "seq_%d"%seq not in mynode.msgs:
        #     mynode.msgs["seq_%d"%seq] = {}
        sent = "sent_%s_%s"%(tp, seq)
        if sent not in mynode.msgs:
            mynode.msgs[sent] = False

        if tp == "pks":
            mynode.pvss.setPK(int(yourid), rv['pk'])
            # print("node:%s's pks length:%d"%(mynode.id, len(mynode.pvss.pks)))
            if len(mynode.pvss.pks) == len(config['nodes']):                      
                time.sleep(3)
                # print(mynode.pvss.pks)
                # time.sleep(100)
                sv={'C_P': json.loads(json.dumps(mynode.pvss.share(n,f+1)))}
                sv['epoch'] = epoch
                mynode.seq += 1 
                sv['seq'] = "seq_%d"%mynode.seq
                
                mynode.msgs[tp][sv['seq']]={}
                mynode.msgs[tp][sv['seq']][mynode.id]=sv['C_P']
                # mynode.msgs[sent] = True

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
            # time.sleep(0.2)         
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
                # time.sleep(0.2)
                if not mynode.msgs[sent]:
                     mynode.msgs[sent] = True
                else:
                    return                

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
                time.sleep(0.5)
                if not mynode.msgs[sent]:
                     mynode.msgs[sent] = True
                else:
                    return
                # if "initial" in mynode.msgs:
                #     print("node %s reach consensus on %s"%(mynode.id, mynode.msgs["initial"][seq][mynode.id]))
                sv={'C_P': json.loads(json.dumps(mynode.pvss.share(n,f+1)))}
                sv['epoch'] = epoch
                mynode.seq += 1 
                sv['seq'] = "seq_%d"%mynode.seq
                
                
                # print("%s initial ct= %s at %s"%(mynode.id, mynode.pvss.hash(sv['C_P']), sv['seq']))

                if "initial" not in mynode.msgs:
                    mynode.msgs["initial"]={}
                if sv['seq'] not in mynode.msgs["initial"]:
                    mynode.msgs["initial"][sv['seq']]={}
                if mynode.id not in mynode.msgs["initial"][sv['seq']]:
                    mynode.msgs["initial"][sv['seq']][mynode.id]=sv['C_P']
                
                mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)})  
        elif tp == "reconstruct":
            # print(mynode.id, tp, epoch, yourid)
            mynode.msgs[tp][seq][epoch][yourid] = rv['c_i']
            
            if len(mynode.msgs[tp][seq][epoch]) > 2*f:#TODO f
                C=mynode.msgs["initial"][seq][rv['L']]['C']
                # print(mynode.msgs[tp][seq])
                # cis = {}                
                # print(mynode.msgs[tp][seq][epoch])
                gs = mynode.pvss.recon(C, mynode.msgs[tp][seq][epoch])
                beaconV = mynode.pvss.hash(str(rv['Re_1'])+str(gs))
                print("Node %s at epoch:%s, output beacon value: %s"%(mynode.id, epoch, beaconV))
                # mynode.reconnect_nodes()
                # sv = {"beacon": }
                # sv['epoch'] = -1
                # sv['seq'] = seq
                                
            



class Peer():    
    def __init__(self, ID):
        self.ID= ID
        self.config = config
        
        node = Node(ip, port, ID, callback)
        node.start()

        time.sleep(2)
        for j in range(int(ID)+1, n+1):
            node.connect_with_node(ip,config["portBase"]+j)
            print("Node %s connect %d"%(self.ID, j))           
        time.sleep(2)  
        v = {'pk':node.pvss.pk}
        v['epoch'] = 'l_%se_%d'%(1,-1)
        v['seq'] = "seq_%d"%(-1) 
        node.send_to_nodes({"type": "pks", "v": json.dumps(v)})
        
        self.epoch=1
        self.curSeq = {i:1 for i in range(1, n+1)}
        self.LQ = queue.Queue(f)
        [self.LQ.put(i) for i in range(1,f+1)]
        self.CL = {}
        for i in range(f+1, n+1):
            self.CL={i:True}
        
        self.Re_1=config['Re_1']
        # self.L = config['Re_1']
        self.CTL=node.msgs
        keys = list(self.CL.keys())
        self.L = keys[self.Re_1 % (n-f)]
        print(node.id, "choose leader",self.L)

        while True:
            # if "initial" in self.CTL and self.curSeq[self.L] in self.CTL["initial"]:
            #     print(len(self.CTL["initial"][self.curSeq[self.L]]))
            time.sleep(0.5)
            # print(self.CTL)
            seq = "seq_%d"%self.curSeq[self.L]
            sent = "sent_%s_%s"%("ready", seq)

            # print(sent in node.msgs and node.msgs[sent], (seq in self.CTL["initial"]),seq, str(self.L) in self.CTL["initial"][seq])
            if sent in node.msgs and node.msgs[sent] and \
                (seq in self.CTL["initial"] and \
                 str(self.L) in self.CTL["initial"][seq]) and \
                 len(self.CTL["initial"][seq][str(self.L)])>1 :
                oldL= self.LQ.get()
                self.LQ.put(self.L)
                if self.L in self.CL:
                    del self.CL[self.L]
                EC = self.CTL["initial"][seq][str(self.L)]
                # print(EC)
                sv = {'c_i': node.pvss.preRecon(EC['C'], self.ID)}
                sv['epoch'] = 'l_%de_%d'%(self.L, self.epoch)
                sv['L'] = str(self.L)
                sv['seq'] = seq
                sv['Re_1'] = self.Re_1
                # print("%s consume %d's %dth ciphertext %s"%(node.id, self.L, self.curSeq[self.L], node.pvss.hash(EC)))  
                node.send_to_nodes({"type": "reconstruct", "v": json.dumps(sv)})
                self.curSeq[self.L]+=1
                # self.epoch+=1
                
                # epoch ++ TODO


if __name__ == '__main__':    
    peer = Peer(ID)
