from collections import deque

import matplotlib.pyplot as plt
import sounddevice as sd
from matplotlib.animation import FuncAnimation
from numpy import abs, fft, log10, seterr

# Some aliases to make things readable.
LEFT = 0
RIGHT = 1

# The Queue where the input data will be stored.
indataQ = deque(maxlen=10)

seterr(divide='ignore')


class AudioStream():
    '''Creates stream and plot, performs math, starts and stops processing.'''

    def __init__(self, args):

        def audio_callback(indata, outdata, frames, time, status):
                '''Called by audio stream for each new buffer.'''
                indataQ.append(indata[::, LEFT])
                outdata.fill(0)

        # Create the stream
        self.audio_stream = sd.Stream(callback=audio_callback,
                                      channels=2,
                                      samplerate=args.sample_rate,
                                      blocksize=args.buff_size,
                                      clip_off=True,
                                      dither_off=args.dither)

    def output_signal(freq, Fs, buf_size,):
        '''Create the signal for output'''
        None

    def start_stream(self):
        self.audio_stream.start()

    def stop_stream(self):
        self.audio_stream.stop()

    def reload(self):
        self.audio_stream.close()
        print('audio closed.')
        plt.close()
        print('plot closed.')
        self.__init__()
        print('re-init.')
        self.start_plot()
        print('plot started.')


class FFTDisplay():

    def __init__(self, args):
        self.args = args
        # Determine the frequencies the dfft calculates at.
        self.freq = fft.rfftfreq(args.fft_size, 1 / args.sample_rate)
        # Setup the display:
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=args.xlims, ylim=args.ylims)
        self.ax.set_xscale('log', basex=10)
        self.line, = self.ax.plot([], [])
        plt.ion()

    def plot_init(self):
        '''Provide blank data to the animation.'''
        self.line.set_data([], [])
        return self.line,

    def update_plot(self, frame):
        '''Calculates and draws the new data.'''
        try:
            a_in = indataQ.popleft()
            xform = fft.rfft(a_in, n=self.args.fft_size)
            mag = xform * 2 / self.args.buff_size
            mag_in_dB = 20 * log10(abs(mag))
            self.line.set_data(self.freq, mag_in_dB)
        except IndexError:
            # Occurs when indataQ is empty.
            pass
        except RuntimeWarning:
            # Is thrown when the input data contains a zero.
            pass
        return self.line,

    def start_plot(self):
        # Start the animation
        self.anim = FuncAnimation(self.fig,
                                  self.update_plot,
                                  init_func=self.plot_init,
                                  interval=2,
                                  blit=True
                                  )
        plt.show()
        # while self.audio_stream.active:
