import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from verbose import VerboseMessage as v

(MESSAGE_QTSERVER_LOG_HEX, MESSAGE_MAXSTUDIO_LOG_DEC, MESSAGE_MXTAPP_HEX) = range(3)
(MIN_REPORT_ID, MAX_REPORT_ID) = range(2)

class T5MsgReplayer(object):
    PARAMS = {
        'xres': 0,
        'yres': 0,
        'clear': 0xffff,    #bit value, 1 for clear after released
        'interval': 5,
        'finger': 10,
        'reportid': {6: [1, 1]}, #<Object>: <Min id>, <Max id>

        'linewidth': 8,
        'markersize': 12,
    }

    def __init__(self, xres=0, yres=0):
        pass

    @staticmethod
    def set_param(self, name, val):
        if name in self.PARAMS.keys():
            if name == 'reportid':
                try:
                    if len(val) == 2:
                        self.PARAMS['reportid'][val[0]] = [val[1], val[1]]
                        return
                    elif len(val) == 3:
                        self.PARAMS['reportid'][val[0]] = [val[1], val[2]]
                        return
                    else:
                        raise ValueError(name, val)
                except:
                    raise ValueError(name, val)
            else:
                if isinstance(val, type(self.PARAMS[name])):
                    self.PARAMS[name] = val
                    return

        v.msg(v.WARN, 'Unhandled param \'{:s}\': '.format(name), val)

    def get_param(self, name):
        if name in self.PARAMS.keys():
            return self.PARAMS[name]

        return

    def get_report_id(self, object_id):
        for key, val in self.PARAMS['reportid'].items():
            if key == object_id:
                v.msg(v.DEBUG2, "Found T{:d} report id '{:d}-{:d}'".format(object_id, *val))
                return val

    def get_min_report_id(self, object_id):
        val = self.get_report_id(object_id)
        if val is not None:
            v.msg(v.DEBUG2, "Found T{:d} min report id '{:d}'".format(object_id, val[0]))
            return val[0]

        raise ValueError('No found T{:d} report id'.format(object_id))

    def is_object_report_id(self, object_id, rid):
        ra = self.get_report_id(object_id)
        if ra is not None:
            if rid >= ra[MIN_REPORT_ID] and rid <= ra[MAX_REPORT_ID]:
                return True

        return False

    def update_line(self, num, ax, txtbox, data, line, xdata, ydata):
        v.msg(v.DEBUG, num)

        if num >= len(data):
            raise ValueError("Frame No {:d} over data len {:d}".format(num, len(data)))

        #fig.patch.set_facecolor('black')
        msg = data.iloc[num]
        v.msg(v.DEBUG2, msg.name)
        v.msg(v.DEBUG, tuple(msg.index))
        v.msg(v.DEBUG, tuple(msg.values))
        if isinstance(msg.name, datetime.datetime):
            timetxt = msg.name.strftime("%H:%M:%S:%f")
        else:
            timetxt = msg.name

        v.msg(v.DEBUG2, timetxt)
        txtbox.set_text(timetxt)
        #txtbox.draw(ax)
        #event = msg['tchstatus'] & 0xf
        #type = (msg['tchstatus'] >> 4) & 0x7
        reportid = msg['reportid']

        if self.is_object_report_id(6, reportid):
            v.msg(v.INFO, "T6 message")

            if msg['tchstatus']:
                ax.patch.set_facecolor('blue')
            else:
                ax.patch.set_facecolor('white')
        elif self.is_object_report_id(100, reportid):
            v.msg(v.INFO, "T100 message")

            detect = (msg['tchstatus'] >> 7) & 0x1
            x = msg['x0'] + msg['x1'] * 256
            y = msg['y0'] + msg['y1'] * 256
            id = reportid - self.get_min_report_id(100)
            if id > len(line) or id < 0:
                return line

            v.msg(v.INFO, "id {:d} x {:d} y {:d}".format(id, x, y))

            if detect:
                if not len(xdata[id]):
                    pass
                xdata[id].append(x)
                ydata[id].append(y)
            else:
                mask = self.get_param('clear')
                if mask & (1 << id):
                    del xdata[id][:]
                    del ydata[id][:]
                pass

            line[id].set_data([xdata[id], ydata[id]])

            v.msg(v.DEBUG, zip(xdata[id], ydata[id]))
            v.msg(v.DEBUG, line[id])

        return tuple(line)

    def load(self, path, datatype):

        df = pd.DataFrame()

        if not os.path.exists(path):
            v.msg(v.ERR, "File not exist: '{:s}'".format(path))
            return df

        try:
            if datatype == MESSAGE_MXTAPP_HEX:
                v.msg(v.INFO, 'MESSAGE_MXTAPP_HEX')
                dformat = (2, 8, 16)
                col = ('', '', 'reportid', 'tchstatus', 'x0', 'x1', 'y0', 'y1', '', '', '', '')
                df = pd.read_csv(path, sep=',', skiprows=1, names=col, dtype=str)
            else:   #   MESSAGE_QTSERVER_LOG_HEX / MESSAGE_MAXSTUDIO_LOG_DEC
                if datatype == MESSAGE_MAXSTUDIO_LOG_DEC:
                    v.msg(v.INFO, 'MESSAGE_MAXSTUDIO_LOG_DEC')
                    dformat = (0, 7, 10)
                    col = ['datetime', 'object', 'reportid', 'tchstatus', 'x0', 'x1', 'y0', 'y1', '', '', '', '', '']
                else:
                    v.msg(v.INFO, 'MESSAGE_QTSERVER_LOG_HEX')
                    dformat = (0, 6, 16)
                    col = ['datetime', 'reportid', 'tchstatus', 'x0', 'x1', 'y0', 'y1', '', '', '', '', '']

                df = pd.read_csv(path, sep=',',  skiprows=1, names=col, dtype=str,
                                 parse_dates=["datetime"], date_parser=lambda x: pd.to_datetime(x, format="%H:%M:%S %f"),
                                 index_col="datetime")
        except Exception as e:
            v.msg(v.ERR, "Unable to parse file, error: '{:s}'".format(str(e)))
            return df

        df.dropna(axis=1, how='all', inplace=True)
        #df.fillna()
        #convert data
        for i in range(*dformat[:2]):
            #df[col[i]] = df[col[i]].astype(str).apply(lambda x: int(x, 16))
            df.iloc[:, i] = df.iloc[:, i].apply(lambda x: int(x, dformat[2]))

        v.msg(v.DEBUG, df.index)
        v.msg(v.DEBUG, df.columns)
        v.msg(v.DEBUG, df)

        return df

    def get_resolution_info(self):

        xres, yres = self.PARAMS['xres'], self.PARAMS['yres']
        if xres and yres:
            return xres, yres

        v.msg(v.WARN, 'Please input the Resolution, format is <x, y>: ')
        try:
            raw = input('input res: ').split(',')
            if len(raw) == 2:
                xres, yres = list(map(int, raw))
        except:
            v.msg(v.ERR, 'Input value error')

        if not xres or not yres:
            raise ValueError('Invalide Resolution : {:d},{:d}'.format(xres, yres))

        return xres, yres

    def replay(self, filename, datatype):

        data = self.load(filename, datatype)
        print(type(datatype))
        if data.empty:
            v.msg(v.ERR, "Couldn't load the file data path='{:s}' type='{:d}'".format(filename, datatype))
            return

        xres, yres = self.get_resolution_info()
        fig1 = plt.figure(figsize=(xres/100, yres/100))
        ax = fig1.add_subplot(111)
        #ax.patch.set_facecolor('black')
        txtbox = ax.text(3, 8, 'boxed italics text in data coords', style='italic',
                bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

        colors = ['ro', 'g^', 'b^', 'c^', 'm^', 'yo', 'rs', 'gs', 'bs', 'ms']
        finger_count = self.get_param('finger')
        plt_parm = []
        xdata = []
        ydata = []
        for i in range(finger_count):
            plt_parm.extend([[], [], colors[i % len(colors)]])      # x, y, color
            xdata.append([])
            ydata.append([])

        lines = plt.plot(*tuple(plt_parm))
        for line in lines:
            line.set_linewidth(self.get_param('linewidth'))
            line.set_markersize(self.get_param('markersize'))

        plt.xlim(0, xres - 1)
        plt.ylim(0, yres - 1)
        plt.xlabel('x')
        plt.title('test')

        line_ani = FuncAnimation(fig1, self.update_line, len(data), fargs=(ax, txtbox, data, lines, xdata, ydata),
                                           interval=self.get_param('interval'), blit=True, repeat=False)
        plt.show()
