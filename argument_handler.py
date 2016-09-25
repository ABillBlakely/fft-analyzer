import argparse

description = '''A realtime fft analyzer for python.'''


def ArgHandler(argv):

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-b', '--buff-size', action='store',
                        type=int, metavar='SIZE',
                        default=4096, choices=[512, 1024, 2048, 4096],
                        help=('Buffer size of audio stream. '
                              'Available options are [%(choices)s]'))

    parser.add_argument('-d', '--dither', action='store_false',
                        help='Turn dithering on.')
                        # Beware double negative: toggles sound devices
                        # 'dither_off' so false here turns dithering on.

    parser.add_argument('-s', '--sample-rate', action='store',
                        type=int, metavar='RATE',
                        default=48000, choices=[44100, 48000, 88200, 96000],
                        help=('Sample rate used by device. '
                              'Not all choices can be used by all devices. '
                              'Default is %(default)s, '
                              'available choices are [%(choices)s].'))

    parser.add_argument('-l', '--list-devices', action='store_true',
                        help='View available devices for this computer.')

    parser.add_argument('-i', '--input-device',  action='store',
                        type=int, metavar='DEV_ID',
                        help=("Integer value of device to use for input, "
                              "see 'list-devices.'"))

    parser.add_argument('-o', '--output-device', action='store',
                        type=int, metavar='DEV_ID',
                        help=("Integer value of device to use for output, "
                              "see 'listdevices.'"))

    parser.add_argument('-f', '--fft-size', action='store',
                        type=int, metavar='SIZE',
                        default=16384,
                        choices=[4096, 8192, 16384, 32768, 65536, 131072],
                        help=('Select the size of the fft sample. '
                              'Default is %(default)s, '
                              'available choices are: [%(choices)s].'))

    parser.add_argument('-x', '--xlims', nargs=2, action='store',
                        type=int, metavar=('LOWER', 'UPPER'),
                        default=(20, 20000),
                        help=('Magnitude axis limits in dB. '
                              'Default is %(default)s.'))

    parser.add_argument('-y', '--ylims', nargs=2, action='store',
                        type=int, metavar=('LOWER', 'UPPER'),
                        default=(-150, 0),
                        help='Freq axis limits in Hz. Default is %(default)s.')

    args = parser.parse_args(argv[1:])
    return(args)
