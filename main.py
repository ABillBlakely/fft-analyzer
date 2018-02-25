from collections import deque

import numpy as np

import sounddevice as sd

import plotly.plotly as plotly
import plotly.tools as tls
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import sys


from argument_handler import ArgHandler

# Some aliases to make things readable.
LEFT = 0
RIGHT = 1

# The Queue where the input data will be stored.
# Declared in global scope for now.
indataQ = deque(maxlen=10)

a_in = np.array([0, 0])

current_unit = 'dBFS'

# Turn off numpy warning on divide by zero:
np.seterr(divide='ignore')


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
        freq_array = np.fft.rfftfreq(n=precision * self.args.buff_size,
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
        self.__init__(args)
        print('re-initialized.')
        return None

if __name__ == '__main__':

    # Parse and collect the input arguments
    args = ArgHandler(sys.argv)
    if args.list_devices:
        print(sd.query_devices())
        exit()

    stream = AudioStream(args)
    # output_signal_properties = stream.create_output_signal()
    # print('Output signal is freq:{} Hz'.format(output_signal_properties[0]))

    # Initialize the mag and frequency values.
    freq_axis = np.fft.rfftfreq(n=args.fft_size, d=(1 / args.sample_rate))
    mag_in_dB = np.zeros_like(freq_axis) - 150

    app = dash.Dash()

    app.layout = html.Div(id='Body', children=[
        html.H1(children="Plotly/Dash FFT analyzer"),

        html.Div(children='''
            Some sort of subtitle
            '''),

        html.Button('Start', id='start'),

        html.Button('Toggle Output', id='output_enable'),

        # Change to separate dropdown lists of inputs and outputs.
        html.Button('List Devices', id='list_devices'),

        dcc.Graph(id='frequency_plot'),

        dcc.Interval(id='interval', interval=100, n_intervals=0),

        html.Div(id='Average')
        ])

    @app.callback(
        dd.Output(component_id='Average', component_property='children'),
        [dd.Input(component_id='interval', component_property='n_intervals')])
    def average_display(nn):
        rms_avg = np.sqrt(np.mean(a_in**2))
        return 'RMS Average: {:.5} {unit}'.format(20*np.log10(rms_avg), unit=current_unit)

    @app.callback(
        dd.Output(component_id='list_devices', component_property='value'),
        [dd.Input(component_id='list_devices', component_property='n_clicks')])
    def list_devices(nn):
        print(sd.query_devices())
        return ''

    @app.callback(
        dd.Output(component_id='start', component_property='value'),
        [dd.Input(component_id='start', component_property='n_clicks')])
    def start_stop(nn):
        if stream.audio_stream.active:
            stream.stop_stream()
            print('Stream Stopped')
            return 'Start'
        else:
            stream.start_stream()
            print('Stream started')
            return 'Stop'

    @app.callback(
        dd.Output(component_id='frequency_plot', component_property='figure'),
        [dd.Input(component_id='interval', component_property='n_intervals')])
    def update_plot(nn):
        global mag_in_dB
        global a_in
        try:
            a_in = indataQ.popleft() * np.blackman(args.buff_size)
            mag_in_dB = 20 * np.log10(np.abs(
                        np.fft.rfft(a=a_in, n=args.fft_size)
                        * 2 / args.buff_size))
        except IndexError:
            pass
        return {'data': [{'x': freq_axis, 'y': mag_in_dB,
                          # 'type': 'line',
                          'name': 'channel_1'}],
                'layout': {'title': 'Magnitude vs. Frequency',
                           'xaxis': {
                                     'type': 'log',
                                     'title': 'Frequency [Hz]',
                                     'range': np.log10(args.xlims)
                                     },
                           'yaxis': {'range': args.ylims,
                                     'title': 'Magnitude [{unit}]'.format(unit=current_unit)
                                     }
                           }
                }

    app.run_server(debug=True)

    # while True:
    #     control = input("Enter 'q' to quit, 'l' to list devices, "
    #                     "'s' to change settings, "
    #                     "or press enter to start: ")
    #     if control == 'q':
    #         exit()
    #     elif control == 'l':
    #         print(sd.query_devices())
    #         continue
    #     elif control == 's':
    #         break
    #     elif control == '':
    #         stream.start_stream()
    #     else:
    #         continue

    #     while True:
    #         control = input("Press enter to stop, 't' to toggle output: ")
    #         if control == 't':
    #             output_status = stream.toggle_out()
    #             print('Output is {}'.format(output_status))
    #         elif control == '':
    #             stream.stop_stream()
    #             break
    #         else:
    #             continue

