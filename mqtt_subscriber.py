
import paho.mqtt.client as mqtt             #Needed for mqtt
import datetime                             #Need for timestamps
import mysql.connector                      #Needed to connect to MySQL


MQTT_SERVER = "localhost"                   #MQTT Server (this Raspi)

mydb = mysql.connector.connect(             #MySQL login details
        host="188.**.**.***",
        port="3306",
        user="***063_pi",
        passwd="*********",
        database="***063_test"
)

mycursor = mydb.cursor()

################### Welcome Message ###################
print("-----------------------------------------------------------------")
print("                   Subscriber program started                    ")
print("-----------------------------------------------------------------")

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " +str(rc))

        client.subscribe("tmp_humidity")                                    #Listening to messages on humidity channel
        client.subscribe("tmp_temperature")                                 #Listening to messages on temperature channel

def on_message(client, userdata, msg):

        localtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = datetime.datetime.now().strftime('%Y.%m.%d')                 #Variable for todays date YYYY/MM/DD
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')              #Variable for current time HH:MM:SS
        msg.payload = msg.payload.decode("utf-8")                           #Allows message to contain special characters

        if msg.topic == "tmp_humidity":
                print(msg.payload + "% humidity")

                sql = "INSERT INTO tmp_humidity (bed, date, time, value) VALUES (%s, %s, %s, %s)"   #Tabelname: tmp_humidity; Columns: bed, date, time, value
                val = (int("1"), date, timeNow, msg.payload)                #Date: YYYY/MM/DD
                mycursor.execute(sql, val)
                mydb.commit()                                               #Sends data to Database
                print("humidity commited")

        elif msg.topic == "tmp_temperature":
                print(msg.payload + "°C")

                sql = "INSERT INTO tmp_temperature (bed, date, time, value) VALUES (%s, %s, %s, %s)"   #Tabelname: test; Columns: Date,Time,randNumber
                val = (int("1"), date, timeNow, msg.payload)                #Date: YYYY/MM/DD
                mycursor.execute(sql, val)
                mydb.commit()                                               #Sends data to Database
                print("temperature commited")

        else:
            print("Error, unknown topic: " + msg.topic)                     #Print Error, in case of a message in an unknown channel


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()
