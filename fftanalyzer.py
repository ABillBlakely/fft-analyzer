
import argparse
import sounddevice as sd
from collections import deque
from numpy import abs, fft, log10, zeros_like
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
from time import sleep

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

if args.list_devices == True:
    print(sd.query_devices())
    exit()



# The Queue where the input data will be stored.
indataQ = deque(maxlen=10)

class plot_controls():

    def __init__(self):
        # Determine the frequencies the dfft calculates at.
        self.freq = fft.rfftfreq(args.fft_size, 1 / args.sample_rate)
        self.mag = zeros_like(self.freq)
        # Setup the display:
        self.fig = figure(title='Spectrum',
                     # tools='crosshair',
                     x_axis_label='Freq (Hz)', x_axis_type = 'log',
                     y_axis_label='Mag (dB)')
        self.data = self.fig.circle(self.freq, self.mag, size=2)
        # self.session = push_session(curdoc())
        print('Plot initialized.')

    def start_plot(self):

        def plot_callback():
            self.mag += 0.1
            newdata = {'x':self.freq, 'y':self.mag}
            self.data.data_source.data = newdata
        curdoc().add_root(column(self.fig))
        curdoc().add_periodic_callback(plot_callback, 1000)
        print('Plot started.')

    def stop_plot(self):
        pass

class stream_controls():

    def __init__(self):

        # Some aliases to make things readable.
        LEFT = 0
        RIGHT = 1

        def audio_callback(indata, outdata, frames, time, status):
                '''Called by audio stream for each new buffer.'''
                indataQ.append(indata[::, LEFT])
                outdata.fill(0)

        self.audio_stream = sd.Stream(callback=audio_callback,
                                      channels=2,
                                      samplerate=args.sample_rate,
                                      blocksize=args.buff_size,
                                      clip_off=True,
                                      dither_off=args.dither)
        print('Stream initialized.')

    def start_stream(self):
        self.audio_stream.start()
        while self.audio_stream.stopped == True:
            pass
        print('Stream started.' )

    def stop_stream(self):
        self.audio_stream.stop()

    def close_stream(self):
        self.audio_stream.close()

def main():
    # stream = stream_controls()
    # stream.start_stream()
    plot = plot_controls()
    plot.start_plot()
    # w = input('Enter to kill...')
    # stream.close_stream()
    # plot.stop_plot()
    # stream.start_plot()


def loop():
    while True:
        control = input("Enter 'q' to quit, 'l' to list devices")

        if control == 'q':
            exit()
        elif control == 'l':
            print(sd.query_devices())
            continue

        else:
            continue

main()
loop()
