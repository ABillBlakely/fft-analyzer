# FFT Analyzer

This project consists of some tests and experiments writing an audio analyzer using python. It is largely based on replicating the spectrum analyzer functionality of [Arta](http://artalabs.hr/), but will eventually have some features I found lacking from arta during my testing of the Zinc Box. While ARTA's primary focus seems to be on testing speakers, this project is intended to focus on testing circuits directly in loopback.


## Recent

2016-9-26: Shifting focus from plotting to signal gen and analysis. Currently I can produce sine waves in program so now I need to measure THD and THD+N.


## Goals

In Approximate order of priority:

- [x] Display fft analysis of signals.
- [x] Generate sine wave.
- [ ] Calculate the THD and THD+N.
- [ ] Generate twin tone signals and calculate IMD.
- [ ] Generate noise signal and find frequency response.
- [ ] Determine SNR.

## Captains Log

- 2016-9-26: Back on matplotlib until work on a GUI begins. Bokeh expects all the data to be there when the plot is started, so while it might be possible to use, it is very difficult to use how I want. The program can now generate sine waves and organization is improved although not perfect.

- 2016-9-17: Nearly started from scratch again. Replacing the awful matplotlib library with bokeh, which so far seems pretty nice. Also improved code orginization and added an argument parser for some command line setting of options.

- 2016-6-20: Rebuilt from scratch replacing Pyaudio with sounddevices. Allows for using asio drivers with compiling pyaudio, and the API is a little nicer. Need to double check the math is correct, but will move on to generation of test tones for now. Following that a command line interface will be neccesary to control the increasing feature set.
