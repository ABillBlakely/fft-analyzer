import numpy as np
import matplotlib.pyplot as plt
import pyaudio
import time
from timeit import timeit

def fftOfBuffer(audio_buffer, sample_rate, buffer_size, output_in_dB=True):
    """  Converts the audio_buffer to frequency domain."""
    freq_axis = np.linspace(0, sample_rate/2, buffer_size/2, endpoint=False)
    window = np.kaiser(buffer_size, 7)
    signal_freq = np.fft.rfft(audio_buffer * window) * 2 / buffer_size
    if output_in_dB is True:
        return(20 * np.log10(np.abs(signal_freq[:-1])), freq_axis)
    else:
        return(signal_freq[:-1], freq_axis)


class plotFFT:
    """Helper for drawing plots of fft data.

    Uses matplotlib to draw plots that update with every call
    to draw_plot."""

    def __init__(self, style='bmh'):
        plt.ion()
        plt.show()
        self.fig = plt.figure()
        self.plot = plt.subplot(111)
        self.style = style

    def draw_plot(self, signal_in_freq_domain, freq_axis):
        self.plot.cla()
        with plt.style.context(self.style):
            self.plot.semilogx(freq_axis, signal_in_freq_domain)
            self.plot.set_ylim(-120, 10)
            self.plot.set_xlim(20, 20000)
            plt.pause(0.001)

    def close(self):
        plt.close(self.fig)


sample_rate = 48000
buffer_size = 2048
channels = 1
byte_depth = 2  # Called width in pyaudio speak.

p = pyaudio.PyAudio()

# This creates a list of the possible hosts For now it prints their names.
available_hosts = []
for n in range(p.get_host_api_count()):
    available_hosts.append(p.get_host_api_info_by_index(n))
for host in available_hosts:
    print("Available audio drivers:", host['name'])

external_data = np.zeros(buffer_size, dtype=np.float32)


def audio_callback(in_data, buffer_size, time_info, status):
    """Called by the stream whenever a new buffer is available."""
    global external_data
    external_data = np.fromstring(in_data, dtype=np.float32)
    return(in_data, pyaudio.paContinue)

# Create and run the stream
audio_stream = p.open(rate=sample_rate,
                      channels=channels,
                      format=pyaudio.paFloat32,
                      frames_per_buffer=buffer_size,
                      input=True,
                      output=True,
                      input_device_index=None,
                      output_device_index=None,
                      stream_callback=audio_callback,
                      start=True,
                      )

plot0 = plotFFT()

if audio_stream.is_active() is True:
    # time.sleep(1)
    for n in range(20):
        fftOfBuffer(external_data, sample_rate, buffer_size)
        sig_freq, freq_axis = fftOfBuffer(external_data,
                                          sample_rate,
                                          buffer_size)
        plot0.draw_plot(sig_freq, freq_axis)
        RMS_voltage = np.sqrt(np.sum(external_data ** 2) / buffer_size)
        print("RMS level (dB):", 20 * np.log10(RMS_voltage))

plot0.close()       
audio_stream.close()
print("all done")
print(exit())