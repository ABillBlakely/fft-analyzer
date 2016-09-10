from numpy import fft


class args():
    def __init__(self):
        # FFT calculation parameters
        self.fftsize = 8192
        self.window = 'kaiser'

        # Sound device parameters
        self.Fs = 48000
        self.buffsize = 4096
        self.clipoff = True
        self.ditheroff = True

        # Graph display parameters
        self.freq_ax = fft.rfftfreq(self.fftsize, 1 / self.Fs)
        self.freq_lim = (20, self.Fs / 2)
        self.mag_lim = (-150, 0)

arg = args()
