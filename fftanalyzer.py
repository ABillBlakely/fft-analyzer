from functools import partial
from time import sleep

import sounddevice as sd
from bokeh.client import push_session
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from numpy import fft, zeros_like
from random import random
from tornado import gen


class plot_control:

    def __init__(self, args):


        # Determine the frequencies the dfft calculates at.
        self.freq = fft.rfftfreq(args.fft_size, 1 / args.sample_rate)
        self.mag = zeros_like(self.freq)
        # Setup the display:
        self.source = ColumnDataSource(data=dict(x=[1000], y=[1]))
        self.doc = curdoc()

        self.fig = figure(title='Spectrum',
                          # tools='crosshair',
                          x_axis_label='Freq (Hz)', x_axis_type='log',
                          y_axis_label='Mag (dB)',
                          x_range=[20, 20000], y_range=[-5, 5],)

        self.data = self.fig.circle(x='x', y='y', size=50,
                                    source=self.source)
        self.doc.add_root(self.fig)
        print('Plot initialized.')

    def plot_callback(self, newdata):
        self.source.stream(newdata)

    def update_plot(self):
        print('hey.')
        self.freq = self.frew
        self.mag = self.mag + 1
        newdata = {'x': self.freq, 'y': self.mag}
        self.doc.add_next_tick_callback(partial(self.plot_callback, newdata))

    def start_plot(self):
        # self.session.show(self.fig)
        pass

    def stop_plot(self):
        pass


class audio_interface:

    def __init__(self):
        pass

    def create_stream(self, args, indataQ):
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
        while self.audio_stream.stopped is True:
            pass
        print('Stream started.')

    def stop_stream(self):
        self.audio_stream.stop()

    def close_stream(self):
        self.audio_stream.close()
