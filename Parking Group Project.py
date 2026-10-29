"""
This code 

Modified by Kaitai Chen using code from Sean Peyton Burnett
October 23, 2026
"""

from machine import Pin, PWM
import utime

# ---------------------------------------------------------------------------
# Pin setup
# ---------------------------------------------------------------------------
trigger_pin = 1 # 28th GP
echo_pin = 2 # 27th GP
buzzer_pin = 15 # 15th GP
red_pin = 22 # 20th GP
green_pin = 21 # 19th GP
blue_pin = 20 # 18th GP

trigger = Pin(trigger_pin, Pin.OUT)  # Trigger pin sends pulse of current
echo = Pin(echo_pin, Pin.IN)         # Echo pin receives reflected pulse
buzzer = PWM(Pin(buzzer_pin))
red_led = PWM(Pin(red_pin)) # Red pin provides power to the red LED
green_led = PWM(Pin(green_pin)) # Green pin provides power to the green LED
blue_led = PWM(Pin(blue_pin)) # Blue pin provides power to the blue LED

red_led.freq(1000)
green_led.freq(1000)
blue_led.freq(1000)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
DISTANCE_THRESHOLD_CM = 7   # Alert when an object is closer than this
BUZZ_FREQUENCY = 2000        # Pitch of the buzz in Hz
BUZZ_VOLUME = 20000          # 0 (silent) to 65535 (loudest)
BEEP_MODE = True             # True = beep on/off, False = continuous buzz
PLAY_SONG = False            # True = play the song instead of buzzing

ALERT_ON_NO_OBJECT = True    # True = beep and flash when no object is detected
NO_OBJECT_FREQUENCY = 800    # Pitch (Hz) for the "no object" beep
NO_OBJECT_BEEP_TIME = 0.3    # Seconds on and off for the "no object" beep

# ---------------------------------------------------------------------------
# Note frequencies (only used if PLAY_SONG is True)
# ---------------------------------------------------------------------------
tones = {
    "E5": 659, "G5": 784, "A5": 880, "B5": 988,
}

# "P" = pause
song = ["E5", "G5", "A5", "P", "E5", "G5", "B5", "A5", "P",
        "E5", "G5", "A5", "P", "G5", "E5"]


# ---------------------------------------------------------------------------
# Buzzer and LED functions
# ---------------------------------------------------------------------------
def playtone(frequency, volume=BUZZ_VOLUME):
    buzzer.freq(frequency)
    buzzer.duty_u16(volume)


def bequiet():
    buzzer.duty_u16(0)
    
def set_color(red, green, blue):
    """Set RGB LED color. Values should be 0-255"""
    # Convert 0-255 values to 0-65535 for duty_u16
    red_duty = int(red * 65535 / 255)
    green_duty = int(green * 65535 / 255)
    blue_duty = int(blue * 65535 / 255)
    
    red_led.duty_u16(red_duty)
    green_led.duty_u16(green_duty)
    blue_led.duty_u16(blue_duty)



def alert_on():
    set_color (255, 0, 0) # Sets light to be red
    playtone(BUZZ_FREQUENCY)


def alert_off(): # Turn off the light
    set_color (0, 0, 0)
    bequiet()


def no_object_alert():
    """Slower, lower-pitched beep and flash so it sounds different from
    the close-object alert."""
    led.value(1)
    playtone(NO_OBJECT_FREQUENCY)
    utime.sleep(NO_OBJECT_BEEP_TIME)
    alert_off()
    utime.sleep(NO_OBJECT_BEEP_TIME)


def playsong(mysong):
    led.value(1)
    for note in mysong:
        if note == "P":
            bequiet()
        else:
            playtone(tones[note])
        utime.sleep(0.3)
    alert_off()


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
alert_off()

while True:
    distance = ultra()

    if distance is None:
        print("No object detected")
        #if ALERT_ON_NO_OBJECT:
            #no_object_alert()
        #else:
            #alert_off()
            #utime.sleep(0.2)
        continue

    print("The distance from object is ", distance, "cm")

    if distance < DISTANCE_THRESHOLD_CM: # Time to stop
        #if PLAY_SONG:
            #playsong(song)
        #elif BEEP_MODE:
            #alert_on()
            #utime.sleep(0.1)
            #alert_off()
            #utime.sleep(0.1)
        alert_on() # Turn on the alert
        utime.sleep(0.6)
    elif distance <= DISTANCE_THRESHOLD_CM + 23 and distance > DISTANCE_THRESHOLD_CM + 8: # Time to proceed
        set_color (0, 255, 0) # Set light to be green
        utime.sleep(1)
    elif distance <= DISTANCE_THRESHOLD_CM + 8: # Time to slow down
        set_color (238, 100, 10) # Set light to be yellow
        utime.sleep(1)
    else: # System doesn't detect objects ahead
        alert_off()
        utime.sleep(0.7)
