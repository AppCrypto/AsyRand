
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@3.0.95.226 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@54.255.165.42 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@13.250.25.126 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@47.129.8.21 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@54.255.163.212 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@13.215.253.19 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@52.77.239.135 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@18.139.3.48 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@18.140.65.62 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@47.129.42.248 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@54.169.169.121 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@47.128.249.151 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@13.212.247.219 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@13.213.58.191 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@13.250.122.97 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@13.229.232.108 "cd beacon && sh kill.sh" &

# ssh -i BeaconTest_Osaka.pem -o ConnectTimeout=3 ubuntu@54.255.163.212  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Osaka.pem -o ConnectTimeout=3 ubuntu@15.152.238.217  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Osaka.pem -o ConnectTimeout=3 ubuntu@15.168.45.36  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Osaka.pem -o ConnectTimeout=3 ubuntu@15.168.59.238  "cd beacon && sh kill.sh" &

# ssh -i BeaconTest_Ireland.pem -o ConnectTimeout=3 ubuntu@18.202.125.41  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Ireland.pem -o ConnectTimeout=3 ubuntu@34.243.26.159  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Ireland.pem -o ConnectTimeout=3 ubuntu@52.19.102.183  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Ireland.pem -o ConnectTimeout=3 ubuntu@54.246.109.50  "cd beacon && sh kill.sh" &

# ssh -i BeaconTest_Paris.pem -o ConnectTimeout=3 ubuntu@13.37.153.19  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Paris.pem -o ConnectTimeout=3 ubuntu@13.37.161.173  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Paris.pem -o ConnectTimeout=3 ubuntu@13.37.182.131  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Paris.pem -o ConnectTimeout=3 ubuntu@15.236.228.24  "cd beacon && sh kill.sh" &

# ssh -i BeaconTest_Ohio.pem -o ConnectTimeout=3 ubuntu@18.222.52.228  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Ohio.pem -o ConnectTimeout=3 ubuntu@3.139.154.250  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Ohio.pem -o ConnectTimeout=3 ubuntu@3.143.129.24  "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Ohio.pem -o ConnectTimeout=3 ubuntu@3.20.133.205  "cd beacon && sh kill.sh" &

# ssh -i BeaconTest_Mumbai.pem -o ConnectTimeout=3 ubuntu@13.200.53.130 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Mumbai.pem -o ConnectTimeout=3 ubuntu@13.234.100.134 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Mumbai.pem -o ConnectTimeout=3 ubuntu@3.111.202.217 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Mumbai.pem -o ConnectTimeout=3 ubuntu@65.2.154.26 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Frankfurt.pem -o ConnectTimeout=3 ubuntu@18.156.184.202 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Frankfurt.pem -o ConnectTimeout=3 ubuntu@3.77.89.37 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Frankfurt.pem -o ConnectTimeout=3 ubuntu@35.156.113.255 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Frankfurt.pem -o ConnectTimeout=3 ubuntu@52.28.214.81 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Sydney.pem -o ConnectTimeout=3 ubuntu@3.106.173.166 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Sydney.pem -o ConnectTimeout=3 ubuntu@52.63.29.90 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Sydney.pem -o ConnectTimeout=3 ubuntu@54.252.72.184 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_Sydney.pem -o ConnectTimeout=3 ubuntu@54.79.26.185 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_SaoPaulo.pem -o ConnectTimeout=3 ubuntu@52.67.111.172 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_SaoPaulo.pem -o ConnectTimeout=3 ubuntu@52.67.198.168 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_SaoPaulo.pem -o ConnectTimeout=3 ubuntu@54.94.189.238 "cd beacon && sh kill.sh" &
# ssh -i BeaconTest_SaoPaulo.pem -o ConnectTimeout=3 ubuntu@54.94.202.91 "cd beacon && sh kill.sh" &

wait
echo "finished"