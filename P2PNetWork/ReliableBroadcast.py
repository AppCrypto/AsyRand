from P2P_network.Node import Node
import hashlib

def hash(str):
    m = hashlib.sha256()
    m.update(str.encode("utf8"))
    return m.hexdigest()
    return str
