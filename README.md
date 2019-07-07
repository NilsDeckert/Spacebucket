# Spacebucket

Doing a fully automated spacebucket using a Raspberry Pi 2 and Raspberry Pi Zero W.

Have a look at the [wiki](https://github.com/NilsDeckert/Spacebucket/wiki) for a more detailed insight into the idea

For this project I'm using two Raspberry Pis, a Zero W (publisher) to capture sensor data and to pass it to the Pi 2 (subscriber). The Raspberry Pi 2 then processes the received data, controls fans and light accordingly and uploads the data to a database for later use (e.g. visualizing it in a graph).

![Imgur](https://i.imgur.com/KGCkV81.png)

1. [Introduction](#spacebucket)

2. [Getting started / Setup](#prerequisites--setup)

   - [Publisher](#publisher)
   
     - [Sensor](#temperature-and-humidity-sensor)
     
     - [mqtt](#mqtt)
     
     - [MySQL](#mysql)
  
   - [Subscriber](#subscriber)
   
     - [433MHz Transmitter](#433mhz-transmitter)
     
     - [mqtt](#mqtt)
     
     - [MySQL](#mysql)

   - [Where to put which file](#files-on-the-publisher)

3. [Usage](#usage)

   - [Commands](#commands)

---

# Getting started

**Note: As of right now, the following part is not complete by any means and will be updated every now and then. How ever, I am listing useful ressources I used in the wiki for anyone who wants to try or has a similar project. Cheers!**

## Prerequisites / Setup

---

## Publisher:

#### Temperature and humidity sensor:
The DHT11-sensor uses the **Adafruit_Python_DHT** library. To use it you have to install the python-dev module first:

```shell
sudo apt-get install build-essential python-dev
```
then download the library and install it
```shell
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT/
sudo python setup.py install
```

#### mqtt:
```shell
sudo pip3 install paho-mqtt
```

#### MySQL:
```shell
python3 -m pip install mysql-connector 
```

---

## Subscriber:

#### 433MHz transmitter

To use the 433MHz transmitter install [433Utils by Ninjablocks](https://github.com/ninjablocks/433Utils):
```shell
git clone --recursive https://github.com/ninjablocks/433Utils.git
cd 433Utils/RPi_utils
make all
```
and then compile the outlet.cpp:
```shell
cd ../../
sudo g++ -DRPI /433Utils/rc-switch/RCSwitch.cpp outlet.cpp -o outlet -lwiringPi
```

#### mqtt:
```shell
sudo pip3 install paho-mqtt
```

#### MySQL:
```shell
python3 -m pip install mysql-connector 
```

### Files on the publisher:
* mqtt_publisher.py
* pw.py
### Files on the subscriber:
* mqtt_subscriber.py
* outlet.cpp
* pw.py

### pw.py

Change the `pw.py` on both devices to fit your database

## Usage

If you've set up the software and the hardware correctly, start the software on both devices:

### Subscriber:
```shell
sudo python3 mqtt_subscriber.py
```

### Publisher:

```shell
sudo python3 mqtt_publisher.py
```

With the publisher program running, you can also use commands to interven in the program:
### Commands:
As of right now, there is only one command available

To read the current sensor data and send it to the subscriber, use
```
force measure
```
The cycle in which the software measures the data will not be shifted by this
