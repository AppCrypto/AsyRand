import sys,os
import time,json
import hashlib
# import pvss

config = json.loads(open("./nodeConfiguration.json","r").read())


import requests

def get_external_ip():
    try:
        ip = requests.get("http://jsonip.com/").json().get('ip')
        return ip
    except:
        return None 

myip= "127.0.0.1"

if len(sys.argv)>1 and sys.argv[1] == "realip":
    myip = get_external_ip()
    print(myip)

    

os.system("ps -ef|grep 'peer.py' |awk '{print $2}'|xargs kill -9")
time.sleep(1)
for i in range(1, len(config["nodes"])+1):
    if config['nodes'][str(i)]["ip"] == myip:
        os.system("python3 peer.py "+str(i) + "&" )

