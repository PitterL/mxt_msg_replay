import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import datetime
from verbose import VerboseMessage as v

(MESSAGE_QTSERVER_LOG_HEX, MESSAGE_MAXSTUDIO_LOG_DEC, MESSAGE_MXTAPP_HEX) = range(3)
(MIN_REPORT_ID, MAX_REPORT_ID) = range(2)
#(T100_MIN_REPORT_ID, T100_MAX_REPORT_ID) = (0x31, 0x40)
#(T6_MIN_REPORT_ID, T6_MAX_REPORT_ID) = (1, 1)

#file_attribute = ("log\\gen_messageprocessor_t5_20170531_151514.csv", MESSAGE_T5_LOG_DEC)

class T5MsgReplayer(object):
    PARAMS = {
        'xres': 0,
        'yres': 0,
        'clear': True,
        'interval': 5,
        'finger': 10,
        'reportid': {6: [1, 1]}, #<Object>: <Min id>, <Max id>
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
                if type(val) is type(self.PARAMS[name]):
                    self.PARAMS[name] = val
                    return

        v.msg(v.WARN, 'Unhandled param \'{:s}\': '.format(name), val)

    def get_report_id(self, object_id):
        for key, val in self.PARAMS['reportid'].items():
            if key == object_id:
                return tuple(val)
            return

    def get_min_report_id(self, object_id):
        val = self.get_report_id(object_id)

        if val is not None:
            return val[0]

        raise ValueError('No found object {:d} report id'.format(object_id))

    def is_object_report_id(self, object_id, rid):
        ra = self.get_report_id(object_id)
        if ra is not None:
            if rid >= ra[MIN_REPORT_ID] and rid <= ra[MAX_REPORT_ID]:
                return True

        return False

    def update_line(self, num, ax, txtbox, data, line, xdata, ydata):

        if num >= len(data):
            raise ValueError("Frame No {:d} over data len {:d}".format(num, len(data)))

        #fig.patch.set_facecolor('black')
        msg = data.iloc[num]
        v.msg(v.DEBUG2, msg.name)
        v.msg(v.DEBUG2, msg)
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

            id = msg['reportid'] - self.get_min_report_id(100)
            if id > len(line) or id < 0:
                return line

            v.msg(v.INFO, "id {:d} x {:d} y {:d}".format(id, x, y))

            if detect:
                if not len(xdata[id]):
                    pass
                xdata[id].append(x)
                ydata[id].append(y)
            else:
                if self.PARAMS['clear']:
                    del xdata[id][:]
                    del ydata[id][:]
                pass

            line[id].set_data([xdata[id], ydata[id]])

            v.msg(v.DEBUG, zip(xdata[id], ydata[id]))
            v.msg(v.DEBUG, line[id])

        return tuple(line)

    def load(self, path, type):

        file = os.path.join('.', path)
        try:
            if type == MESSAGE_MXTAPP_HEX:
                col = ('', '', 'reportid', 'tchstatus', 'x0', 'x1', 'y0', 'y1', '', '', '', '')
                df = pd.read_csv(file, sep=',', header=0, names=col, engine='python')
            else:   #MESSAGE_QTSERVER_LOG_HEX / MESSAGE_MAXSTUDIO_LOG_DEC

                timeformat = "%H:%M:%S %f"
                if type == MESSAGE_MAXSTUDIO_LOG_DEC:
                    col = ['datetime', 'object', 'reportid', 'tchstatus', 'x0', 'x1', 'y0', 'y1', '', '', '', '', '']
                else:
                    col = ['datetime', 'reportid', 'tchstatus', 'x0', 'x1', 'y0', 'y1', '', '', '', '', '']
                df = pd.read_csv(file, sep=',', parse_dates=["datetime"], skiprows=1,
                                 date_parser=lambda x: pd.to_datetime(x, format=timeformat),
                                 index_col="datetime", names=col, engine='python').dropna(axis=1)
            v.msg(v.DEBUG, df.index)
            v.msg(v.DEBUG, df.columns)
            v.msg(v.DEBUG, df)
        except Exception as e:
            v.msg(v.ERR, "Unable to parse file, error: '{:s}'".format(str(e)))
            raise e

        if type == MESSAGE_MXTAPP_HEX:
            for i in range(6):
                df[col[i + 2]] = df[col[i + 2]].astype(str).apply(lambda x: int(x, 16))
        elif type == MESSAGE_QTSERVER_LOG_HEX:
            for i in range(6):
                df[col[i + 1]] = df[col[i + 1]].astype(str).apply(lambda x: int(x, 16))
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

    def replay(self, file, type):
        xres, yres = self.get_resolution_info()
        finger_count = self.PARAMS['finger']
        fig1 = plt.figure(figsize=(xres/100, yres/100))
        ax = fig1.add_subplot(111)
        #ax.patch.set_facecolor('black')
        txtbox = ax.text(3, 8, 'boxed italics text in data coords', style='italic',
                bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
        para = []
        xdata = []
        ydata = []
        l = []
        data = self.load(file, type)

        colors = ['ro', 'g^', 'b^', 'c^', 'm^', 'yo', 'rs', 'gs', 'bs', 'ms']
        for i in range(finger_count):
            para.extend([[], [], colors[i % len(colors)]]) # x, y, color
            xdata.append([])
            ydata.append([])
            l.append(None)

        line = plt.plot(*tuple(para))
        for i in range(finger_count):
            l[i] = line[i]
            l[i].set_linewidth(8)
            l[i].set_markersize(12)

        plt.xlim(0, xres - 1)
        plt.ylim(0, yres - 1)
        plt.xlabel('x')
        plt.title('test')
        line_ani = FuncAnimation(fig1, self.update_line, len(data), fargs=(ax, txtbox, data, l, xdata, ydata),
                                           interval=self.PARAMS['interval'], blit=True, repeat=False)
        plt.show()
