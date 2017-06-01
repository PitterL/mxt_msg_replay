import os
import sys
import argparse
import t5_parser as t5p
from verbose import VerboseMessage as v

def runstat(args=None):
    parser = parse_args(args)
    aargs = args if args is not None else sys.argv[1:]
    args = parser.parse_args(aargs)
    print(args)

    if not args.filename:
        parser.print_help()
        return

    v.set(args.verbose)

    t5 = t5p.T5MsgReplayer()

    if args.xres:
        t5.set_param(t5, 'xres', args.xres)
    if args.yres:
        t5.set_param(t5, 'yres', args.yres)
    if args.clear:
        t5.set_param(t5, 'clear', args.clear)
    if args.interval:
        t5.set_param(t5, 'interval', args.interval)
    if args.finger:
        t5.set_param(t5, 'finger', args.finger)
    if args.reportid:
        t5.set_param(t5, 'reportid', args.reportid)

    path = args.filename
    if path:
        if os.path.exists(path):
            t5.replay(path, args.log)
        else:
            v.msg(v.WARN, 'Un-exist file name \'{:s}\''.format(path))

def parse_args(args=None):

    parser = argparse.ArgumentParser(
        prog='t5replay',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Tools for replay maxTouch t5 message')

    parser.add_argument('--version',
                        action='version', version='%(prog)s v1.0.0',
                        help='show version')

    parser.add_argument('-f', '--filename',
                        nargs='?',
                        default='',
                        metavar='File',
                        help='where the t5 message log file will be load')

    parser.add_argument('-l', '--log', required=False,
                        choices=range(3),
                        nargs=1,
                        default=0,
                        help='message type: <1> QTServer(default) <2> Maxstudio <3> Mxt-app')

    parser.add_argument('-x', '--xres', required=False,
                        type=int,
                        default=0,
                        help='x resolution')

    parser.add_argument('-y', '--yres', required=False,
                        type=int,
                        default=0,
                        help='y resolution')

    parser.add_argument('-i', '--interval', required=False,
                        type=int,
                        default=5,
                        help='replaying interval for each frame')

    parser.add_argument('--finger', required=False,
                        type=int,
                        default=10,
                        help='max finger count support')

    parser.add_argument('-r', '--reportid', required=False,
                        type=int,
                        nargs='+',
                        help='<n> <min> <max>: T<n> report <min id> <max id>')

    parser.add_argument('-cl', '--clear', required=False,
                        action='store_true',
                        help='Whether the piont in canvas will be clean when release')

    parser.add_argument('-v', '--verbose',
                        type=int,
                        choices=range(5),
                        default=1,
                        help='set debug verbose level[0-5]')

    return parser

cmd = r"-x 720 -y 1367 -v 3 -r 100 46 55 -f log\gen_messageprocessor_t5_20170531_151514.csv".split()
#cmd =r"t5replay -h".split()
#cmd = None
if __name__ == "__main__":

    runstat(cmd)
