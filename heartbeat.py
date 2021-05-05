import Adafruit_ADS1x15
import serial
import time
import smbus
import os
import linecache

i2c_ch = 3 #Channel 1 for heartbeat sensor and channel 3 for temperature sensor

# TMP102 address on the I2C4 bus
i2c_address = 0x48

# Register addresses
reg_temp = 0x00
reg_config = 0x01

filename = "/home/pi/iotproject/aws-iot-device-sdk-python/cmpe295/pulse_reading.txt"
filename2 = "/home/pi/iotproject/aws-iot-device-sdk-python/cmpe295/temp_reading.txt"

# Calculate the 2's complement of a number
def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

# Read temperature registers and calculate Celsius
def read_temp():

    # Read temperature registers
    val = bus.read_i2c_block_data(i2c_address, reg_temp, 2)
    # NOTE: val[0] = MSB byte 1, val [1] = LSB byte 2
    #print ("!shifted val[0] = ", bin(val[0]), "val[1] = ", bin(val[1]))

    temp_c = (val[0] << 4) | (val[1] >> 4)
    #print (" shifted val[0] = ", bin(val[0] << 4), "val[1] = ", bin(val[1] >> 4))
    #print (bin(temp_c))

    # Convert to 2s complement (temperatures can be negative)
    temp_c = twos_comp(temp_c, 12)

    # Convert registers value to temperature (C)
    temp_c = temp_c * 0.0625
    temp_c = round(temp_c, 2)
    file = open(filename2, "w")
    file.write( str(temp_c) )
    file.flush()
    # print(temp_c)
    # return temp_c

# Initialize I2C (SMBus)
bus = smbus.SMBus(i2c_ch)

# Read the CONFIG register (2 bytes)
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
# print("Old CONFIG:", val)

# Set to 4 Hz sampling (CR1, CR0 = 0b10)
val[1] = val[1] & 0b00111111
val[1] = val[1] | (0b10 << 6)

# Write 4 Hz sampling back to CONFIG
bus.write_i2c_block_data(i2c_address, reg_config, val)

# Read CONFIG to verify that we changed it
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
# print("New CONFIG:", val)

def read_pulse():
    GAIN = 2/3  #gain =1 for 4V, 2/3 for 6V
    counter = 0  #setting the counter for temperature
    runningTotal = 0
    rate = [0]*10 #array that hold last 10 IBI value
    amp = 100 #amplitude of pulse waveform
    firstBeat = True; #used to seed rate array so we can start with reasonable BPM
    secondBeat = False; #used to seed rate array so we can start with reasonable BPM
    sampleCounter = 0 #use to determine pulse timing
    lastBeatTime = 0 #used to find IBI
    lastTime = int(time.time()*1000) #timing calculation
    th = 525 #used to find the instant moment of heart beat
    P = 512 # use to find peak in pulse wave
    T = 512 #use to find trough in pulse wave
    IBI = 600 # int that holds the time interval between beats
    Pulse = False; #"true" when user hearbeat detected.
    adc = Adafruit_ADS1x15.ADS1015()   #the adc convertor that we use
    while True:  
          counter = counter+1 #counter for the temperature
         
          Signal = adc.read_adc(0, gain=GAIN)
         
          currentTime = int(time.time()*1000)
          #setting current time
         
          sampleCounter += currentTime - lastTime
          lastTime = currentTime
         
          N = sampleCounter - lastBeatTime
   
   # find the peak and trough of the pulse wave
          if Signal > th and  Signal > P:          
            P = Signal
         
          if Signal < th and N > (IBI/5.0)*3.0 :  
            if Signal < T :                      
                T = Signal
               
          # signal surges up in value every time there is a pulse
          if N > 250 :                   # avoid high frequency noise          
            if  (Signal > th) and  (Pulse == False) and  (N > (IBI/5.0)*3.0)  :      
              Pulse = True;                       #set pulse to true
              IBI = sampleCounter - lastBeatTime  #measure the time between beats in mS
              lastBeatTime = sampleCounter        #keep track of time for next pulse

              if secondBeat:                     # if this is the second beat, if secondBeat == TRUE
                secondBeat = False;                # clear secondBeat flag
                for i in range(len(rate)):             # seed the running total to get a realisitic BPM at startup
                  rate[i] = IBI                      

              if firstBeat :                   # if this is the second beat, if secondBeat == TRUE    
                firstBeat = False;                  # clear firstBeat flag
                secondBeat = True;                   # set the second beat flag
                continue                              
 
 # keep a running total of the last 10 IBI values  
              rate[:-1] = rate[1:]                # shift data in the rate array
              rate[-1] = IBI                      # add the latest IBI to the rate array
              runningTotal = sum(rate)            # add upp oldest IBI values
             
              runningTotal /= len(rate)           # average the IBI values
 
              BPM = int(60000/runningTotal)      
              # temperature = read_temp()
              # print(str(BPM))
              file = open(filename, "w")
              file.write( str(BPM) )
              file.flush()

            if Signal < th and Pulse == True:
                Pulse = False;
                amp = P - T                  
                th = amp/2 + T
                T = th
                P = th

            if N > 2500 :
                th = 512
                T = 512                  
                P = 512                                            
                lastBeatTime = sampleCounter
                firstBeat = 0                    
                secondBeat = 0    
                # temperature = read_temp()              
                # print("0")
                file = open(filename, "w")
                file.write("0")
                file.flush()
          
            time.sleep(0.005)

read_temp()
read_pulse()
