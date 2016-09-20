from collections import deque
from sys import argv
from threading import Thread
from time import sleep

import sounddevice as sd

from addarguments import addArgs
from fftanalyzer import plot_control


args = addArgs(argv)

if args.list_devices is True:
    print(sd.query_devices())
    exit()

# The Queue where the input data will be stored.
indataQ = deque(maxlen=10)


def loop():
    plot = plot_control(args)
    plot.start_plot()
    while True:
        print('loop')
        sleep(1)
        plot.update_plot()

thread = Thread(target=loop)
thread.start()
print('thread created')
