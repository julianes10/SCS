#Pre-requisite
PATH="$PATH:/usr/bin:/usr/local/bin:/usr/sbin:/usr/local/sbin:/bin:/sbin"

NAME="noip2"

mkdir /home/pi/noip
cd /home/pi/noip
wget http://www.no-ip.com/client/linux/noip-duc-linux.tar.gz
tar vzxf noip-duc-linux.tar.gz
cd noip-2.1.9-1
sudo make
sudo make install
#sudo /usr/local/bin/noip2
#sudo noip2 ­-S (Capital “S”)

cp -rf "$NAME.service" /lib/systemd/system/

chmod 644 /lib/systemd/system/"$NAME.service" 
systemctl enable "$NAME.service"
systemctl start  "$NAME.service"
systemctl status "$NAME.service"

