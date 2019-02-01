#!/usr/bin/env python3

import sys
import numpy
import wave
import struct
import operator

def get_peaks(window):
    peaks = []
    i = 0
    for val in window:
        if val >= 20 * numpy.mean(window):
            peaks.append((i, val))
        i += 1
    return peaks

def get_float_by_channel(frame, number_of_channels):
    s_data = struct.unpack('{n}h'.format(n=number_of_channels), frame)
    d0 = s_data[0]
    if number_of_channels == 2:
        d1 = s_data[1]
        return float((d0 + d1) / 2)
    else:
        return float(d0)

def process_input(file_name):
    file = wave.open(file_name, 'rb')
        
    number_of_channels = file.getnchannels()
    frames = file.getnframes()
    framerate = file.getframerate()

    float_list = []
    for i in range(frames):
        frame = file.readframes(1)
        float_val = get_float_by_channel(frame, number_of_channels)
        float_list.append(float_val)

    file.close()

    chunk_len = frames // framerate
    peaks = []
    for i in range(chunk_len):
        start = i * framerate
        end = (i + 1) * framerate
        fft_dat = numpy.fft.rfft(float_list[start: end])
        my_peaks = get_peaks(numpy.abs(fft_dat))
        peaks.extend(my_peaks)
    return peaks

def print_min_max(peaks):
    if len(peaks) == 0:
        print("no peaks")
    else:
        maximum_peak = max(peaks, key=operator.itemgetter(0))
        minimum_peak = min(peaks, key=operator.itemgetter(0))
        print("low = " + str(minimum_peak[0]) + ", " + "high = " + str(maximum_peak[0]))

# start
if len(sys.argv) < 2:
    print("argv error: not enough program arguments")
    print("invocation: ./peaks.py file.wav")
    sys.exit()

file_name = sys.argv[1]
peaks = process_input(file_name)
print_min_max(peaks)
