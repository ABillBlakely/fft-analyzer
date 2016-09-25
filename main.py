import sys

import sounddevice as sd

from argument_handler import ArgHandler
from fft_analyzer import AudioStream, FFTDisplay


args = ArgHandler(sys.argv)
# print(args)
# exit()
if args.list_devices:
    print(sd.query_devices())
    exit()


def main():
    stream = AudioStream(args)
    plot = FFTDisplay(args)
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
