rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@3.0.95.226:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@54.255.165.42:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@13.250.25.126:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@47.129.8.21:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@54.255.163.212:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@13.215.253.19:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@52.77.239.135:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@18.139.3.48:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@18.140.65.62:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@47.129.42.248:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@54.169.169.121:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@47.128.249.151:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@13.212.247.219:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@13.213.58.191:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@13.250.122.97:~/beacon/ &
rsync -avz -e "ssh -i BeaconTest_Singapore.pem" ./ ubuntu@13.229.232.108:~/beacon/ &

wait

echo "finished"
