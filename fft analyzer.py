import numpy as np
from collections import deque
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation 
# import time

Fs = 48000
buf_size = 2048
fft_size = 4096

indataq = deque(maxlen=10)

# Default device is manually set, list possibilities with the print commands.
# sd.default.in
print(sd.query_devices())
# print(sd.query_hostapis())

# for now use stereo channels with left and right.
sd.default.channels = 2
# Some aliases to make things readable.
LEFT = 0
RIGHT = 1

# Most of the defaults are here for easy config.

# sd.default.dtype = 'float32'
# sd.default.latency = 'low'
sd.default.samplerate = Fs
sd.default.blocksize = buf_size
# sd.default.clip_off = False
sd.default.dither_off = True
sd.default.never_drop_input = False
sd.default.prime_output_buffers_using_stream_callback = False
# sd.default.reset()


def output_signal(freq, Fs, buf_size):
    '''Create the signal for output'''
    None


def audio_callback(indata, outdata, frames, time, status):
    '''Called by audio stream for each new buffer.'''
    indataq.append(indata[::, LEFT])


def plot_init():
    '''Provide blank data to the animation.'''
    line.set_data([], [])
    return line,


def update_plot(frame):
    '''Calculates and draws the new data.'''
    try:
        a_in = indataq.popleft()
        mag = 20 * np.log10(np.abs(np.fft.rfft(a_in, n=fft_size) * 2 / buf_size))
        line.set_data(freq, mag)
    except Exception as e:
        # Drawing speed is higher than the data load, which is good, but we
        # can't have it throwing errors and coming to a halt.
        None
    return line,

audio_stream = sd.Stream(callback=audio_callback)

# Setup the display:
freq = np.fft.rfftfreq(fft_size, 1.0 / Fs)
fig = plt.figure()
ax = plt.axes(xlim=(20, Fs / 2), ylim=(-150, 0))
ax.set_xscale('log', basex=10)
line, = ax.plot([], [])

# Start the animation
anim = FuncAnimation(fig,
                     update_plot,
                     # init_func=plot_init,
                     interval=20,
                     blit=True
                     )

with audio_stream:
    plt.show()
