import sys
import time
import hashlib
from P2P_network.Node import Node
from P2P_network.ReliableBroadcast_p2p import hash
sys.path.insert(0, '..') # Import the files where the modules are located

localhost="127.0.0.1"
n=10#总节点数
f=1#拜占庭节点数
nodes = []
#for test
echo_sent_list = list()  #
ready_sent_list = list()
 # Check if ready has been sent and collect ready messages
delivered_msgs = list()
hash_msgs=list()

def see_node():
    for i in range(1, n + 1):
        nodes[i].print_connections()



def node_callback(event, main_node, connected_node, data):

    try:
        #if event != 'node_request_to_stop': # node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
            #print('Event: {} from main node {}: connected node {}: {}'.format(event, main_node.id, connected_node.id, data))
        if event == "node_message":
            print("{}收到,来自{},内容{}".format(main_node.id,connected_node.id,data))
            if data["type"]=="initial" and data["v"] not in delivered_msgs :
                delivered_msgs.append(data["v"])
                hash_msgs.append(hash(data["v"]))
                main_node.send_to_nodes({"type": "echo", "hv": hash(data["v"])})
                #print(delivered_msgs)
            elif data["type"]=="echo" and main_node.id not in echo_sent_list and data["hv"] in hash_msgs:
                #print(main_node.id)
                echo_sent_list.append(main_node.id)
                time.sleep(0.001)
                if len(echo_sent_list)>=((n+f+1)/2) or len(ready_sent_list)>(f+1):
                    main_node.send_to_nodes({"type":"ready","hv":data["hv"]})
            elif data["type"]=="ready" and main_node.id not in ready_sent_list and data["hv"] in hash_msgs:
                ready_sent_list.append(main_node.id)
                time.sleep(0.001)
                if len(ready_sent_list)>=(2*f+1) :
                    print(main_node.id+delivered_msgs[-1]+"\n")
                    time.sleep(0.001)
                    ready_sent_list.clear()
                    echo_sent_list.clear()

    except Exception as e:
        print(e)

def init_p2pnet(n):#n为整个网络的节点，目的是构建一个全连接的p2p网络，实现可广播
    IP_base=10000
    port_base=8000
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



init_p2pnet(10)#节点数量，存储节点字典，端口号起始基
#nodes[1].send_to_nodes("message: hoi from node 1")
see_node()
print(nodes)
nodes[2].send_to_nodes({"type": "initial", "v": "to do something"})
print(delivered_msgs)
print(hash_msgs)

