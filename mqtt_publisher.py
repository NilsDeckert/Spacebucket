#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import Adafruit_DHT
import threading
import time
import datetime
import pw
import sys

MQTT_SERVER = "192.168.178.67"
mydb = pw.login
mycursor = mydb.cursor()
DHTSensor = Adafruit_DHT.DHT11
GPIO.setmode(GPIO.BCM)
channel = 21
GPIO.setup(channel, GPIO.IN)
GPIO_Pin = 23
stopthread = 0

################### Welcome Message ###################
print("-----------------------------------------------------------------")
print("                    Publisher program started                    ")
print("-----------------------------------------------------------------")
print("")

################################################

try:
    mycursor.execute("SELECT * FROM settings")
    records = mycursor.fetchall()

    for row in records:
#       print("Id = ", row[0], )
       print("Name:           ", row[1])
       print("setHumidity:    ", row[5])
       print("setTemperature: ", row[6])
       print("LightFrom:      ", row[3])
       print("LightTo:        ", row[4], "\n")
       setHumidity = row[5]
       setTemperature = row[6]
       LightFrom = row[3]
       LightTo = row[4]
       print("Current time:    " + datetime.datetime.now().strftime('%H:%M:%S'))
except Error as e:
    print ("Error while connecting to MySQL", e)
finally:
    #closing database connection.
    if(mydb.is_connected()):
        mycursor.close()
        print("MySQL connection is closed")
################################################

print("|------------|------------------------|-----------|")

def callback(channel):
    if GPIO.input(channel):
        print("no water detected")
    else:
        print("water detected")

def push():
    try:
        global stopthread
        date = datetime.datetime.now().strftime('%d.%m.%Y')
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')
        Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)
        publish.single("tmp_humidity", Humidity, hostname=MQTT_SERVER)
        print("| {} | humidity sent          |   {}%   |".format(date, Humidity))
        print("|------------|------------------------|-----------|")
        t1 = threading.Timer(900, push, args=[])
        t1.start()
        if stopthread is 1:
    #        _stop_event.set()
            t1.cancel()
            t1.join()
            stopthread = 0
        return
    except (KeyboardInterrupt, SystemExit):
        t1.join()
        exit()
        #cleanup_stop_thread()
        sys.exit()

def push2():
    try:
        global stopthread
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')
        Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)
        publish.single("tmp_temperature", int(Temperature), hostname=MQTT_SERVER)
        print("| {}   | temperature sent       |   {}°C  |".format(timeNow, Temperature))
        t2 = threading.Timer(900, push2, args=[])
        t2.start()
        if stopthread is 1:
    #        _stop_event.set()
            t2.cancel()
            t2.join()
            stopthread = 0
        return
    except (KeyboardInterrupt, SystemExit):
        t2.join()
        exit()
        #cleanup_stop_thread()
        sys.exit()


push()
print(">>> {} Setting up initial time delay".format(datetime.datetime.now().strftime('%H:%M:%S')))
time.sleep(450)
print(">>> Done")
print("|------------|------------------------|-----------|")
push2()
while True:
    try:
        global stopthread
        command = input()
        print("Input: "+ " " + command)
        if command == "force measure":
            print("")
            print("|------------|------------------------|-----------|")
            date = datetime.datetime.now().strftime('%d.%m.%Y')
            timeNow = datetime.datetime.now().strftime('%H:%M:%S')
            Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)
            publish.single("tmp_humidity", Humidity, hostname=MQTT_SERVER)
            print("| {} | humidity sent          |   {}%   |".format(date, Humidity))
            time.sleep(1)
            publish.single("tmp_temperature", int(Temperature), hostname=MQTT_SERVER)
            print("| {}   | temperature sent       |   {}°C  |".format(timeNow, Temperature))
            print("|------------|------------------------|-----------|")

        elif command == "fanspeed":
            fan_speed = input("Fanspeed:")
            if fan_speed:
                print("Fanspeed: " + fan_speed)
                publish.single("fan_speed", int(fan_speed), hostname=MQTT_SERVER)
            #print("|------------|------------------------|-----------|")

        elif command == "help":
            print("Available commands:")
            print("  >force measure")
            print("  >fanspeed")
            print("  >exit")

        elif command == "exit":
            #sys.exit()
            stopthread = 1
            cleanup_stop_thread()
            raise SystemExit(0)
    except:
        exit()
