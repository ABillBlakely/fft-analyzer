import sys

import sounddevice as sd

from argument_handler import ArgHandler
from fft_analyzer import AudioStream, FFTDisplay

if __name__ == '__main__':

    args = ArgHandler(sys.argv)
    # print(args)
    # exit()
    if args.list_devices:
        print(sd.query_devices())
        exit()

    stream = AudioStream(args)
    output_signal_properties = stream.create_output_signal()
    print('Output signal is freq:{} Hz'.format(output_signal_properties[0]))
    plot = FFTDisplay(args)
    plot.start_plot()

    while True:
        control = input("Enter 'q' to quit, 'l' to list devices, "
                        "'s' to change settings, "
                        "or press enter to start: ")
        if control == 'q':
            exit()
        elif control == 'l':
            print(sd.query_devices())
            continue
        elif control == 's':
            break
        elif control == '':
            stream.start_stream()
        else:
            continue

        while True:
            control = input("Press enter to stop, 't' to toggle output: ")
            if control == 't':
                output_status = stream.toggle_out()
                print('Output is {}'.format(output_status))
            elif control == '':
                stream.stop_stream()
                break
            else:
                continue

