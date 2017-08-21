import sys
import os
import time
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


# Convert time
def utf2local(utc):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


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


def get_last_image(scale=16):
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
    args = {'time': last_refresh_time}
    args['dirpath'] = dirpath

    utftime   =            args['time'].strftime("%Y/%m/%d/%H%M%S").replace('/', '')
    localtime = utf2local(args['time']).strftime("%Y/%m/%d/%H%M%S").replace('/', '')

    filepath = "%s/%s.png" % (args['dirpath'], localtime)
    args['filepath'] = filepath
    args['scale']   = scale

    print "last_refresh_time: utf: %s; local: %s" %(utftime, localtime)

    if os.path.exists(args['filepath']):
        print "%s already exist. " % args['filepath']
    else:
        print 'output[%s] scale[%i]' %(args['filepath'], scale)
        download(args)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        get_last_image()
    elif len(sys.argv) == 2:
        get_last_image()
    elif len(sys.argv) == 3:
        get_last_image(scale=int(sys.argv[2]))
