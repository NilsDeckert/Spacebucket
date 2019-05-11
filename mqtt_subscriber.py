
import paho.mqtt.client as mqtt             #Needed for mqtt
import datetime                             #Need for timestamps
import pw                                   #Imports login credentials from pw.py, inlcudes mysql.connector


MQTT_SERVER = "localhost"                   #MQTT Server (this Raspi)

mydb = pw.login                             #MySQL login details

mycursor = mydb.cursor()

################### Welcome Message ###################
print("-----------------------------------------------------------------")
print("                   Subscriber program started                    ")
print("-----------------------------------------------------------------")
print("")

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " +str(rc))
        prin("")
        client.subscribe("tmp_humidity")                                    #Listening to messages on humidity channel
        client.subscribe("tmp_temperature")                                 #Listening to messages on temperature channel

def on_message(client, userdata, msg):

        localtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = datetime.datetime.now().strftime('%Y.%m.%d')                 #Variable for todays date YYYY/MM/DD
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')              #Variable for current time HH:MM:SS
        msg.payload = msg.payload.decode("utf-8")                           #Allows message to contain special characters
        payload = msg.payload

        if msg.topic == "tmp_humidity":
                print("|------------|------------------------|-----------|")
                print("| {} | humidity               |   {}%   |".format(date, payload))

                sql = "INSERT INTO tmp_humidity (bed, date, time, value) VALUES (%s, %s, %s, %s)"   #Tabelname: tmp_humidity; Columns: bed, date, time, value
                val = (int("1"), date, timeNow, msg.payload)                #Date: YYYY/MM/DD
                mycursor.execute(sql, val)
                mydb.commit()                                               #Sends data to Database
                print("| {}   | committed              |           |".format(timeNow))
                print("|------------|------------------------|-----------|")

        elif msg.topic == "tmp_temperature":
                print("| {} | temperature            |   {}C   |".format(date, payload))

                sql = "INSERT INTO tmp_temperature (bed, date, time, value) VALUES (%s, %s, %s, %s)"   #Tabelname: test; Columns: Date,Time,randNumber
                val = (int("1"), date, timeNow, msg.payload)                #Date: YYYY/MM/DD
                mycursor.execute(sql, val)
                mydb.commit()                                               #Sends data to Database
                print("| {}   | commited               |           |".format(timeNow))
                print("|------------|------------------------|-----------|")
                print("")

        else:
            print("Error, unknown topic: " + msg.topic)                     #Print Error, in case of a message in an unknown channel


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()
