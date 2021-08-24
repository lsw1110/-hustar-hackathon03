import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import datetime
import urllib.request
import random
import spidev

import pygame

pygame.mixer.init()

GPIO.setwarnings(False)

sensor = Adafruit_DHT.DHT11
pin = 4

GPIO.setmode(GPIO.BCM)
spi=spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=50000

Pump1_1 = 20
Pump1_2 = 21
Fan = 16
LED_R = 5
LED_B = 6
LED_G = 13
SW_01 = 19 # 수동 팬 가동
SW_02 = 26 # 수동 펌프 가
SW_03 = 17 #비상 스위치

HT_01 = pygame.mixer.Sound("0011.wav") # 온습도 경보
HT_02 = pygame.mixer.Sound("0012.wav") # 온습도 경보 해제
WT_01 = pygame.mixer.Sound("0021.wav") # 토양 수분 경보
WT_02 = pygame.mixer.Sound("0022.wav") # 토양 수분 경보 해제
P_Fan = pygame.mixer.Sound("0031.wav") # 수동 환기팬 가동
P_Pump = pygame.mixer.Sound("0041.wav") # 수동 물 펌프 가동
Emergency = pygame.mixer.Sound("0051.wav") # 긴급 상황(Zombie apocalypse)

GPIO.setup(Pump1_1, GPIO.OUT)
GPIO.setup(Pump1_2, GPIO.OUT)
GPIO.setup(Fan, GPIO.OUT)

GPIO.setup(LED_R, GPIO.OUT)
GPIO.setup(LED_G, GPIO.OUT)
GPIO.setup(LED_B, GPIO.OUT)

GPIO.setup(SW_01, GPIO.IN)
GPIO.setup(SW_02, GPIO.IN)
GPIO.setup(SW_03, GPIO.IN)


def read_spi_adc(adcChannel):
    adcValue=0
    buff=spi.xfer2([1,(8+adcChannel)<<4,0])
    adcValue = ((1023-(((buff[1]&3)<<8)+buff[2]))*2/1023)*100

    return adcValue

try:

    while True:
        wtime = datetime.datetime.now()
        h, temp = Adafruit_DHT.read_retry(sensor, pin)

        SW1 = GPIO.input(SW_01)
        SW2 = GPIO.input(SW_02)
        SW3 = GPIO.input(SW_03)

        if SW1 == True: # 수동 Fan 가동

            print("수동 팬 가동")
            GPIO.output(LED_R, False)
            GPIO.output(LED_G, True)
            GPIO.output(LED_B, True)

            P_Fan.play()
            GPIO.output(Fan, False)
            time.sleep(10)

        if SW2 == True: # 수동 펌프 가동

            print("수동 펌프 가동")
            GPIO.output(LED_R, True)
            GPIO.output(LED_G, True)
            GPIO.output(LED_B, False)

            P_Pump.play()
            GPIO.output(Pump1_1, True)
            GPIO.output(Pump1_2, False)
            time.sleep(10)

        if SW3 == True: # 비상 스위치

            print("비상 비상 비상")
            GPIO.output(LED_R, False)
            GPIO.output(LED_G, True)
            GPIO.output(LED_B, True)

            Emergency.play()
            time.sleep(33)


        if SW1 == False and SW2 == False and SW3 == False:

            print(wtime, 'Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temp, h))

            adcValue=read_spi_adc(0)
            print("Land Moisture Sensor : %d" %(adcValue))

            Rain = read_spi_adc(1)
            print("Rain : %d" %(Rain))
            
            CO2 = read_spi_adc(2)
            print("CO2 : %d" %(CO2))

            if temp>27 or h>60:

                GPIO.output(LED_R , False)
                GPIO.output(LED_G, True)
                GPIO.output(LED_B, True)

            elif adcValue<30:

                GPIO.output(LED_R, True)
                GPIO.output(LED_G, True)
                GPIO.output(LED_B, False)

            else:

                GPIO.output(LED_R, True)
                GPIO.output(LED_G, False)
                GPIO.output(LED_B, True)



            if temp>27 or h>60:
                HT_01.play()
                time.sleep(4)
                while 1:
                    GPIO.output(Fan, False)
                    h, temp = Adafruit_DHT.read_retry(sensor, pin)
                    print('온습도 정상화까지 대기중...')
                    print(wtime, 'Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temp, h))
                    time.sleep(1)
                    if temp<28 and h<71:
                        print('온습도 정상화 완료')
                        break

                GPIO.output(Fan, False)

            else:
                #HT_02.play()
                GPIO.output(Fan, True)


            if adcValue<30:
                WT_01.play()
                time.sleep(13)
                while 1:
                    GPIO.output(Pump1_1, True)
                    GPIO.output(Pump1_2, False)
                    adcValue=read_spi_adc(0)
                    print('토양 수분 정상화까지 대기중...')
                    print("Water Sensor : %d" %(adcValue))
                    time.sleep(1)
                    if adcValue>29:
                        print('토양 수분 정상화 완료')
                        break

            else:
                #WT_02.play()
                GPIO.output(Pump1_1, False)
                GPIO.output(Pump1_2, False)


            time.sleep(3)



except KeyboardInterrupt:
    pass
GPIO.cleanup()