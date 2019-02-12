#!/usr/bin/env python3

import sys
import wave
from math import log2
import struct
import numpy


def freq_to_pitch(freq, pitch):
    pitch_names = ["c", "cis", "d", "es", "e", "f", "fis", "g", "gis", "a", "bes", "b"]

    one_octave = 12
    sc_val = pitch * pow(2, -1 * (one_octave + 9) / one_octave)
    dist_val = (log2(freq) - log2(sc_val)) * one_octave

    octave_level = int(dist_val // one_octave)
    pitch_level = int(dist_val % one_octave)
    cents = int(100 * (dist_val % 1))

    if cents > 50:
        pitch_level = pitch_level + 1
        cents = cents - 100

    if pitch_level >= one_octave:
        pitch_level = pitch_level - one_octave
        one_octave = one_octave + 1

    pitch_name = pitch_names[pitch_level]
    if octave_level < 0:
        octave_sfx = ',' * ((-1 * octave_level) - 1)
        pitch_name = pitch_name.title()
    else:
        octave_sfx = "'" * octave_level

    return "{}{}{:+d}".format(pitch_name, octave_sfx, cents)


def cluster_peaks(peaks):
    clusters_list = []

    if len(peaks) == 0:
        return clusters_list

    clusters = []
    one_cluster = []
    peak_dist = 1

    for freq, amp in peaks:
        if len(one_cluster) > 0:
            prev_freq = one_cluster[-1][0]
            if prev_freq == freq - peak_dist:
                one_cluster = one_cluster + [(freq, amp)]
            else:
                cluster_max = max(one_cluster, key=lambda pair: pair[1])
                clusters = clusters + [cluster_max]
                one_cluster = [(freq, amp)]
        else:
            one_cluster = [(freq, amp)]

        if len(one_cluster) > 0:
            cluster_max = max(one_cluster, key=lambda pair: pair[1])
            clusters = clusters + [cluster_max]

    clusters_list = list(filter(lambda pair: pair[0] != 0, clusters))
    return clusters_list


def data_processing(data, is_stereo):
    if is_stereo:
        res = []
        for j in range(0, len(data), 2):
            cun = data[j:j + 2]
            res.append((cun[0] + cun[1]) / 2.0)
        return res
    else:
        return data


def find_peaks(win):
    amps = numpy.fft.rfft(win)
    my_sum = sum([numpy.abs(v) for v in amps])
    avg_amp = my_sum / len(amps)

    peaks = []
    for f, amp in enumerate(amps):
        if numpy.abs(amp) >= avg_amp:
            peaks.append((f, numpy.abs(amp)))
    return peaks


def print_result(result_list):
    time_from = result_list[0]["win_start"]
    time_to = result_list[0]["win_end"]
    from_to_res = result_list[0]["line"]
    for item in result_list:
        if from_to_res != item["line"]:
            print("%.1f-%.1f %s" % (time_from, time_to, from_to_res))
            time_from = item["win_start"]
            time_to = item["win_end"]
            from_to_res = item["line"]
        else:
            time_to = item["win_end"]
    print("%.1f-%.1f %s" % (time_from, time_to, from_to_res))


def main():
    if len(sys.argv) < 3:
        print("argv error: not enough program arguments")
        print("invocation: ./music.py freq file")
        sys.exit()

    input_freq = int(sys.argv[1])
    file_name = sys.argv[2]

    with wave.open(file_name, 'rb') as f:
        nchannels = f.getnchannels()
        framerate = f.getframerate()
        nframes = f.getnframes()

        is_stereo = True if nchannels == 2 else False
        d_bytes = f.readframes(nframes)
        data = [d for d in struct.unpack('{}h'.format(
               nchannels * nframes), d_bytes)]

    win_size = int(framerate * 0.1)
    win = []
    peaks = []
    win_start = 0.0
    win_end = 0.1
    result_list = []

    while data:
        win_frames = data[:win_size]
        del data[:win_size]
        if len(win_frames) == win_size:
            win = win + data_processing(win_frames, is_stereo)

            if len(win) < framerate:
                continue

            while len(win) > framerate:
                del win[:win_size]

            peaks = find_peaks(win)

            clusters_list = cluster_peaks(peaks)
            clusters_list = sorted(peaks, key=lambda p: p[1])
            clusters_list = clusters_list[-3:]

            res = []
            for one_cluster in sorted(clusters_list, key=lambda p: p[0]):
                res.append(freq_to_pitch(one_cluster[0], input_freq))

            result_list.append({"win_start": win_start, "win_end": win_end, 
                                    "line": " ".join(res) })
            win_start += 0.1
            win_end += 0.1

    if len(result_list) > 0:
        print_result(result_list)


if __name__ == '__main__':
    main()
