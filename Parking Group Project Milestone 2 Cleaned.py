"""
This code is meant to gauge the distance between an ultrasonic sensor and progressively change an RGB LED's light
in stages based on distance thresholds coded beforehand, with the purpose of warning
a driver to stop their car in a parking space before they hit the wall.

Modified by Kaitai Chen using code from Sean Peyton Burnett
October 23, 2026
"""

### First, import other functions from libraries

from machine import Pin, PWM
import utime

### Pin setup

trigger_pin = 1 # 1st GP
echo_pin = 2 # 2nd GP
buzzer_pin = 15 # 15th GP
red_pin = 22 # 22nd GP
green_pin = 21 # 21st GP
blue_pin = 20 # 20th GP

trigger = Pin(trigger_pin, Pin.OUT)  # Trigger pin sends pulse of current
echo = Pin(echo_pin, Pin.IN)         # Echo pin receives reflected pulse
red_led = PWM(Pin(red_pin)) # Red pin provides power to the red LED
green_led = PWM(Pin(green_pin)) # Green pin provides power to the green LED
blue_led = PWM(Pin(blue_pin)) # Blue pin provides power to the blue LED

red_led.freq(1000)
green_led.freq(1000)
blue_led.freq(1000)

### Settings

DISTANCE_THRESHOLD_CM = 10   # Distance before the final warning to stop is triggered

ALERT_ON_NO_OBJECT = True    # True = beep and flash when no object is detected
NO_OBJECT_FREQUENCY = 800    # Pitch (Hz) for the "no object" beep
NO_OBJECT_BEEP_TIME = 0.3    # Seconds on and off for the "no object" beep


### LED functions
    
def set_color(red, green, blue):
    """Set RGB LED color. Values should be 0-255"""
    # Convert 0-255 values to 0-65535 for duty_u16
    red_duty = int(red * 65535 / 255)
    green_duty = int(green * 65535 / 255)
    blue_duty = int(blue * 65535 / 255)
    
    red_led.duty_u16(red_duty)
    green_led.duty_u16(green_duty)
    blue_led.duty_u16(blue_duty)

def alert_stop(): # Stop immediately
    set_color (255, 0, 0) # Sets light to be red
    
def alert_medium(): # Warning, slow down on the approach
    set_color (238, 100, 10) # Set light to be yellow

def alert_proceed(): # Proceed with parking
    set_color (0, 255, 0) # Set light to be green

def alert_off(): # Turn off the light
    set_color (0, 0, 0)

# ---------------------------------------------------------------------------
# Ultrasonic sensor function
# ---------------------------------------------------------------------------
def ultra():
    """Return the distance to the nearest object in cm (None if no echo)."""
    # Send out a pulse from trigger pin
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(10)
    trigger.low()

    # Measure time of signal on vs off (with timeouts so it can't hang)
    timeout_us = 30000
    start = utime.ticks_us()
    while echo.value() == 0:
        if utime.ticks_diff(utime.ticks_us(), start) > timeout_us:
            return None
    signaloff = utime.ticks_us()

    while echo.value() == 1:
        if utime.ticks_diff(utime.ticks_us(), signaloff) > timeout_us:
            return None
    signalon = utime.ticks_us()

    timepassed = utime.ticks_diff(signalon, signaloff)

    # Calculate distance from speed of sound
    distance = (timepassed * 0.0343) / 2
    return distance


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
alert_off() # First, turn off the alarm upon activation of the code.

while True:
    distance = ultra()

    if distance is None:
        print("ERROR: No object detected")
        continue

    print("The distance from object is ", distance, "cm")

    if distance < DISTANCE_THRESHOLD_CM: # Time to stop
        alert_stop() # Turn on the alert
        utime.sleep(0.6)
    elif distance <= DISTANCE_THRESHOLD_CM + 30 and distance > DISTANCE_THRESHOLD_CM + 15: # Time to proceed
        alert_proceed()
        utime.sleep(0.5)
    elif distance <= DISTANCE_THRESHOLD_CM + 15: # Time to slow down
        alert_medium()
        utime.sleep(0.5)
    else: # System doesn't detect objects ahead
        alert_off()
        utime.sleep(0.5)

