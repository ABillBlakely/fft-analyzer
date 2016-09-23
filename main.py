import sys

import sounddevice as sd

from argumentHandler import arg_handler
from fftanalyzer import audio_stream, fft_display


args = arg_handler(sys.argv)
# print(args)
# exit()
if args.list_devices is True:
    print(sd.query_devices())
    exit()


def main():
    stream = audio_stream(args)
    plot = fft_display(args)
    plot.start_plot()
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
