
import argparse
import matplotlib.pyplot as plt
import sounddevice as sd
from collections import deque
from matplotlib.animation import FuncAnimation
from numpy import abs, fft, log10, seterr

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('-b', '--buff-size', action='store', type=int,
                    default=4096, #choices=[512,1024,2048,4096],
                    help='Buffer size of audio stream.')

parser.add_argument('-d', '--dither', action='store_false',
                    help='Turn dithering on.') # Beware double negative: toggles sound devices 'dither_off' so false here turns dithering on.

parser.add_argument('-s', '--sample-rate', action='store', type=int, metavar='RATE',
                    default=48000, choices=[44100,48000,88200,96000],
                    help=('Sample rate used by device. Not all choices can be used by all devices. '
                          'Default is %(default)s, available choices are [%(choices)s].'))

parser.add_argument('-l', '--list-devices', action='store_true',
                    help='View available devices for this computer.')

parser.add_argument( '-i', '--input-device',  action='store', type=int, metavar='DEV_ID',
                    help="Integer value of device to use for input, see 'list-devices.'")

parser.add_argument('-o', '--output-device', action='store', type=int, metavar='DEV_ID',
                    help="Integer value of device to use for output, see 'listdevices.'")

parser.add_argument('-f', '--fft-size', action='store', type=int, metavar='SIZE',
                    default=16384, choices=[4096, 8192, 16384, 32768, 65536, 131072],
                    help=('Select the size of the fft sample. '
                          'Default is %(default)s, available choices are: [%(choices)s].'))

parser.add_argument('-x', '--xlims', nargs=2, action='store', type=int, metavar=('LOWER', 'UPPER'),
                    default =(20, 20000),
                    help='Magnitude axis limits in dB. Default is %(default)s.')

parser.add_argument('-y', '--ylims', nargs=2, action='store', type=int, metavar=('LOWER', 'UPPER'),
                    default =(-150, 0),
                    help='Freq axis limits in Hz. Default is %(default)s.')

args = parser.parse_args()
# print(args)
# exit()
if args.list_devices == True:
    print(sd.query_devices())
    exit()

# Some aliases to make things readable.
LEFT = 0
RIGHT = 1

# The Queue where the input data will be stored.
indataQ = deque(maxlen=10)

def audio_callback(indata, outdata, frames, time, status):
        '''Called by audio stream for each new buffer.'''
        indataQ.append(indata[::, LEFT])
        outdata.fill(0)

class audio_processor():
    '''Creates stream and plot, performs math, starts and stops processing.'''

    def __init__(self):
        # Create the stream
        self.audio_stream = sd.Stream(callback=audio_callback,
                                      channels=2,
                                      samplerate=args.sample_rate,
                                      blocksize=args.buff_size,
                                      clip_off=True,
                                      dither_off=args.dither)
        # Determine the frequencies the dfft calculates at.
        self.freq = fft.rfftfreq(args.fft_size, 1 / args.sample_rate)
        # Setup the display:
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=args.xlims, ylim=args.ylims)
        self.ax.set_xscale('log', basex=10)
        self.line, = self.ax.plot([], [])
        plt.ion()

    def output_signal(freq, Fs, buf_size):
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

    def plot_init(self):
        '''Provide blank data to the animation.'''
        self.line.set_data([], [])
        return self.line,

    def update_plot(self, frame):
        '''Calculates and draws the new data.'''
        try:
            a_in = indataQ.popleft()
            mag = 20 * log10(abs(fft.rfft(a_in, n=args.fft_size) * 2 / args.buff_size))
            self.line.set_data(self.freq, mag)
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

def main():
    stream = audio_processor()
    stream.start_plot()
    while True:
        control = input("Enter 'q' to quit, 'l' to list devices, "
                        "or press enter to start: ")
        if control == 'q':
            exit()
        elif control == 'l':
            print(sd.query_devices())
            continue
        elif control == '':
            stream.start_stream()
        else:
            continue
        input("Press enter to stop")
        stream.stop_stream()

main()
