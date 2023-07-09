import sys
import time
import hashlib
from P2PNetWork.Node import Node
sys.path.insert(0, '..') # Import the files where the modules are located
#from P2PNetWork.ExtendNode import BeaconNode
n=10#总节点数
f=3#拜占庭节点数



def see_node():
    for i in range(1, n + 1):
        nodes[i].print_connections()

def hash(str):
    m = hashlib.sha256()
    m.update(str.encode("utf8"))
    return m.hexdigest()
    return str


def InitP2Pnet(n):#n为整个网络的节点，目的是构建一个全连接的p2p网络，实现可广播
    IpBase=0   #节点IP值
    PortBase=10000   #端口号
    global nodes
    nodes=[]
    nodes.append(1)
    localhost = "127.0.0.1"
    for i in range(1,n+1):
        node = Node(localhost, PortBase+i, IpBase+i, callback=NodeCallBack)
        node.start()
        nodes.append(node)
    k=1
    for i in range(1,n+1):
        for j in range(k+1,n+1):
            nodes[i].connect_with_node(localhost,PortBase+j)
            #print(i)
            #print(j)
        k=k+1


def NodeCallBack(event, main_node, connected_node, data):#消费者模型
    try:
        if event == "node_message" and data["epoch"] not in main_node.NodesMessage:
            #print("{}收到,来自{},内容{}".format(main_node.id, connected_node.id, data))
            if data["type"]=="initial" and data["epoch"] not in main_node.NodesEchoList:
                main_node.NodesEchoList[data["epoch"]]= set()
                main_node.send_to_nodes({"epoch":data["epoch"],"type": "echo", "hv": hash(data["v"])})
                #print(str(main_node.id)+"已发送echo")
                #print(main_node.NodesEchoList)

            elif data["type"]=="echo":
                if data["epoch"] not in main_node.NodesEchoList:
                    main_node.NodesEchoList[data["epoch"]]=set()
                    main_node.NodesEchoList[data["epoch"]].add(connected_node.id)
                else:
                    main_node.NodesEchoList[data["epoch"]].add(connected_node.id)
                    if len(main_node.NodesEchoList[data["epoch"]])>((n+f)/2) and data["epoch"] not in main_node.NodesReadyList:
                        main_node.NodesReadyList[data["epoch"]]=set()
                        main_node.send_to_nodes({"epoch":data["epoch"],"type": "ready", "hv": data["hv"]})
            elif data["type"] == "ready":
                if data["epoch"] not in main_node.NodesReadyList:
                    main_node.NodesReadyList[data["epoch"]]=set()
                    main_node.NodesReadyList[data["epoch"]].add(connected_node.id)
                else:
                    main_node.NodesReadyList[data["epoch"]].add(connected_node.id)
                    if len(main_node.NodesReadyList[data["epoch"]])>(2*f):
                        print("第"+str(main_node.id)+"号节点完成共识"+str(data["epoch"])+"epoch的共识")
                        #CTl.push
                        main_node.NodesMessage.append(data["epoch"])
                    elif data["epoch"] not in main_node.NodesEchoList and len(main_node.NodesReadyList[data["epoch"]])>f:
                        main_node.send_to_nodes({"epoch": data["epoch"], "type": "ready", "hv": data["hv"]})
    except Exception as e:
        print(e)

InitP2Pnet(10)#节点数量，存储节点字典，端口号起始基
#see_node()
#nodes[1].send_to_nodes("message: hoi from node 1")

see_node()
nodes[1].send_to_nodes({"epoch": 1, "type": "initial", "v": "do something"})

time.sleep(5)
#nodes[5].send_to_nodes({"epoch": 2, "type": "initial", "v": "to do something"})
for i in range(1,11):
    print("第"+str(i)+"号节点")
    print(nodes[i].NodesMessage)
    print(nodes[i].NodesEchoList)
    print((nodes[i].NodesReadyList))

#nodes[3].send_to_nodes({"epoch":2,"type": "initial", "v": "to do something2"})
time.sleep(1)
#nodes[5].NodeMessage.append(5)


"""#连续发送生产消息
for i in range(1,10000):
    nodes[i%10].send_to_nodes({"epoch": i, "type": "initial", "v": "do something"})
    time.sleep(0.01)
"""
