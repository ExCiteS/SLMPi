import math
import sys
import time

import numpy
import pygame
import pyaudio
import analyse

samplerate = 44100

# Initialize PyAudio
pyaud = pyaudio.PyAudio()

# Open input stream, 16-bit mono at 44100 Hz
# On my system, device 1 is a USB microphone, your number may differ.
stream = pyaud.open(
    format = pyaudio.paInt16,
    channels = 1,
    rate = 44100,
    input_device_index = 1,
    input = True)

# Open sound input before pygame, otherwise pygame hogs sounds
pygame.display.init()

screen = pygame.display.set_mode((1024, 768))


clk = pygame.time.Clock()
tm = 0

history = []

while True:
    
    tm += clk.tick()
    if tm > 8000: 
        tm = 0
        history = []
    # Read raw microphone data
    rawsamps = stream.read(1024)
    # Convert raw data to NumPy array
    samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
    # Show the volume and pitch
    screen.fill((0, 0, 0))
    tx = int((tm / 8000.0) * 1024.0)
    if tx > 1024: tx -= 1024
    pygame.draw.rect(screen, (0, 255, 0), (tx, 0, 3, 768))
    m, v = None, None
    m = analyse.musical_detect_pitch(samps, samplerate=samplerate)
    v = analyse.loudness(samps)
    if m is not None:
        # m is in range about 40-80
        ty = (m - 40.0) / 40.0
        # ty is in range 0-1
        ty = int(768 - ty * 768.0)
        # now ty is betwee 0 - 768
        pygame.draw.rect(screen, (0, 255, 255), (0, ty, 1024, 3))
        history.append((tx, ty))
    for (x, y) in history:
        pygame.draw.rect(screen, (255, 0, 0), (x, y, 3, 3))
    pygame.display.flip()
    for evt in pygame.event.get():
        if evt.type == pygame.KEYDOWN:
            sys.exit()
        if evt.type == pygame.QUIT:
            sys.exit()
