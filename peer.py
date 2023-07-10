import sys,os
import time
import hashlib,requests
from node import Node
# sys.path.insert(0, '..') # Import the files where the modules are located
import newjson as json,threading,multiprocessing
from multiprocessing import Process, Manager 
 


from flask import Flask, render_template,request,jsonify,redirect,url_for,send_from_directory
from config import config

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
        # print("node:%s recieve type:%s from mode:%s friends: %d"%(mynode.id, tp, yournode.id, len(mynode.all_nodes)))
        


        if epoch not in mynode.msgs:
            mynode.msgs[epoch]={}
        if tp not in mynode.msgs:
            mynode.msgs[tp]={}        
        if seq not in mynode.msgs[tp]:
            mynode.msgs[tp][seq] = {}
        sent = "sent_%s_%d"%(tp, seq)
        if sent not in mynode.msgs:
            mynode.msgs[sent] = {}

        if tp == "pks":
            mynode.pvss.setPK(int(yourid), rv['pk'])
            # print("node:%s's pks length:%d"%(mynode.id, len(mynode.pvss.pks)))
            if len(mynode.pvss.pks) == len(config['nodes']):                      
                time.sleep(1)
                sv={"shares": mynode.pvss.share(n,f+1)}
                sv['epoch'] = -1
                sv['seq'] = mynode.seq
                mynode.seq += 1 
                mynode.msgs[tp][sv['seq']]={}
                mynode.msgs[tp][sv['seq']][mynode.id]=sv["shares"]
                # mynode.msgs[sent] = True
                mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)})  
        elif tp == "initial":
            mynode.msgs[tp][seq][yourid] = rv['shares']
            sv = {"hshares":mynode.pvss.hash(str(rv['shares']))}
            sv['epoch'] = -1
            sv['seq'] = seq           
            # time.sleep(0.2)         
            mynode.send_to_nodes({"type": "echo", "v": json.dumps(sv)})  
        elif tp == "echo":
            mynode.msgs[tp][seq][yourid] = rv['hshares']
            sv = {"hshares":rv['hshares']}
            sv['epoch'] = -1
            sv['seq'] = seq            
            if len(mynode.msgs["echo"][seq]) > 2*f or ("ready" in mynode.msgs and seq in mynode.msgs["ready"] and len(mynode.msgs["ready"][seq]) > f):
                # time.sleep(0.2)
                if not mynode.msgs[sent]:
                     mynode.msgs[sent] = True
                else:
                    return
                mynode.send_to_nodes({"type": "ready", "v": json.dumps(sv)}) 
        elif tp == "ready":
            mynode.msgs[tp][seq][yourid] = rv['hshares']
            sv = {"hshares":rv['hshares']}
            sv['epoch'] = -1
            sv['seq'] = seq
            if len(mynode.msgs["ready"][seq]) > 2*f:
                # mynode.reconnect_nodes()
                # time.sleep(0.2)
                if not mynode.msgs[sent]:
                     mynode.msgs[sent] = True
                else:
                    return
                print("node %s goto next produce %d"%(mynode.id, mynode.seq))
                sv={"shares": mynode.pvss.share(n,f+1)}
                sv['epoch'] = -1
                sv['seq'] = mynode.seq
                mynode.seq += 1 
                mynode.msgs[tp][sv['seq']]={}
                mynode.msgs[tp][sv['seq']][mynode.id]=sv["shares"]                
                mynode.send_to_nodes({"type": "initial", "v": json.dumps(sv)})  
                



class Peer():    
    def __init__(self, ID):
        self.ID= ID
        self.config = config
        
        node = Node(ip, port, ID, callback)
        node.start()

        time.sleep(2)
        for j in range(int(ID)+1,len(config["nodes"])+1):
            node.connect_with_node(ip,config["portBase"]+j)
            print("Node %s connect %d"%(self.ID, j))           
        time.sleep(2)  
        v = {'pk':node.pvss.pk}
        v['epoch'] = -1
        v['seq'] = -1
        node.send_to_nodes({"type": "pks", "v": json.dumps(v)})
        

    # def broadcast(self, content):
        

if __name__ == '__main__':    
    peer = Peer(ID)
