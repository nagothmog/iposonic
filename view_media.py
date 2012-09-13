#
# Views for downloading songs
#
#
import os
import sys
import subprocess

from flask import request, send_file, Response
from webapp import iposonic, app
from iposonic import IposonicException, SubsonicProtocolException, SubsonicMissingParameterException
from mediamanager import MediaManager, StringUtils, UnsupportedMediaError

#
# download and stream
#


@app.route("/rest/stream.view", methods=['GET', 'POST'])
def stream_view():
    """@params
        - id=1409097050
        - maxBitRate=0 TODO

    """
    (u, p, v, c, f, callback) = map(
        request.args.get, ['u', 'p', 'v', 'c', 'f', 'callback'])
        
    (eid, maxBitRate) = map(request.args.get, ['id', 'maxBitRate'])

    print("request.headers: %s" % request.headers)
    if not eid:
        raise SubsonicProtocolException(
            "Missing required parameter: 'id' in stream.view")
    info = iposonic.get_entry_by_id(eid)
    path = info.get('path', None)
    assert path, "missing path in song: %s" % info

    def change_bitrate(maxBitRate, info):
        try:
            return int(maxBitRate) < info.get('bitRate')
        except:
            print "sending unchanged"
            return False
            
    print "actual - bitRate: " , info.get('bitRate')
    assert os.path.isfile(path), "Missing file: %s" % path
    if change_bitrate(maxBitRate, info):
        return Response(_downsample_mp3(path, maxBitRate), direct_passthrough = True)
    print "sending static file: %s" % path
    return send_file(path)
    raise IposonicException("why here?")

def _downsample_mp3(path, maxBitRate):
    """Transcode mp3 files reducing the bitrate."""
    cmd = ["/usr/bin/lame" , "-B",  maxBitRate, path, "-"]
    print "generate(): %s" % cmd
    srcfile = subprocess.Popen(cmd, stdout = subprocess.PIPE) 
    while True:
        data = srcfile.stdout.read(4096)
        if not data:
            break
        print
        yield data

@app.route("/rest/download.view", methods=['GET', 'POST'])
def download_view():
    """@params ?u=Aaa&p=enc:616263&v=1.2.0&c=android&id=1409097050&maxBitRate=0

    """
    if not 'id' in request.args:
        raise SubsonicProtocolException(
            "Missing required parameter: 'id' in stream.view")
    info = iposonic.get_entry_by_id(request.args['id'])
    assert 'path' in info, "missing path in song: %s" % info
    if os.path.isfile(info['path']):
        return send_file(info['path'])
    raise IposonicException("why here?")


@app.route("/rest/scrobble.view", methods=['GET', 'POST'])
def scrobble_view():
    """Add song to last.fm"""
    (u, p, v, c, f, callback) = map(
        request.args.get, ['u', 'p', 'v', 'c', 'f', 'callback'])

    return request.formatter({})


@app.route("/rest/setRating.view", methods=['GET', 'POST'])
def set_rating_view():
    (u, p, v, c, f, callback) = map(
        request.args.get, ['u', 'p', 'v', 'c', 'f', 'callback'])
    (eid, rating) = map(request.args.get, ['id', 'rating'])
    if not rating:
        raise SubsonicMissingParameterException(
            'rating', sys._getframe().f_code.co_name)
    if not eid:
        raise SubsonicMissingParameterException(
            'id', sys._getframe().f_code.co_name)
    iposonic.update_entry(eid, {'userRating': 5})
    return request.formatter({})


@app.route("/rest/getLyrics.view", methods=['GET', 'POST'])
def get_lyrics_view():
    raise NotImplementedError("WriteMe")
