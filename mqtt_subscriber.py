import paho.mqtt.client as mqtt                                                 #Needed for mqtt
import datetime                                                                 #Need for timestamps
import mysql.connector                                                          #Needed to connect to MySQL


MQTT_SERVER = "localhost"                                                       #MQTT Server (this Raspi)
MQTT_PATH = "test_channel"                                                      #MQTT Channel

mydb = mysql.connector.connect(                                                 #MySQL login details
        host="188.**.**.***",
        port="3306",
        user="***063_pi",
        passwd="******",
        database="***063_test"
)

mycursor = mydb.cursor()

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " +str(rc))

        client.subscribe(MQTT_PATH)

def on_message(client, userdata, msg):  #Triggers whenever a new message is being received
        localtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = datetime.datetime.now().strftime('%Y.%m.%d')                     #Variable for todays date YYYY/MM/DD
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')                  #Variable for current time HH:MM:SS
        msg.payload = msg.payload.decode("utf-8")                               #Allows message to contain special characters

        sql = "INSERT INTO test (Date, Time, randNumber) VALUES (%s, %s, %s)"   #Tabelname: test; Columns: Date,Time,randNumber
        val = (date, timeNow, int(msg.payload))                                 #Date: YYYY/MM/DD
        mycursor.execute(sql, val)
        print("[" + msg.topic + "] " + timeNow +" -  " +  str(msg.payload))     #Prints Channel, Date+Time, Message into console

        mydb.commit()                                                           #Sends data to Database
        print("[" + msg.topic + "] " + timeNow +" - " + mycursor.rowcount + "record inserted."  +  str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()                                                           #Program keeps waiting for messages
