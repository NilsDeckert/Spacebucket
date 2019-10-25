#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import Adafruit_DHT
import argparse
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
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO_Pin = 23
stopthread = 0

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="Toggle debug output and additional commands", action="store_true")
args = parser.parse_args()
debug = args.debug

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
##Soil sensor
def callback(channel):
    if GPIO.input(channel):
        print("no water detected")
        publish.single("tmp_soil", "no water", hostname=MQTT_SERVER)
        print("message sent")
    else:
        publish.single("tmp_soil", "water", hostname=MQTT_SERVER)
        print("water detected")

GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)

##Water sensor
def button_callback(channel1):
    print("Button pressed!")

GPIO.add_event_detect(10, GPIO.RISING)
GPIO.add_event_callback(10, button_callback)

push()
print(">>> {} Setting up initial time delay".format(datetime.datetime.now().strftime('%H:%M:%S')))
time.sleep(15) #450
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
            try:
                fan_speed = int(fan_speed) #Make sure input is a number
                if fan_speed:              #Check if user gave input or just hit enter to skip
                    print("Fanspeed: " + str(fan_speed))
                    publish.single("fan_speed", fan_speed, hostname=MQTT_SERVER)
            except ValueError:
                if fan_speed:
                    print("Input has to be a number")
            #print("|------------|------------------------|-----------|")

        elif command == "light on":
            publish.single("msg_light", "on", hostname=MQTT_SERVER)
            print("Turning on light...")
        elif command == "light off":
            publish.single("msg_light", "off", hostname=MQTT_SERVER)
            print("Turning off light...")

        elif command == "simulate temperature" and debug: #Only allow command if script is started in debugmode
            sim_temperature = input("Temperature:")
            try:
                sim_temperature = int(sim_temperature) #Make sure input is a number
                if sim_temperature:                    #Check if user gave input or just hit enter to skip
                    print("Simulating Temperature: " + sim_temperature + "C")
                    publish.single("tmp_temperature", sim_temperature, hostname=MQTT_SERVER)
            except ValueError:
                if sim_temperature:
                    print("Input has to be a number")

        elif command == "simulate humidity" and debug: #Only allow command if script is started in debugmode
            sim_humidity = input("Humidity:")
            try:
                sim_humidity = int(sim_humidity) #Make sure input is a number
                if sim_humidity:                    #Check if user gave input or just hit enter to skip
                    print("Simulating Humidity: " + sim_humidity + "%")
                    publish.single("tmp_humidity", sim_humidity, hostname=MQTT_SERVER)
            except ValueError:
                if sim_humidity:
                    print("Input has to be a number")

        elif command == "help":
            print("Available commands:")
            print("  >fanspeed")
            print("  >force measure")
            print("  >light on")
            print("  >light off")
            if debug:
                print("simulate temperature")
                print("simulate humidty")
            print("  >exit")

        elif command == "exit":
            #sys.exit()
            stopthread = 1
            cleanup_stop_thread()
            raise SystemExit(0)
    except:
        exit()
