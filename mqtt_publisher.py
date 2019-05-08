import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import datetime

MQTT_SERVER = "192.168.178.66"                                                          #IP of the receiving Raspberry Pi
DHTSensor = Adafruit_DHT.DHT11                                                          #Sensor
GPIO_Pin = 23                                                                           #GPIO Pin the sensor is connected to

print("-----------------------------------------------------------------")
print("                    Publisher program started                    ")
print("-----------------------------------------------------------------")
print("")
print("|------------|------------------------|-----------|")

try:
    while True:
        date = datetime.datetime.now().strftime('%d.%m.%Y')
        timeNow = datetime.datetime.now().strftime('%H:%M:%S')
        Humidity, Temperature = Adafruit_DHT.read_retry(DHTSensor, GPIO_Pin)        #Defining 'Humidity' and 'Temperature' as the output of the sensor

        if Humidity is not None and Temperature is not None:                        #Making sure the sensor has proper output

            publish.single("tmp_humidity", Humidity, hostname=MQTT_SERVER)
            print("| {} | humidity sent          |  ({})%  |").format(date, Humidity)
            time.sleep(1)                                                           #Wait 1s just to make sure everything gets processed properly
            publish.single("tmp_temperature", Temperature, hostname=MQTT_SERVER)
            print("| {}   | temperature sent       |  ({})C  |").format(timeNow, Temperature)
            time.sleep(29)                                                          #Wait 29s (30 in total) until the next loop

        else:
            print("Error")

except KeyboardInterrupt:                                                           #On Ctrl + C:
    exit()                                                                          #Program quits
    GPIO.cleanup()                                                                  #GPIO pins get 'cleaned up'
