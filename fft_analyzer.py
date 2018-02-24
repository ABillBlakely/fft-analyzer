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

# Turn off numpy warning on divide by zero:
seterr(divide='ignore')


class AudioStream():
    '''Controls the audio input and output.'''

    def __init__(self, args):

        def audio_callback(indata, outdata, frames, time, status):
            '''Called by audio stream for each new buffer.'''
            indataQ.append(indata[::, LEFT])
            if self.out_enable:
                outdata[:, LEFT] = self.out_deque[0]
                self.out_deque.rotate(-1)
            else:
                outdata.fill(0)
            self.cumulated_status |= status
            return None

        self.args = args
        self.out_enable = False

        fft_window = np.hanning(self.args.buff_size)
        # Setup the stream
        sd.default.device = [args.input_dev, args.output_dev]
        sd.default.channels = 2
        sd.default.dtype = None
        sd.default.latency = None
        sd.default.samplerate = args.sample_rate
        sd.default.blocksize = args.buff_size
        sd.default.clip_off = True
        sd.default.dither_off = args.dither
        sd.default.never_drop_input = None
        sd.default.prime_output_buffers_using_stream_callback = None

        # Checks will throw errors for invalid settings.
        sd.check_input_settings()
        sd.check_output_settings()

        # Will store sounddevice status flags on buffer under/overflows, etc.
        self.cumulated_status = sd.CallbackFlags()
        # Will store data to write to output buffer.
        self.out_deque = deque()

        # Create the stream
        self.audio_stream = sd.Stream(callback=audio_callback)

    def create_output_signal(self, freq=1000, level=-3, sig_type='sine'):
        '''Creates the array for global out_sig.
        Should eventually handle multiple signal types.
        Currently this only builds sine waves that are periodic
        in our buffer size multiplied by a precision value.
        It finds the closest frequency to the specified frequency which
        can be transformd via inverse fft.

        Arguments:
            freq (float): frequency in Hz.
            level (float): signal level in dB.
            sig_type (string): Currently only supports sine waves.
        Returns:
            (float): actual frequency in Hz.
            (float): signal level in dB.
            (str): the signal type.
        The generated output signal is written to the class level out_deque
        in pieces that are each equal to a buffer size.
        '''
        # Precision affects how closely we match the desired signal frequency.
        precision = int(2**16 / self.args.buff_size)
        # Turn output off while switching,
        # but remember if it should turn back on
        if self.out_enable:
            retoggle = True
            self.toggle_out()
        else:
            retoggle = False

        # Build frequency array zero padded for increased freq resolution.
        freq_array = fft.rfftfreq(n=precision * self.args.buff_size,
                                  d=(1 / self.args.sample_rate))
        # Find nearest frequency that is represented in the array
        closest_freq_index = np.searchsorted(freq_array, freq)
        # Construct zero valued magnitude array.
        mag_array = np.zeros_like(freq_array)
        # set magnitude scaled up to what it should be in frequency domain.
        mag_array[closest_freq_index] = ((10 ** (level / 20)
                                         * precision
                                         * self.args.buff_size / 2))
        # Get discrete sample array of length = precision * buff_size.
        out_sig = np.fft.irfft(a=mag_array, n=precision * self.args.buff_size)
        # Build the output deque in slices each equal to the buffer size.
        index = 0
        self.out_deque = deque()
        for index in range(int(len(out_sig) / self.args.buff_size)):
            self.out_deque.append(out_sig[index * self.args.buff_size:
                                  (index + 1) * self.args.buff_size])

        # Turn output back on if necessary
        if retoggle:
            self.toggle_out()

        return (freq_array[closest_freq_index], level, sig_type)

    def start_stream(self):
        self.audio_stream.start()
        while self.audio_stream.stopped:
            pass
        return self.audio_stream.active

    def toggle_out(self):
        self.out_enable = not self.out_enable
        return self.out_enable

    def stop_stream(self):
        self.audio_stream.stop()
        while self.audio_stream.active:
            pass
        return self.audio_stream.stopped

    def reload(self, args):
        self.audio_stream.close()
        print('audio closed.')
        plt.close()
        print('plot closed.')
        self.__init__(args)
        print('re-initialized.')
        return None


class FFTDisplay():
    '''Handles the display of the audio information.

    Currently this is using matplotlib to provide display duties,
    but this is temporary and will be replaced with something GUI
    compatible when work begins in earnest on GUI.
    '''
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
        return [self.line]

    def plot_callback(self, frame):
        '''Calculates and draws the new data.'''
        try:
            print(indataQ[0])
            a_in = indataQ.popleft()
            mag_in_dB = 20 * log10(abs(
                        fft.rfft(a=a_in, n=self.args.fft_size)
                        * 2 / self.args.buff_size))
            self.line.set_data(self.freq, mag_in_dB)
        except IndexError as err:
            # Occurs when indataQ is empty, hold current data.
            # self.line.set_data(self.freq, self.freq)
            # print(err)
            pass
        return [self.line]

    def start_plot(self):
        # Start the animation
        self.anim = FuncAnimation(fig=self.fig,
                                  func=self.plot_callback,
                                  frames=None,
                                  init_func=self.plot_init,
                                  fargs=None,
                                  interval=20,
                                  blit=True,
                                  repeat=False)
        plt.show()
        return None
