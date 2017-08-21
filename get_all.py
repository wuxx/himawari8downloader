import sys
import os
import time
import getopt
import json
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime,timedelta
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
    print "resp date: %s" % resp['date']
    last_refresh_time = datetime.strptime(resp['date'], '%Y-%m-%d %H:%M:%S')
    return last_refresh_time


def get_last_image(args):
    print "scale: %d" % args['scale']
    cwd = os.getcwd()
    localdate = time.strftime("%Y%m%d", time.localtime())
    print "cwd: %s; localdate: %s " % (cwd, localdate)
    dirpath = "%s/%s" %(cwd, localdate)
    if os.path.exists(dirpath):
        print "dirpath %s already created." % dirpath
    else:
        print "path not exist."
        os.mkdir(dirpath)


    last_refresh_time = get_last_time()

    print "last_refresh_time utc: %s; time local: %s" % (last_refresh_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    if not args.has_key('time'):
        args['time'] = last_refresh_time

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

        print "%s start" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        download(args)
        print "%s end" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

if __name__ == '__main__':
    last_utctime = get_last_time();
    print "last_utctime: %s" % last_utctime
    localtime = utc2local(last_utctime)
    #print localtime

    #print datetime.now()
    #print ((datetime.now()-timedelta(minutes=0)).strftime("%Y-%m-%d %H:%M"))
    #print ((datetime.now()-timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M"))
    #print "\n"
    #print ((localtime-timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M"))

    #print local2utc(localtime-timedelta(minutes=10))

    local_start = datetime(localtime.year, localtime.month, localtime.day, 0, 0, 0)
    local_time  = datetime(localtime.year, localtime.month, localtime.day, 
                           localtime.hour, localtime.minute, localtime.second)
    #print local_time
    #print local_start
    #print (local_time - local_start).seconds
    count = ((local_time - local_start).seconds / (60 * 10)) + 1 #every 10 mins
    for i in range (count):
        local_time = ((localtime-timedelta(minutes=(10 * i))).strftime("%Y-%m-%d %H:%M:%S"))
        utc_time   = local2utc(localtime-timedelta(minutes=(10 * i))).strftime("%Y-%m-%d %H:%M:%S")
        print "local_time: [%s]; utc_time: [%s];" % (local_time, utc_time)
        os.system("python himawari8downloader.py -s 1 -t \"%s\"" % (utc_time));

    #print (localtime-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M")
