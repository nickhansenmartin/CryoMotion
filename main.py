from machine import ADC, Pin, I2C, PWM
import uasyncio as asyncio
from pico_i2c_lcd import I2cLcd

# Assign buttons to pins
estop = Pin(21, Pin.IN, Pin.PULL_UP)
up = Pin(20, Pin.IN, Pin.PULL_UP)
down = Pin(19, Pin.IN, Pin.PULL_UP)

# Indicates button state
button = 0 # 0 = nothing, 1 = emergency stop, 2 = up, 3 = down

# Controls button activation
async def buttons():
    global button
    while True:
        if estop.value() == 0:
            print("EMERGENCY STOP")
            button = 1
        elif up.value() == 0:
            print("UP")
            button = 2
        elif down.value() == 0:
            print("DOWN")
            button = 3
        else:
            button = 0
        await asyncio.sleep(0.1)

# Creates i2c and lcd objects
i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)

# Controls screen
async def screen():
    while True:
        lcd.hide_cursor()
        if button == 0: # Default
            lcd.putstr("Cryogenic" + "\n" + "Motion" + "\n" +"Control")
        elif button == 1: # Stop
            lcd.putstr("WARNING:" + "\n" + "EMERGENCY STOP" + "\n" + "ACTIVATED!")
            await asyncio.sleep(2)
        elif button == 2: # Up
            lcd.putstr("Current State:" + "\n" + "Going Up!")
        elif button == 3: # Down
            lcd.putstr("Current State:" + "\n" + "Going Down!")
        await asyncio.sleep(0.5)
        lcd.clear()

# Motor settings
# Motor A
IN1 = Pin(3, Pin.OUT)
IN2 = Pin(4, Pin.OUT)

# Motor B
IN3 = Pin(6, Pin.OUT)
IN4 = Pin(7, Pin.OUT)

speedA = PWM(Pin(2))
speedB = PWM(Pin(8))
speedA.freq(1000)
speedB.freq(1000)

# Controls motors
async def motor_control():
    while True:
        if button == 0: # Default
            IN1.low()
            IN2.low()
            IN3.low()
            IN4.low()
        elif button == 1: # Stop
            IN1.low()
            IN2.low()
            IN3.low()
            IN4.low()
            # break
        elif button == 2: # Up
            speedA.duty_u16(17000) # Duty cycles account for incorrect wrong motor
            speedB.duty_u16(65535)
            IN1.low()
            IN2.high()
            IN3.high()
            IN4.low()
            await asyncio.sleep(1)
        elif button == 3: # Down
            speedA.duty_u16(17000)
            speedB.duty_u16(65535)
            IN1.high()
            IN2.low()
            IN3.low()
            IN4.high()
            await asyncio.sleep(0.5)
        await asyncio.sleep(0.5)

# MAIN FUNCTION #
async def main():
    asyncio.create_task(buttons())
    asyncio.create_task(screen())
    asyncio.create_task(motor_control())
    await asyncio.sleep(10000)

asyncio.run(main())
