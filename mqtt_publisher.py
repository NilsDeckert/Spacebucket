# -*- coding: utf-8 -*-
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import Adafruit_DHT
import threading
import time
import datetime
import pw                                                                       # Imports login credentials from pw.py, inlcudes mysql.connector
import sys

MQTT_SERVER = "192.168.178.67"                                                  # IP of the receiving Raspberry Pi (subscriber)
mydb = pw.login                                                                 # MySQL login credentials
mycursor = mydb.cursor()
DHTSensor = Adafruit_DHT.DHT11
GPIO_Pin = 23                                                                   # GPIO Pin the sensor is connected to
stopthread = 0

################### Welcome Message ###################
print("-----------------------------------------------------------------")
print("                    Publisher program started                    ")
print("-----------------------------------------------------------------")
print("")
#######################################################
########### Getting settings from database ############
#######################################################
try:
    mycursor.execute("SELECT * FROM settings")
    records = mycursor.fetchall()

    for row in records:
       print("Name:           ", row[1])
       print("setHumidity:    ", row[5])
       print("setTemperature: ", row[6])
       print("LightFrom:      ", row[3])
       print("LightTo:        ", row[4], "\n")
       setHumidity = row[5]                                                     # Defining variables for later use
       setTemperature = row[6]
       LightFrom = row[3]
       LightTo = row[4]

except Error as e:
    print ("Error while connecting to MySQL", e)
finally:
    if(mydb.is_connected()):
        mycursor.close()                                                        # Closing connection to database
        print("MySQL connection is closed")
################################################

print("|------------|------------------------|-----------|")

def push():
    try:
        global stopthread
        date = datetime.datetime.now().strftime('%d.%m.%Y')
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')
        Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)    # Defining 'Humidity' and 'Temperature' as the output of the sensor
        publish.single("tmp_humidity", Humidity, hostname=MQTT_SERVER)          # Sending sensor information to subscriber
        print("| {} | humidity sent          |   {}%   |".format(date, Humidity))
        time.sleep(1)
        publish.single("tmp_temperature", Temperature, hostname=MQTT_SERVER)    # Sending sensor information to subscriber
        print("| {}   | temperature sent       |   {}°C  |".format(timeNow, Temperature))
        print("|------------|------------------------|-----------|")
        t1 = threading.Timer(29, push, args=[])                                 # Restarting after 29 seconds
        t1.start()                                                              # Start threading
        if stopthread is 1:
            t1.cancel()
            t1.join()
            stopthread = 0
        return
    except (KeyboardInterrupt, SystemExit):
        t1.join()
        exit()
        sys.exit()


push()

#######################################################
############ Implementing a command line ##############
#######################################################

while True:
    try:
        global stopthread
        command = input()
        print("Input: "+ " " + command)
        print("")
        print("|------------|------------------------|-----------|")
        if command == "force measure":                                          # Command "force measure" -> measuring outside of usual cycle
            date = datetime.datetime.now().strftime('%d.%m.%Y')
            timeNow = datetime.datetime.now().strftime('%H:%M:%S')
            Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)
            publish.single("tmp_humidity", Humidity, hostname=MQTT_SERVER)
            print("| {} | humidity sent          |   {}%   |".format(date, Humidity))
            time.sleep(1)
            publish.single("tmp_temperature", Temperature, hostname=MQTT_SERVER)
            print("| {}   | temperature sent       |   {}°C  |".format(timeNow, Temperature))
            print("|------------|------------------------|-----------|")
        elif command == "exit":
            stopthread = 1
            cleanup_stop_thread()
            raise SystemExit(0)
    except:
        exit()
