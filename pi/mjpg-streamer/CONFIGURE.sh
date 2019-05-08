## Thanks to 
#### https://community.octoprint.org/t/setting-up-octoprint-on-a-raspberry-pi-running-raspbian/2337
#### https://github.com/jacksonliam/mjpg-streamer

git clone https://github.com/jacksonliam/mjpg-streamer.git
sudo apt-get update
sudo apt-get install cmake libjpeg8-dev
sudo apt-get install gcc g++
cd mjpg-streamer-experimental
make
sudo make install

