#!/usr/bin/env python

import numpy
import math
import pyaudio
import analyse
import datetime
import time
import httplib, urllib
from time import localtime, strftime
from subprocess import call
from scipy.signal import lfilter
from A_weighting import A_weighting


samplerate = 44100 #samples per second
t = 16 #seconds
samples = samplerate * t

B, A = A_weighting(samplerate)
trim = 93.97940008672037609572522210551 #p0-based offset (ask Matthias)

mic_gain = 12 #in dB (a gain of 12dB corresponds to 50%)

#Quick&dirty calibration
meteor_calibration_100 = -9 #dB offset, at gain 100% / 22 dB
meteor_calibration_50 = 0 #db offser, at gain 50% / 12 dB
calibration = meteor_calibration_50

 
lAeq = 0

#Setup audio recording:
pyau = pyaudio.PyAudio()
stream = pyau.open(format=pyaudio.paInt16, channels=1 , rate=samplerate, input=True, frames_per_buffer=samples, input_device_index=1)

def sound_level_meter():

 #       feed = api.feeds.get(FEED_ID)
 #       datastream = get_datastream(feed)


        while True:
                # Read raw microphone data:
                try:
                        rawsamps = stream.read(samples)
                except IOError, ioe:
                        print "IOError: " + str(ioe)
                        continue
                # Convert raw data to NumPy array:
                chunk = numpy.fromstring(rawsamps, dtype=numpy.int16)

                #Compute leq:
                #leq = compute_leq(chunk) + calibration

                #Compute LAeq
                filteredChunk = lfilter(B, A, chunk)

                global lAeq
                lAeq = compute_leq(filteredChunk) + calibration

                #print "Leq" + str(t) + "s  = " + str(leq) + " dB"
                print "LAeq" + str(t) + "s = " + str(lAeq) + " dB(A)"
                doit()
                #print ""
                
              

def compute_leq(chunk):
                #Loudness (code from analyse.loudness()):
                #data = numpy.array(chunk, dtype=float) / 32768.0
                #ms = math.sqrt(numpy.sum(data ** 2.0) / len(data)) #I don't think it needs the sqrt!?
                #if ms < 10e-8: ms = 10e-8
                #return 10.0 * math.log(ms, 10.0)

                data = numpy.array(chunk, dtype=float) / 32768.0
                ms = numpy.sum(data ** 2.0) / len(data)
                if ms < 10e-8: ms = 10e-8 #?

                return (10.0 * math.log(ms, 10.0)) + trim


def doit():
                params = urllib.urlencode({'field1': lAeq,'key':'A79TZLK14WVKVLQQ'})
                headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
                conn = httplib.HTTPConnection("api.thingspeak.com:80")
        
                try:
                       conn.request("POST", "/update", params, headers)
                       response = conn.getresponse()
                       print strftime("%a, %d %b %Y %H:%M:%S", localtime())
                       print response.status, response.reason
                       data = response.read()
                       conn.close()
                except:
                       print "connection failed"       



def init():
        print "Setting gain to 12dB / 50%:"
        call(["amixer", "-c", "1", "set", "Mic", "capture", str(mic_gain) + "dB"])
      
        print "Starting sound level meter:"
        sound_level_meter()


init()
