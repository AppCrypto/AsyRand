
ssh -i BeaconTest_canada.pem -o ConnectTimeout=3 ubuntu@15.156.141.12 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_canada.pem -o ConnectTimeout=3 ubuntu@3.96.70.23 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_canada.pem -o ConnectTimeout=3 ubuntu@3.98.6.204 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_canada.pem -o ConnectTimeout=3 ubuntu@3.99.17.175 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@122.248.197.195 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@175.41.153.64 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@52.77.191.56 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Singapore.pem -o ConnectTimeout=3 ubuntu@54.255.77.91 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Seoul.pem -o ConnectTimeout=3 ubuntu@13.125.136.55 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Seoul.pem -o ConnectTimeout=3 ubuntu@3.36.157.62 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Seoul.pem -o ConnectTimeout=3 ubuntu@52.79.113.39 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Seoul.pem -o ConnectTimeout=3 ubuntu@54.180.171.139 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_California.pem -o ConnectTimeout=3 ubuntu@13.52.162.138 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_California.pem -o ConnectTimeout=3 ubuntu@52.8.110.149 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_California.pem -o ConnectTimeout=3 ubuntu@52.8.196.35 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_California.pem -o ConnectTimeout=3 ubuntu@54.67.73.60 "cd beacon && sh kill.sh" &

ssh -i BeaconTest_Osaka.pem -o ConnectTimeout=3 ubuntu@13.208.104.15  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Osaka.pem -o ConnectTimeout=3 ubuntu@15.152.238.217  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Osaka.pem -o ConnectTimeout=3 ubuntu@15.168.45.36  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Osaka.pem -o ConnectTimeout=3 ubuntu@15.168.59.238  "cd beacon && sh kill.sh" &

ssh -i BeaconTest_Ireland.pem -o ConnectTimeout=3 ubuntu@18.202.125.41  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Ireland.pem -o ConnectTimeout=3 ubuntu@34.243.26.159  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Ireland.pem -o ConnectTimeout=3 ubuntu@52.19.102.183  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Ireland.pem -o ConnectTimeout=3 ubuntu@54.246.109.50  "cd beacon && sh kill.sh" &

ssh -i BeaconTest_Paris.pem -o ConnectTimeout=3 ubuntu@13.37.153.19  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Paris.pem -o ConnectTimeout=3 ubuntu@13.37.161.173  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Paris.pem -o ConnectTimeout=3 ubuntu@13.37.182.131  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Paris.pem -o ConnectTimeout=3 ubuntu@15.236.228.24  "cd beacon && sh kill.sh" &

ssh -i BeaconTest_Ohio.pem -o ConnectTimeout=3 ubuntu@18.222.52.228  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Ohio.pem -o ConnectTimeout=3 ubuntu@3.139.154.250  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Ohio.pem -o ConnectTimeout=3 ubuntu@3.143.129.24  "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Ohio.pem -o ConnectTimeout=3 ubuntu@3.20.133.205  "cd beacon && sh kill.sh" &

ssh -i BeaconTest_Mumbai.pem -o ConnectTimeout=3 ubuntu@13.200.53.130 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Mumbai.pem -o ConnectTimeout=3 ubuntu@13.234.100.134 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Mumbai.pem -o ConnectTimeout=3 ubuntu@3.111.202.217 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Mumbai.pem -o ConnectTimeout=3 ubuntu@65.2.154.26 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Frankfurt.pem -o ConnectTimeout=3 ubuntu@18.156.184.202 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Frankfurt.pem -o ConnectTimeout=3 ubuntu@3.77.89.37 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Frankfurt.pem -o ConnectTimeout=3 ubuntu@35.156.113.255 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Frankfurt.pem -o ConnectTimeout=3 ubuntu@52.28.214.81 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Sydney.pem -o ConnectTimeout=3 ubuntu@3.106.173.166 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Sydney.pem -o ConnectTimeout=3 ubuntu@52.63.29.90 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Sydney.pem -o ConnectTimeout=3 ubuntu@54.252.72.184 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_Sydney.pem -o ConnectTimeout=3 ubuntu@54.79.26.185 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_SaoPaulo.pem -o ConnectTimeout=3 ubuntu@52.67.111.172 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_SaoPaulo.pem -o ConnectTimeout=3 ubuntu@52.67.198.168 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_SaoPaulo.pem -o ConnectTimeout=3 ubuntu@54.94.189.238 "cd beacon && sh kill.sh" &
ssh -i BeaconTest_SaoPaulo.pem -o ConnectTimeout=3 ubuntu@54.94.202.91 "cd beacon && sh kill.sh" &

wait
echo "finished"