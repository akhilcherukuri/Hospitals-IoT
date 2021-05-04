import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735
# from heartbeat import read_temp, read_pulse
 
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
 
BAUDRATE = 24000000

spi = board.SPI()
 

disp = st7735.ST7735R(spi, rotation=90,           # 1.8" ST7735R
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)
#def aws_icon:


# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height
image = Image.new("RGB", (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# First define some constants to allow easy positioning of text.
padding = 6
x = 0

# Load a TTF Font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
filename = "/home/pi/iotproject/aws-iot-device-sdk-python/cmpe295/pulse_reading.txt"
filename2 = "/home/pi/iotproject/aws-iot-device-sdk-python/cmpe295/temp_reading.txt"
 
while True:
    # Draw a black filled box to clear the image.
    pulse_reading = 0
    temperature_reading = 0
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    draw.line((0,55,160,55), fill="#FFFFFF")

    f = open(filename, "r")
    pulse_reading = f.readline()
    f = open(filename2, "r")
    temperature_reading = f.readline()

 
    Line0 = " Remote Monitoring"
    Line1 = " and Operations"
    Line2 = " Management for Hospitals"
    Line3 = " Temperature ℃ :"
    Line3_2 = temperature_reading
    Line4 = " Pulse ❤️ : "
    Line4_2 = pulse_reading

    AWS_line = "☁"


    # Write four lines of text.
    y = padding
    draw.text((20, y), Line0, font=font, fill="#00FF00")
    y += 15
    draw.text((28, y), Line1, font=font, fill="#00FF00")
    y += 15
    draw.text((x, y), Line2, font=font, fill="#00FF00")
    y += 25
    draw.text((31, y), Line3, font=font, fill="#FF8800")
    y += 13
    draw.text((64, y), Line3_2, font=font, fill="#FF0000")
    y += 19
    draw.text((15,y-8), AWS_line, font=font, fill="#00FF00")
    draw.text((56, y), Line4, font=font, fill="#FF8800")
    y += 13
    draw.text((66, y), Line4_2, font=font, fill="#FF0000")
 
    # Display image.
    disp.image(image)
    time.sleep(0.3)