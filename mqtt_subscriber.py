import paho.mqtt.client as mqtt
import datetime
import mysql.connector


MQTT_SERVER = "localhost"               #MQTT Server (this Raspi)
MQTT_PATH = "test_channel"              #MQTT Channel

mydb = mysql.connector.connect(         #MySQL login details
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

def on_message(client, userdata, msg):
        localtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = datetime.datetime.now().strftime('%Y.%m.%d')
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')
        msg.payload = msg.payload.decode("utf-8")

        sql = "INSERT INTO test (Date, Time, randNumber) VALUES (%s, %s, %s)"   #Tabel: test; Columns: Date,Time,randNumber
        val = (date, timeNow, int(msg.payload))       #Date: YYYY/MM/DD
        mycursor.execute(sql, val)
        print("[" + msg.topic + "] " + timeNow +" -  " +  str(msg.payload))

        mydb.commit()
        print("[" + msg.topic + "] " + timeNow +" - " + mycursor.rowcount + "record inserted."  +  str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()
