#!/usr/bin/python
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler
import ctypes
import http.server
import json
import multiprocessing as mp
import numpy as np
import pyaudio
import socketserver
import time

# configs

CHUNK_SIZE = 8192
AUDIO_FORMAT = pyaudio.paInt16
SAMPLE_RATE = 16000
PORT = 8080
BUFFER_SIZE = int(3 * 60 * 60 * (SAMPLE_RATE / float(CHUNK_SIZE)))  # 3 hours of data


def process_audio(shared_time, shared_volume, lock):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=AUDIO_FORMAT, channels=1, rate=SAMPLE_RATE,
                     input=True, frames_per_buffer=CHUNK_SIZE)
    index = 0
    while True:
        lock.acquire()
        audio = np.fromstring(stream.read(CHUNK_SIZE), np.int16)
        shared_time[index] = time.time()
        shared_volume[index] = np.abs(audio).max()
        lock.release()
        if index >= BUFFER_SIZE-1:
            index = BUFFER_SIZE-1
            np.roll(shared_time, -1)
            np.roll(shared_volume, -1)
        else:
            index = index + 1
        time.sleep(1)
    stream.stop_stream()
    stream.close()
    pa.terminate()


def start_web(shared_time, shared_volume, lock):

    class HTTPRequestHandler(BaseHTTPRequestHandler):

        def setup(self):
            BaseHTTPRequestHandler.setup(self)
            self.request.settimeout(1)

        def do_GET(self):
            self.send_response(200)
            if self.path == '/getdata':
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                lock.acquire()
                retdata = np.stack((np.array(shared_time, dtype='int'),
                                   np.array(shared_volume, dtype='int'
                                   )), axis=1)
                lock.release()
                self.wfile.write(bytearray(json.dumps(retdata.tolist()),
                                 'utf-8'))
            else:
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                f = open('index.html', 'rb')
                self.wfile.write(f.read())

    with socketserver.TCPServer(('', PORT), HTTPRequestHandler) as \
        httpd:
        print ('Started #', PORT)
        httpd.serve_forever()


def init_server():
    lock = mp.Lock()
    shared_time = mp.Array(ctypes.c_double, BUFFER_SIZE, lock=False)
    shared_volume = mp.Array(ctypes.c_short, BUFFER_SIZE, lock=False)
    p1 = mp.Process(target=process_audio, args=(shared_time,
                    shared_volume, lock))
    p2 = mp.Process(target=start_web, args=(shared_time, shared_volume,
                    lock))
    p1.start()
    p2.start()


if __name__ == '__main__':
    init_server()