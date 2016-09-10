'''Python Spectrum Analyzer'''

from collections import deque
from numpy import abs, fft, log10
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from args import arg

# Some aliases to make things readable.
LEFT = 0
RIGHT = 1

print(sd.query_devices())

indataq = deque(maxlen=10)


def output_signal(freq, Fs, buf_size):
    '''Create the signal for output'''
    None


def audio_callback(indata, outdata, frames, time, status):
    '''Called by audio stream for each new buffer.'''
    indataq.append(indata[::, LEFT])
    outdata.fill(0)


def plot_init():
    '''Provide blank data to the animation.'''
    line.set_data([], [])
    return line,


def update_plot(frame):
    '''Calculates and draws the new data.'''
    try:
        a_in = indataq.popleft()
        mag = 20 * log10(abs(fft.rfft(a_in, n=arg.fftsize) * 2 / arg.buffsize))
        line.set_data(freq, mag)
    except:
        # Drawing speed is higher than the data load, which is good, but we
        # can't have it throwing errors and coming to a halt.
        # This should probably be done a better way than try/except.
        None
    return line,

audio_stream = sd.Stream(callback=audio_callback,
                         channels=2,
                         samplerate=arg.Fs,
                         blocksize=arg.buffsize,
                         clip_off=arg.clipoff,
                         dither_off=arg.ditheroff
                         )


# Setup the display:
freq = fft.rfftfreq(arg.fftsize, 1 / arg.Fs)
fig = plt.figure()
ax = plt.axes(xlim=arg.freq_lim, ylim=arg.mag_lim)
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
