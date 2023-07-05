import sys
import time
import hashlib
sys.path.insert(0, '..') # Import the files where the modules are located

from p2pnetwork.node import Node
localhost="127.0.0.1"
port_base=8000
IP_base=10000
n=10#总节点数
f=1#拜占庭节点数
nodes = []
#for test
nodes_data=[]
def hash(str):
    m = hashlib.sha256()
    m.update(str.encode("utf8"))
    return m.hexdigest()
    return str

def node_callback(event, main_node, connected_node, data):
    echo_sent_list = dict()  # Check if echo has been sent and collect echo messages
    ready_sent_list = dict()    # Check if ready has been sent and collect ready messages
    delivered_msgs = list()   # Keep delivered messages
    try:
        #if event != 'node_request_to_stop': # node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
            #print('Event: {} from main node {}: connected node {}: {}'.format(event, main_node.id, connected_node.id, data))
        if event == "node_message":
            print("{}收到,来自{},内容{}".format(main_node.id,connected_node.id,data))
            if data["type"]=="initial":
                main_node.send_to_nodes({"type": "echo", "hv": hash(data["v"])})
            elif data["type"]=="echo":
                if



    except Exception as e:
        print(e)

def init_p2pnet(n):#n为整个网络的节点，目的是构建一个全连接的p2p网络，实现可广播

    nodes.append(1)
    for i in range(1,n+1):
        node = Node("127.0.0.1", port_base+i, IP_base+i, callback=node_callback)
        node.start()
        nodes.append(node)

    k=1
    for i in range(1,n+1):
        for j in range(k+1,n+1):
            nodes[i].connect_with_node(localhost,port_base+j)
            #print(i)
            #print(j)
        k=k+1




def see_node():
    for i in range(1, n + 1):
        nodes[i].print_connections()


