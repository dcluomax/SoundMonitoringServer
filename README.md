# SoundMonitoringServer
A super lightweight baby sound monitor server for RaspberryPi or IoT devices in python

## Why
^ do anyone want to spend $$$ on baby sleep tracking devices when you have Raspberry Pi Zero ($10) and a microphone.

## How
### packages used (pre-req)
python and...
```
from http.server import BaseHTTPRequestHandler
import ctypes
import http.server
import json
import multiprocessing as mp
import numpy as np
import pyaudio
import socketserver
import time
```
### run
```
git clone https://github.com/dcluomax/SoundMonitoringServer.git
cd SoundMonitoringServer
cd src
nohup python main.py &
```
### access
by default `http://localhost:8080/`

you can change it to your desired port in `main.py`

## Customize

### main.py
register it as a service if you like.

### index.html 
data leverages https://developers.google.com/chart/interactive/docs/reference#datatable-class

you can filter on noise level, calculate last quiet time, or count noise timespan as you desire. In fact, changes to this file is recommended.
