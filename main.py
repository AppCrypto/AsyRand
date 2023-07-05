import sys
import time
import hashlib
sys.path.insert(0, '..') # Import the files where the modules are located

from p2pnetwork.node import Node
from P2P_network import ReliableBroadcast_p2p
localhost="127.0.0.1"
port_base=8000
IP_base=10000
n=10#总节点数
f=1#拜占庭节点数



init_p2pnet(10)
#nodes[1].send_to_nodes("message: hoi from node 1")
nodes[2].send_to_nodes({"type": "initial", "v": "to do something"})
