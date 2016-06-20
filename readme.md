# FFT Analyzer

This is some test and experiments with writing an audio analyzer using python. It is largely based on replicating the spectrum analyzer functionality of [Arta](http://artalabs.hr/), but will eventually have some features I found lacking from arta during my testing of the Zinc Box. While ARTA's primary focus seems to be on testing speakers, this project is intended to focus on testing circuits directly in loopback.


## Goals
In Approximate order of priority:

- [x] Display fft analysis of signals.
- [ ] Generate sine wave and calculate the THD and THD+N.
- [ ] Generate twin tone signals and calculate IMD.
- [ ] Generate noise signal and find frequency response.
- [ ] Determine SNR.

## Captains Log

- 2016-6-20: Rebuilt from scratch replacing Pyaudio with sounddevices. Allows for using asio drivers with compiling pyaudio, and the API is a little nicer. Need to double check the math is correct, but will move on to generation of test tones for now. Following that a command line interface will be neccesary to control the increasing feature set.