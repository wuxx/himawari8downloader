import sys
import os
import time
import getopt
import json
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
from dateutil import tz

conf ={
    'last_refresh_url': 'http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json',  # latest photo
    'img_url_pattern': 'http://himawari8-dl.nict.go.jp/himawari8/img/D531106/%id/550/%s_%i_%i.png',    # scale, time, row, col
    'scale': 16,     # 1, 2, 4, 8, 16, 20.  Width and height are both 550*scale
}

def usage():
    print '-h help  \n' \
          '-s scale \n' \
          '-t time  \n' \
          ''
    sys.exit(0)

# Convert time
def utc2local(utc):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)

def local2utc(local):
    from_zone = tz.tzlocal()
    to_zone   = tz.tzutc()
    return local.replace(tzinfo=from_zone).astimezone(to_zone)


def download(args):
    scale = args['scale']
    png = Image.new('RGB', (550*scale, 550*scale))
    for row in range(scale):
        for col in range(scale):
            print 'Downloading %i of %i ...' % (row*scale + col + 1, scale*scale)
            strtime = args['time'].strftime("%Y/%m/%d/%H%M%S")
            url = conf['img_url_pattern'] % (args['scale'], strtime, row, col)
            print "url: %s" % url
            r = requests.get(url)
            tile = Image.open(BytesIO(r.content))
            png.paste(tile, (550 * row, 550 * col, 550 * (row + 1), 550 * (col + 1)))

    print 'Download over, save to file %s' % args['filepath']
    png.save(args['filepath'], "PNG")


def get_last_time():
    r = requests.get(conf['last_refresh_url'])
    resp = json.loads(r.text)
    print "resp date: [%s]" % resp['date']
    last_refresh_time = datetime.strptime(resp['date'], '%Y-%m-%d %H:%M:%S')
    return last_refresh_time


def get_last_image(args):
    cwd = os.getcwd()
    localdate = time.strftime("%Y%m%d", time.localtime())
    print "cwd: %s; localdate: %s " % (cwd, localdate)
    dirpath = "%s/%s" %(cwd, localdate)
    if os.path.exists(dirpath):
        pass
        #print "dirpath %s already created." % dirpath
    else:
        print "path not exist."
        os.mkdir(dirpath)

    if not args.has_key('time'):
        args['time'] = get_last_time()

    #print "last_refresh_time utc: %s; time local: %s" % (args['time'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    args['dirpath'] = dirpath

    utctime   = args['time'].strftime("%Y/%m/%d/%H%M%S").replace('/', '')
    localtime = utc2local(args['time']).strftime("%Y/%m/%d/%H%M%S").replace('/', '')

    filepath = "%s/%s.png" % (args['dirpath'], localtime)
    args['filepath'] = filepath

    print "last_refresh_time: utc: %s; local: %s" %(utctime, localtime)

    if os.path.exists(args['filepath']):
        print "%s already exist. " % args['filepath']
    else:
        print 'output[%s] scale[%d]' %(args['filepath'], args['scale'])

        print "########################%s start" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        download(args)
        print "########################%s end" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


if __name__ == '__main__':
    args = {'scale': 1}
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hs:t:", ['help', "scale=", "time="])
        for name, value in options:
            if name in ('-h', '--help'):
                usage()
            elif name in ('-s', '--scale'):
                args['scale'] = int(value)
            elif name in ('-t', '--time'):
                args['time']  = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except getopt.GetoptError:
        usage()        

    #print args
    get_last_image(args)
