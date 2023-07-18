
# ssh -i BeaconTest_canada.pem ubuntu@15.156.141.12 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_canada.pem ubuntu@3.96.70.23 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_canada.pem ubuntu@3.98.6.204 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_canada.pem ubuntu@3.99.17.175 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_Singapore.pem ubuntu@122.248.197.195 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_Singapore.pem ubuntu@175.41.153.64 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_Singapore.pem ubuntu@52.77.191.56 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_Singapore.pem ubuntu@54.255.77.91 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_Seoul.pem ubuntu@13.125.136.55 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_Seoul.pem ubuntu@3.36.157.62 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_Seoul.pem ubuntu@52.79.113.39 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_Seoul.pem ubuntu@54.180.171.139 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_California.pem ubuntu@13.52.162.138 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_California.pem ubuntu@52.8.110.149 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_California.pem ubuntu@52.8.196.35 "cd beacon && python3 main.py realip" &
ssh -i BeaconTest_California.pem ubuntu@54.67.73.60 "cd beacon && python3 main.py realip" &

ssh -i  BeaconTest_Osaka.pem ubuntu@13.208.104.15  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Osaka.pem ubuntu@15.152.238.217  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Osaka.pem ubuntu@15.168.45.36  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Osaka.pem ubuntu@15.168.59.238  "cd beacon && python3 main.py realip" &

ssh -i  BeaconTest_Ireland.pem ubuntu@18.202.125.41  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Ireland.pem ubuntu@34.243.26.159  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Ireland.pem ubuntu@52.19.102.183  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Ireland.pem ubuntu@54.246.109.50  "cd beacon && python3 main.py realip" &

ssh -i  BeaconTest_Paris.pem ubuntu@13.37.153.19  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Paris.pem ubuntu@13.37.161.173  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Paris.pem ubuntu@13.37.182.131  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Paris.pem ubuntu@15.236.228.24  "cd beacon && python3 main.py realip" &

ssh -i  BeaconTest_Ohio.pem ubuntu@18.222.52.228  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Ohio.pem ubuntu@3.139.154.250  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Ohio.pem ubuntu@3.143.129.24  "cd beacon && python3 main.py realip" &
ssh -i  BeaconTest_Ohio.pem ubuntu@3.20.133.205  "cd beacon && python3 main.py realip" &

wait
echo "finished"
