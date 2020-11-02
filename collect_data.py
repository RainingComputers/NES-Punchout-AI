import sys
import time

import cv2
import mss
import numpy as np

import pykitml as pk
from pykitml import load, save


# Get command line arguments 
try:
    # Part of the screen to capture (1548, 203, 256, 256) 
    # for 1080p screen, top-right corner
    x, y, w, h = [int(num_str) for num_str in sys.argv[1].split(',')]
    filename = sys.argv[2]
except:
    print('USAGE: capture.py x,y,w,h FILENAME')
    exit()

inputs = []
outputs = []

def on_frame(server, frame):
    last_time = time.time()

    print('Frame:', frame)

    joypad = server.get_joypad()
    print('JOYPAD:', joypad)

    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": w, "height": h}
        # Get raw pixels from the screen, save it to a Numpy array
        img = np.array(sct.grab(monitor))
        # Resize image
        img = cv2.resize(src=img, dsize=(64, 64))
        # Convert to gray scale
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        # Reshape
        img = img.reshape(4096)

    # Continue emulation
    server.frame_advance()
    
    # Calculate up/sec
    ups = round(1 / (time.time() - last_time), 2)
    print('Ups/Sec = ', ups)

    # Collect data
    inputs.append(img)
    outputs.append(joypad)
    print('Collected:', len(inputs), 'frames')
    
def on_quit():
    # Process the collected data
    inputs_numpy = np.array(inputs)

    outputs_numpy = []
    for output in outputs:
        values = output.split()
        if(values[1] == 'true'): onehot = [1, 0, 0]
        elif(values[5] == 'true'): onehot = [0, 1, 0]
        else: onehot = [0, 0, 1]
        outputs_numpy.append(onehot)

    outputs_numpy = np.array(outputs_numpy)

    print('Collected', inputs_numpy.shape[0], 'frames.')

    if(inputs_numpy.shape[0] < 2000): print('Warning not enough data points.')

    save((inputs_numpy[:2000], outputs_numpy[:2000]), 'Data/'+filename)

# Intialize and start server
server = pk.FCEUXServer(on_frame, on_quit)
print(server.info)
server.start()
