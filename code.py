import time
import board
import busio
from adafruit_emc2101 import EMC2101
import digitalio
import neopixel


g,r,b = 0,0,0
mintemp = 20 # Temperature Boundaries. Closer to this is green. LEDs
maxtemp = 35 # Temperature Boundaries. Closer to this is red. LEDs
LEDBRIGHTNESS = 0.6 # Yes, you can change the brightness here
BAUD_RATE = 115200 # The UART connection speed
TIMEOUT = 0 # number of time before timeout

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
pixels = neopixel.NeoPixel(board.GP15, 2, brightness=LEDBRIGHTNESS, auto_write=False, pixel_order="GRB")

button = digitalio.DigitalInOut(board.GP12) # Button on the back of the fan unit

fan_power = digitalio.DigitalInOut(board.GP16) # The fan power control is on GPIO16 you can turn it off/on.
fan_power.direction = digitalio.Direction.OUTPUT
fan_power.value = True # Turn on Fan

UART0 = busio.UART(board.GP0, board.GP1, baudrate=BAUD_RATE, timeout=TIMEOUT) 
UART1 = busio.UART(board.GP8, board.GP9, baudrate=BAUD_RATE, timeout=TIMEOUT)
I2C = busio.I2C(board.GP5, board.GP4) 
emc = EMC2101(I2C)


def show(percent, pixel):
    a = int(round((510 / 100) * percent))
    if a > 255:
        r = 255
        g = 510 - a
    else:
        r = a
        g = 255
    pixels[pixel] = (g, r, b)
    pixels.show()
#    return print('showed', a, 'on', pixel)

# Set Fan Speed 0 < 100 and Print text 
def setFanSpeed(speed:int):
    if(speed < 0):
        speed = 0
    elif (speed > 100):
        speed = 100
    print("Setting fan speed to",str(speed)+"%")
    emc.manual_fan_speed = speed
    time.sleep(2)
    print("Fan speed", emc.fan_speed, "RPM")
    time.sleep(1)

# Compare to see if the external or internal temperature are in the range 
def checkTempInRange(low:int, high:int):
    return low <= emc.external_temperature < high or low <= emc.internal_temperature < high

while True:
    
    temp = emc.external_temperature        
    if mintemp <= temp <= maxtemp:
        temp = temp - mintemp
        mtemp = maxtemp - mintemp
        c = int(round((temp / mtemp) * 100))
        show(c, 0)
    elif temp < mintemp:
        pixels[0] = (255, 0, 0)
    else:
        pixels[0] = (0, 255, 0)
     
    temp = emc.internal_temperature + 2
    if mintemp <= temp <= maxtemp:
        temp = temp - mintemp
        mtemp = maxtemp - mintemp
        c = int(round((temp / mtemp) * 100))
        show(c, 1)
    elif temp < mintemp:
        pixels[1] = (255, 0, 0)
    else:
        pixels[1] = (0, 255, 0)
    time.sleep(0.1)
    
    dataA = UART0.read(8)
    dataB = UART1.read(8)
    #uart.write(bytes(str("Hello Blade A" + "\n"),'UTF-8'))
    #uart1.write(bytes(str("Hello Blade B" + "\n"),'UTF-8'))
    #print (dataA)
    #print (dataB)

    try:
        dataA=int(dataA)
    except:        
        dataA = 'Auto'
    try:
        dataB=int(dataB)
    except:        
        dataB = 'Auto'

#     if dataA is not None:
#         dataA = dataA.decode()
#     if dataB is not None:
#         dataB = dataB.decode()
    if button.value:
        print("Button is not pressed")
    else:
        print("Button pressed")
        
    print("From Blade A", dataA)
    print("From Blade B", dataB)
    
    print("Internal temperature:", emc.internal_temperature, "C")
    print("External temperature:", emc.external_temperature, "C")
    BladeA_uart_info = bytes(str("Internal temperature: " + str(emc.internal_temperature) + " C" + "\r\n"),'UTF-8')
    BladeB_uart_info = bytes(str("External temperature: " + str(emc.external_temperature) + " C" + "\r\n"),'UTF-8')
    #BladeA_uart_info = bytes(str(str(emc.external_temperature) + " C" + "\r\n"),"ascii")
    #BladeB_uart_info = bytes(str(str(emc.internal_temperature) + " C" + "\r\n"),"ascii")
    #print(BladeA_uart_info + BladeB_uart_info)
    fan_speed=bytes(str("Fan speed: " + str(emc.fan_speed) + "RPM" + "\r\n" + "\r\n"),'UTF-8')
    blade_request=bytes(str("Blade A: " + str(dataA) + "%" + "| Blade B: " + str(dataB) + "%" + "\r\n"),'UTF-8')
    UART0.write(BladeA_uart_info + BladeB_uart_info + blade_request + fan_speed)
    UART1.write(BladeA_uart_info + BladeB_uart_info + blade_request + fan_speed)
    
    if dataA is not 'Auto' and dataB is not 'Auto':
        print("Both blades want to set the temperature")
        print("Blade A asks:", dataA, "%")
        print("Blade B asks:", dataB, "%")
        emc.manual_fan_speed = int(max(dataA, dataB))
        print("Fan speed", emc.fan_speed, "RPM or", int(max(dataA, dataB)), "%")
        time.sleep(2)
        print("")
        continue   
    if (dataA is not 'Auto' and dataB is 'Auto') or (dataA is 'Auto' and dataB is not 'Auto'):  #xor in a hurry
        if dataA is not 'Auto':
            led.value = True
            print("Set the speed as Blade A asks:", dataA, " %")
            emc.manual_fan_speed = int(dataA)
            time.sleep(1)
            print("Fan speed", emc.fan_speed, "RPM")
            time.sleep(1)
        if dataB is not 'Auto':
            led.value = True
            print("Set the speed as Blade B asks:", dataB, " %")
            emc.manual_fan_speed = int(dataB)
            time.sleep(2)
            print("Fan speed", emc.fan_speed, "RPM")
        time.sleep(2)
        print("")
        continue 
        
    else:
        # If temp exceeds 40C turn fan on 100%
        if 40 <= emc.external_temperature or 40 <= emc.internal_temperature:
            led.value = True
            setFanSpeed(100)

        # If temp between 35C to 40C set fan speed to 70% 
        elif checkTempInRange(35,40):
            setFanSpeed(70)

        # If temp between 33C to 35C set fan speed to 70% 
        elif checkTempInRange(33,35):
            led.value = True
            setFanSpeed(60)

        # If temp between 13C to 33C set fan speed to 70% 
        elif checkTempInRange(31,33):
            led.value = True
            setFanSpeed(40)

        # If temp between 29C to 31C set fan speed to 70% 
        elif checkTempInRange(29,31):
            # led.value = True
            setFanSpeed(30)

        # If temp lower than 29C set fan speed to 10% 
        else:
            # led.value = True
            setFanSpeed(10)

    print("")
    time.sleep(1)