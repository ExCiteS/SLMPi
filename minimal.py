#!/usr/bin/env python

import numpy
import math
import pyaudio
import analyse
import datetime
import time
from subprocess import call
from scipy.signal import lfilter
from A_weighting import A_weighting
#import xively

#parameters
#FEED_ID = '576625546'
#API_KEY = '0ObUvSI2uqV1_x2Yw0MkX6V83Ca9nu9LMSG_NyzgK9Q'

samplerate = 44100 #samples per second
t = 10 #seconds
samples = samplerate * t

B, A = A_weighting(samplerate)
trim = 93.97940008672037609572522210551 #p0-based offset (ask Matthias)

mic_gain = 12 #in dB (a gain of 12dB corresponds to 50%)

#Quick&dirty calibration
meteor_calibration_100 = -9 #dB offset, at gain 100% / 22 dB
meteor_calibration_50 = 0 #db offser, at gain 50% / 12 dB
calibration = meteor_calibration_50

# initialize api client
#api = xively.XivelyAPIClient(API_KEY)

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
                lAeq = compute_leq(filteredChunk) + calibration

                #print "Leq" + str(t) + "s  = " + str(leq) + " dB"
                print "LAeq" + str(t) + "s = " + str(lAeq) + " dB(A)"
                #print ""
                
                #Try to upload the value to Xively
#                datastream.current_value = round(lAeq, 2)
#                datastream.at = datetime.datetime.utcnow()
#                try:
#                  datastream.update()
#                except requests.HTTPError as e:
#                  print "HTTPError({0}): {1}".format(e.errno, e.strerror)

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


# function to return a datastream object. This either creates a new datastream, or returns an existing one
#def get_datastream(feed):
#  try:
#    datastream = feed.datastreams.get("soundlevel")
#    print "Found existing datastream"
#    return datastream
#  except:
#    print "Creating new datastream"
#    datastream = feed.datastreams.create("soundlevel", tags= "LAeq" + str(t) + "s")
#    return datastream



def init():
        print "Setting gain to 12dB / 50%:"
        call(["amixer", "-c", "1", "set", "Mic", "capture", str(mic_gain) + "dB"])
      
        print "Starting sound level meter:"
        sound_level_meter()


init()
