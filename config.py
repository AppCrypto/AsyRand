import newjson as json


config = json.loads(open("./cfg/cfg.json","r").read())
if "keys" not in config:
	config["keys"]=json.loads(open("./cfg/keys.txt","r").read())

loc2ips=json.loads(open('./cfg/ips.txt', 'r').read())
i=1
for location in loc2ips:    
    ips = loc2ips[location]    
    for ip in ips:
        config['nodes'][str(i)]={"ip":ip}
        i+=1
config['initwait'] = i/2
# print(config)