import sys,os
import time,json
import hashlib
# import pvss

config = json.loads(open("./nodeConfiguration.json","r").read())


os.system("ps -ef|grep 'peer.py' |awk '{print $2}'|xargs kill -9")
time.sleep(1)
# os.system("rm err.txt")
for i in range(1, len(config["nodes"])+1):
    # print("python3 peer.py "+str(i))
    os.system("python3 peer.py "+str(i) + "&" )

# time.sleep(120)
