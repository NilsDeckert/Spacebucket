#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import wiringpi
import atexit
import sys
import time
import datetime
import smtplib, ssl
import pw
import emailinfo
import temphumidity
from subprocess import call

MQTT_SERVER = "localhost"               #MQTT Server (this Raspi)
mydb = pw.login
timeNow = datetime.datetime.now().strftime('%H:%M:%S')

wiringpi.wiringPiSetupGpio()                # Initialise wiringpi GPIO
wiringpi.pinMode(18,2)                      # Set up GPIO 18 to PWM mode
wiringpi.pwmWrite(18,0)                     # set pwm to zero initially
fanspeed = 250
light = 0
newday = 0
failedHumidity = 0
failedTemperature = 0
global failedHumidity
global failedTemperature
global light
global LightOn
global LightOff
################### Welcome Message ###################
print("-----------------------------------------------------------------")
print("                   Subscriber program started                    ")
print("-----------------------------------------------------------------" + "\n")
################################################
def fetchall():
    global midnight
    global LightFrom
    global LightTo
    global LightOn
    global LightOff
    global mycursor
    global setTemperature
    try:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM settings")
        records = mycursor.fetchall()

    #    print("Total number of rows in settings is - ", mycursor.rowcount)

        for row in records:
    #       print("Id = ", row[0], )
           print("Name:           ", row[1])
           print("setHumidity:    ", row[5])
           print("setTemperature: ", row[6])
           print("LightFrom:      ", row[3])
           print("LightTo:        ", row[4], "\n")
           setHumidity = row[5]
           setTemperature = row[6]
           LightOn = row[3]
           LightOff = row[4]
#    mycursor.close()

    except Error as e:
        print ("Error while connecting to MySQL", e)

    midnight = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(0, 0))
    LightFrom = LightOn + midnight
    LightTo = LightOff + midnight

fetchall()

now = datetime.datetime.now()
print("Current time:    " + timeNow + "\n")

def LightOnOff():
    global light
    global midnight
    global LightFrom
    global LightTo
    if LightFrom < now < LightTo:
        call(["./outlet", "1"])
        print(">>> " + "Turning light ON! (1/2)")
        light = 1
    else:
        call(["./outlet", "2"])
        print(">>> " + "Turning light OFF! (1/2)")
        light = 0
    time.sleep(5)
    if LightFrom < now < LightTo:
        call(["./outlet", "1"])
        print(">>> " + "Turning light ON! (2/2)")
        light = 1
    else:
        call(["./outlet", "2"])
        print(">>> " + "Turning light OFF! (2/2)")
        light = 0

def LightSchedule():
    try:
        LightOnOff()
    except:
        call(["./outlet", "2"])
        print("Error in LightSchedule()")
        exit()

def reset_ports():                          # resets the ports for a safe exit
    wiringpi.pwmWrite(18,0)                 # set pwm to zero
    wiringpi.digitalWrite(18, 0)            # ports 17 & 18 off
    wiringpi.pinMode(18,0)

def TurnOnFans():
    try:
        wiringpi.pwmWrite(18,fanspeed)
        print(">>> " + "Turning fans ON")
    except:
        reset_ports()

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " +str(rc))
        print("")
        client.subscribe("tmp_humidity")
        client.subscribe("tmp_temperature")
        client.subscribe("set_humidity")
        client.subscribe("set_temperature")
        client.subscribe("fan_speed")

def quit():
    print("")
    client.loop_stop()
    call(["./outlet", "2"])
    print(">>> " + "Turning light OFF! (1/2)")
    time.sleep(3)
    call(["./outlet", "2"])
    print(">>> " + "Turning light OFF! (2/2)")
    reset_ports()
    print(">>> " + "Turning fans OFF" + "\n")
    print("-----------------------------------------------------------------")
    print("                   Subscriber program stopped                    ")
    print("-----------------------------------------------------------------" + "\n")

TurnOnFans()
LightSchedule()

#while True:
def on_message(client, userdata, msg):
    global fanspeed
    global setTemperature
    global now
    global light
    global LightOn
    global LightOff
    global failedHumidity
    global failedTemperature

    localtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date = datetime.datetime.now().strftime('%d.%m.%Y')
    timeNow = datetime.datetime.now().strftime('%H:%M:%S')
    msg.payload = msg.payload.decode("utf-8")
    payload = msg.payload

    midnight = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(0, 0))
    LightFrom = LightOn + midnight
    LightTo = LightOff + midnight

    if msg.topic == "tmp_humidity":
        temphumidity.humidity = payload
        print("|------------|------------------------|-----------|")
        print("| {} | humidity               |   {}%   |".format(date, payload))
        try:
            sql = "INSERT INTO tmp_humidity (bed, date, time, value) VALUES (%s, %s, %s, %s)"   #Tabelname: tmp_humidity; Columns: bed, date, time, value
            val = (int("1"), date, timeNow, payload) #Date: YYYY/MM/DD
            mycursor.execute(sql, val)
            mydb.commit()
            print("| {}   | committed              |           |".format(timeNow))
            failedHumidity = 0

        except:
            print("| {}   | Error commiting to database        |".format(timeNow))
            if failedHumidity == 20:
                message = """\

                Subject: ERROR


                {}
                {}

                The system has a problem commiting data to the database, check output and consider restarting the script

                Affected data: humdity
                Failed Attempts in a row: 20

                Temperature: {}C
                Humidity: {}%
                Fanspeed: {}/1000""".format(date, timeNow, temphumidity.temperature, temphumidity.humidity, fanspeed)

                context = ssl.create_default_context()

                with smtplib.SMTP(emailinfo.smtp_server, emailinfo.port) as server:
                    server.starttls(context=context)
                    server.login(emailinfo.sender_email, emailinfo.password)
                    server.sendmail(emailinfo.sender_email, emailinfo.receiver_email, message)
                failedHumidity = 0
        print("|------------|------------------------|-----------|")
    elif msg.topic == "tmp_temperature":
        temphumidity.temperature = payload
        print("| {} | temperature            |   {}°C    |".format(date, payload))
        try:
            sql = "INSERT INTO tmp_temperature (bed, date, time, value) VALUES (%s, %s, %s, %s)"   #Tabelname: tmp_temperature; Columns: bed, date, time, value
            val = (int("1"), date, timeNow, msg.payload) #Date: YYYY/MM/DD
            mycursor.execute(sql, val)
            mydb.commit()
            print("| {}   | commited               |           |".format(timeNow))
            failedTemperature = 0
        except:
            print("| {}   | Error commiting to database        |".format(timeNow))
            if failedTemperature == 20:
                message = """\

                Subject: ERROR


                {}
                {}

                The system has a problem commiting data to the database, check output and consider restarting the script

                Affected data: temperature
                Failed Attempts in a row: 20

                Temperature: {}C
                Humidity: {}%
                Fanspeed: {}/1000""".format(date, timeNow, temphumidity.temperature, temphumidity.humidity, fanspeed)

                context = ssl.create_default_context()

                with smtplib.SMTP(emailinfo.smtp_server, emailinfo.port) as server:
                    server.starttls(context=context)
                    server.login(emailinfo.sender_email, emailinfo.password)
                    server.sendmail(emailinfo.sender_email, emailinfo.receiver_email, message)
                failedTemperature = 0

        if int(payload) > int(setTemperature) and fanspeed <= 975:
            difference1 = int(payload) - int(setTemperature)
            fanspeed += 50 * difference1
            if fanspeed > 1000:
                fanspeed = 1000
            wiringpi.pwmWrite(18,fanspeed)
            print("|------------|------------------------|-----------|")
            print(">>> fanspeed increased ({})".format(fanspeed))
        elif int(payload) < int(setTemperature) and fanspeed >= 250:
            fanspeed -= 50 * int(setTemperature) - int(payload)
            if fanspeed < 150:
                fanspeed = 150
            wiringpi.pwmWrite(18,fanspeed)
            print("|------------|------------------------|-----------|")
            print(">>> fanspeed decreased ({})".format(fanspeed))
        else:
            print("|------------|------------------------|-----------|")
        print("")
    elif msg.topic == "fan_speed":
        fanspeed = int(msg.payload)
        if fanspeed > 1000:
            fanspeed = 1000
        elif fanspeed < 150:
            fanspeed = 150
        wiringpi.pwmWrite(18,fanspeed)
        print(">>> fanspeed manually adjusted ({})".format(fanspeed))

    else:
        print("Error, unknown topic: " + msg.topic)

    now = datetime.datetime.now()

    if light == 0 and LightFrom < now < LightTo:
        call(["./outlet", "1"])
        print(">>> " + "Turning light ON!")
        light = 1
        message = """\
        Subject: Spacebucket Light on\n\n

        {}
        {}

        Temperature: {}C
        Humidity: {}%
        Fanspeed: {}/1000""".format(date, timeNow, temphumidity.temperature, temphumidity.humidity, fanspeed)

        context = ssl.create_default_context()

        with smtplib.SMTP(emailinfo.smtp_server, emailinfo.port) as server:
            server.starttls(context=context)
            server.login(emailinfo.sender_email, emailinfo.password)
            server.sendmail(emailinfo.sender_email, emailinfo.receiver_email, message)
        print("Email sent")
        newday = 0

    elif light == 1 and now > LightTo > LightFrom or light == 1 and LightFrom > LightTo > now:
        call(["./outlet", "2"])
        print(">>> " + "Turning light OFF!")
        light = 0
        message = """\
        Subject: Spacebucket Light off\n\n

        {}
        {}

        Temperature: {}C
        Humidity: {}%
        Fanspeed: {}/1000""".format(date, timeNow, temphumidity.temperature, temphumidity.humidity, fanspeed)

        context = ssl.create_default_context()

        with smtplib.SMTP(emailinfo.smtp_server, emailinfo.port) as server:
            server.starttls(context=context)
            server.login(emailinfo.sender_email, emailinfo.password)
            server.sendmail(emailinfo.sender_email, emailinfo.receiver_email, message)
        print("Email sent")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
atexit.register(quit)
try:
    client.loop_forever()
except:
    client.loop_stop()
