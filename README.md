Program for replay T100 point from t5 message, support log files from Qtserver/Maxstudio/mxt-app



usage: t5replay [-h] [--version] [-f [File]] [-d {0,1,2}] [-x XRES] [-y YRES]
                [-i INTERVAL] [--finger FINGER] [-r REPORTID [REPORTID ...]]
                [-cl CLEAR] [-v {0,1,2,3,4}]


				=========================
Tools for replay maxTouch t5 message

optional arguments:
  -h, --help            show this help message and exit
  --version             show version
  -f [File], --filename [File]
                        where the t5 message log file will be load (default: )
  -d {0,1,2}, --datatype {0,1,2}
                        message type: <1> QTServer(default) <2> Maxstudio <3>
                        Mxt-app (default: 0)
  -x XRES, --xres XRES  x resolution (default: 0)
  -y YRES, --yres YRES  y resolution (default: 0)
  -i INTERVAL, --interval INTERVAL
                        replaying interval for each frame (default: 10)
  --finger FINGER       max finger count support (default: 10)
  -r REPORTID [REPORTID ...], --reportid REPORTID [REPORTID ...]
                        <n> <min> <max>: T<n> report <min id> <max id>
                        (default: None)
  -cl CLEAR, --clear CLEAR
                        Mask value, whether the piont in canvas will be clean
                        when release(for each bit, 1 clear, 0 not clear
                        (default: 0xffff)
  -v {0,1,2,3,4}, --verbose {0,1,2,3,4}
                        set debug verbose level[0-5] (default: 1)
