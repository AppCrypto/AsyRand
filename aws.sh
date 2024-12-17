sudo apt-get update
echo y | sudo apt-get install gcc
echo y |sudo apt-get install make
echo y |sudo apt-get install perl
echo y |sudo apt-get install m4 flex bison
echo y |sudo apt-get install python3-setuptools python3-dev libssl-dev
echo y |sudo apt-get install python3-pip
pip3 install pyparsing==2.4.6
pip3 install hypothesis



wget https://gmplib.org/download/gmp/gmp-5.1.3.tar.xz
tar -xvf gmp-5.1.3.tar.xz
sudo mv gmp-5.1.3 /usr/local/src/
cd /usr/local/src/gmp-5.1.3
sudo ./configure
sudo make
sudo make install

cd /home/ubuntu
wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
tar -xvf pbc-0.5.14.tar.gz
sudo mv pbc-0.5.14 /usr/local/src/
cd /usr/local/src/pbc-0.5.14
sudo ./configure
sudo make
sudo make install

sudo touch /etc/ld.so.conf.d/libpbc.conf
sudo echo "/usr/local/lib" | sudo tee /etc/ld.so.conf.d/libpbc.conf
sudo ldconfig

cd /home/ubuntu
echo y | sudo apt-get install git
echo y | sudo apt-get install vim
git clone https://gitclone.com/github.com/JHUISI/charm.git
sudo mv charm /usr/local/src/
cd /usr/local/src/charm
sudo sed -i '230s/  alpha|cris|ia64|lm32|m68k|microblaze|ppc|ppc64|sparc64|unicore32|armv6l|armv7l|s390|s390x)/  aarch64|alpha|cris)/' configure.sh

sudo ./configure.sh
sudo make
sudo make install
python3
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group2 = PairingGroup('SS512')
g = group2.random(G1)
g