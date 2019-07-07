# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import wiringpi
import sys
import time
import datetime
import pw                                   # Imports login credentials from pw.py, inlcudes mysql.connector
from subprocess import call

MQTT_SERVER = "localhost"                   # MQTT Server (this Raspi)
mydb = pw.login                             # MySQL login credentials
timeNow = datetime.datetime.now().strftime('%H:%M:%S')

wiringpi.wiringPiSetupGpio()                # Initialise wiringpi GPIO
wiringpi.pinMode(18,2)                      # Set up GPIO 18 to PWM mode
wiringpi.pwmWrite(18,0)                     # set pwm to zero initially

mycursor = mydb.cursor()

################### Welcome Message ###################
print("-----------------------------------------------------------------")
print("                   Subscriber program started                    ")
print("-----------------------------------------------------------------")
print("")
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
       # Assigning settings to variables for later use
       setHumidity = row[5]
       setTemperature = row[6]
       LightFrom = row[3]
       LightTo = row[4]

except Error as e:
    print ("Error while connecting to MySQL", e)

# Comparing current time with settings for light schedule
# Turning light on/off accordingly
midnight = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(0, 0))
LightFrom = LightFrom + midnight
LightTo = LightTo + midnight
now = datetime.datetime.now()

print("Current time:    " + timeNow + "\n")

def LightOnOff():
    if LightFrom < now < LightTo:
        call(["./outlet", "1"])             # Executing 'outlet' w/ argument '1' -> turning on remote outlet
        print(">>> " + "Turning light ON! (1/2)")
    else:
        call(["./outlet", "2"])
        print(">>> " + "Turning light OFF! (1/2)")
    time.sleep(5)
    if LightFrom < now < LightTo:
        call(["./outlet", "1"])
        print(">>> " + "Turning light ON! (2/2)")
    else:
        call(["./outlet", "2"])
        print(">>> " + "Turning light OFF! (2/2)")

def LightSchedule():
    try:
        LightOnOff()
    except:
        call(["./steuerung", "2"])
        print("Error in LightSchedule()")
        exit()

def reset_ports():                          # Resets the ports for a safe exit
    wiringpi.pwmWrite(18,0)                 # Set pwm to zero
    wiringpi.digitalWrite(18, 0)            # Port 18 off
    wiringpi.pinMode(18,0)

def TurnOnFans():
    try:
        wiringpi.pwmWrite(18,250)           # Setting pwm to 250 -> fan spinning slowly
        print(">>> " + "Turning fans ON")
    except:
        reset_ports()

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " +str(rc))
        print("")
        client.subscribe("tmp_humidity")    # Listening to messages on humidity channel
        client.subscribe("tmp_temperature") # Listening to messages on temperature channel

def on_message(client, userdata, msg):

    localtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date = datetime.datetime.now().strftime('%Y.%m.%d')
    msg.payload = msg.payload.decode("utf-8")
    payload = msg.payload

    if msg.topic == "tmp_humidity":
            print("|------------|------------------------|-----------|")
            print("| {} | humidity               |   {}%   |".format(date, payload))
            # Table: tmp_humidity; Columns: bed, date, time, value
            sql = "INSERT INTO tmp_humidity (bed, date, time, value) VALUES (%s, %s, %s, %s)"
            val = (int("1"), date, timeNow, payload)
            mycursor.execute(sql, val)
            mydb.commit()                   # Sending data to database
            print("| {}   | committed              |           |".format(timeNow))
            print("|------------|------------------------|-----------|")

    elif msg.topic == "tmp_temperature":
            print("| {} | temperature            |   {}°C  |".format(date, payload))
            # Table: tmp_temperature; Columns: bed, date, time, value
            sql = "INSERT INTO tmp_temperature (bed, date, time, value) VALUES (%s, %s, %s, %s)"
            val = (int("1"), date, timeNow, msg.payload)
            mycursor.execute(sql, val)
            mydb.commit()                   # Sending data to database
            print("| {}   | commited               |           |".format(timeNow))
            print("|------------|------------------------|-----------|")
            print("")

    else:
        # Print Error in case of a message in an unknown channel
        print("Error, unknown topic: " + msg.topic)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
TurnOnFans()
LightSchedule()
client.loop_forever()
