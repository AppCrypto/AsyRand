import os
import subprocess
import json
import sys,threading
# 读取ip.txt文件
loc2ips=json.loads(open('./cfg/ips.txt', 'r').read())
    
cmd="upload"
if len(sys.argv)>1:
    cmd=sys.argv[1]

def stream_output(ip, location, process):
    for line in process.stdout:
        print(f"{line}", end='')
    for line in process.stderr:
        print(f"[ERROR] {line}", end='')


# rsync -avz -e "ssh -i ./pem/BeaconTest_Singapore.pem -o StrictHostKeyChecking=no" ./ ubuntu@18.140.65.62:~/beacon/ &
# ssh -i ./pem/BeaconTest_Singapore.pem -o StrictHostKeyChecking=no ubuntu@3.0.95.226 "cd beacon && sh kill.sh" &
# ssh -i ./pem/BeaconTest_Singapore.pem -o StrictHostKeyChecking=no ubuntu@54.255.163.212 "cd beacon && python3 main.py realip" &
processes=[]
for location in loc2ips:    
    ips = loc2ips[location]    
    for ip in ips:

        pem_file = f"./pem/BeaconTest_{location}.pem"
        remote_path = f"ubuntu@{ip}:~/beacon/"
        commandstr = f'rsync -avz -e "ssh -i {pem_file}  -o StrictHostKeyChecking=no " ./ {remote_path} '
        if cmd=="start":
            remote_path = f'ubuntu@{ip} "cd beacon && python3 main.py realip"'
            commandstr = f'ssh -i ./pem/BeaconTest_{location}.pem -o StrictHostKeyChecking=no {remote_path}'
        if cmd=="kill":
            remote_path = f'ubuntu@{ip} "cd beacon && sh kill.sh"'
            commandstr = f'ssh -i ./pem/BeaconTest_{location}.pem -o StrictHostKeyChecking=no {remote_path}'
        if cmd=="clear":
            remote_path = f'ubuntu@{ip} "cd beacon && rm -rf *"'
            commandstr = f'ssh -i ./pem/BeaconTest_{location}.pem -o StrictHostKeyChecking=no {remote_path}'


        print(commandstr)    
        import sys
        if sys.version.startswith("3.6"):
            process = subprocess.Popen(commandstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            processes.append((ip, location, process))
            # 启动一个线程实时获取日志输出
            threading.Thread(target=stream_output, args=(ip, location, process)).start()
        else:
            process = subprocess.Popen(commandstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            processes.append((ip, location, process))
            # 启动一个线程实时获取日志输出
            threading.Thread(target=stream_output, args=(ip, location, process)).start()
        



for ip, location, process in processes:
    process.wait()
    if process.returncode == 0:
        print(f"successfully to {ip} at location {location}.")
    else:
        print(f"Failed to {ip} at location {location}.")






