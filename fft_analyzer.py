from collections import deque

import matplotlib.pyplot as plt
import sounddevice as sd
from matplotlib.animation import FuncAnimation
import numpy as np
from numpy import abs, fft, log10, seterr

# Some aliases to make things readable.
LEFT = 0
RIGHT = 1

# The Queue where the input data will be stored.
indataQ = deque(maxlen=10)
out_sig = None
seterr(divide='ignore')
cumulated_status = sd.CallbackFlags()


class AudioStream():
    '''Controls the audio input and output.'''

    def __init__(self, args):

        def audio_callback(indata, outdata, frames, time, status):
                '''Called by audio stream for each new buffer.'''
                global cumulated_status
                indataQ.append(indata[::, LEFT])
                if out_sig.any():
                    outdata[:, LEFT] = out_sig
                else:
                    outdata.fill(0)
                cumulated_status |= status

        # Checks will throw errors for invalid settings.
        sd.check_input_settings()
        sd.check_output_settings()

        self.args = args

        # Create the stream
        self.audio_stream = sd.Stream(callback=audio_callback,
                                      channels=2,
                                      samplerate=args.sample_rate,
                                      blocksize=args.buff_size,
                                      clip_off=True,
                                      dither_off=args.dither)

    def create_output_signal(self, freq=1000, level=0.98):
        '''Return numpy array of the output signal.'''
        global out_sig
        freq_array = fft.rfftfreq(n=self.args.buff_size,
                                  d=(1 / self.args.sample_rate))
        mag_array = np.zeros_like(freq_array)
        closest_freq = np.searchsorted(freq_array, freq)
        mag_array[closest_freq] = level * self.args.buff_size / 2
        output = np.fft.irfft(a=mag_array, n=self.args.buff_size)
        out_sig = output.copy()
        return(output)

    def start_stream(self):
        self.create_output_signal()
        self.audio_stream.start()

    def stop_stream(self):
        global cumulated_status
        self.audio_stream.stop()
        print(str(cumulated_status))

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
    '''Handles the display of the audio information.'''
    def __init__(self, args):
        self.args = args
        # Determine the frequencies the dfft calculates at.
        self.freq = fft.rfftfreq(n=args.fft_size,
                                 d=(1 / args.sample_rate))
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
            mag_in_dB = 20 * log10(abs(
                        fft.rfft(a=a_in, n=self.args.fft_size)
                        * 2 / self.args.buff_size))
            self.line.set_data(self.freq, mag_in_dB)
        except IndexError:
            # Occurs when indataQ is empty.
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
