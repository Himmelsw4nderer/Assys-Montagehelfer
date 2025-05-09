#!/usr/bin/env python3

import time
from rpi_ws281x import PixelStrip, Color

# LED strip configuration:
LED_COUNT = 26        # Number of LED pixels.
LED_PIN = 12          # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                if i + q < strip.numPixels():
                    strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                if i + q < strip.numPixels():
                    strip.setPixelColor(i + q, 0)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

# Main program logic follows:
if __name__ == '__main__':
    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Initialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')

    try:
        while True:
            print('Color wipe animations.')
            colorWipe(strip, Color(255, 0, 0))  # Red
            colorWipe(strip, Color(0, 255, 0))  # Green
            colorWipe(strip, Color(0, 0, 255))  # Blue

            print('Theater chase animations.')
            theaterChase(strip, Color(127, 127, 127))  # White
            theaterChase(strip, Color(127, 0, 0))  # Red
            theaterChase(strip, Color(0, 0, 127))  # Blue

            print('Rainbow animation.')
            rainbow(strip)

    except KeyboardInterrupt:
        colorWipe(strip, Color(0, 0, 0), 10)  # Turn off all LEDs
