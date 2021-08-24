import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import datetime
import urllib.request
import random
import spidev

GPIO.setwarnings(False)

sensor = Adafruit_DHT.DHT11
pin = 4

GPIO.setmode(GPIO.BCM)
spi=spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=50000

def read_spi_adc(adcChannel):
    adcValue=0
    buff=spi.xfer2([1,(8+adcChannel)<<4,0])
    adcValue = ((1023-(((buff[1]&3)<<8)+buff[2]))*2/1023)*100

    return adcValue

try:

    while True:
        wtime = datetime.datetime.now()
        h, temp = Adafruit_DHT.read_retry(sensor, pin)

        if h is not None and temp is not None:
            print(wtime, 'Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temp, h))

            adcValue=read_spi_adc(0)
            print("Land Moisture Sensor : %d" %(adcValue))

            Rain = read_spi_adc(1)
            print("Rain : %d" %(Rain))
            
            CO2 = read_spi_adc(2)
            print("CO2 : %d" %(CO2))

            time.sleep(15)

            html = urllib.request.urlopen("https://api.thingspeak.com/update?api_key=CDTO9BJPFL0K7UFI&field1="+str(temp)+"&field2="+str(h)+"&field3="+str(adcValue))
            html = urllib.request.urlopen("https://api.thingspeak.com/update?api_key=F2JSG6MGWLX2GPNJ&field1="+str(CO2)+"&field2="+str(Rain))

        else:
            print('Failed to get reading. Try again!')



except KeyboardInterrupt:
    pass
GPIO.cleanup()