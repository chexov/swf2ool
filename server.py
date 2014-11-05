#!/usr/bin/env python

import os
import shutil
import uuid
import subprocess
import urllib2


from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from flask import abort

app = Flask(__name__)

def streamdir(streamid):
    return streamid + "/"


def hasFrames(streamid):
    sdir = streamdir(streamid)
    return len(filter(lambda f: f.endswith('.png'), os.listdir(sdir)))


@app.route("/crossdomain.xml")
def cdxml():
    return app.send_static_file('crossdomain.xml')


@app.route("/upload/<streamid>", methods=["POST"])
def savepng(streamid):
    totalFrames = int(request.headers["Frames-Total"])
    frame = int(request.headers["Frame"])
    sdir=streamdir(streamid)

    if (not os.path.isdir(sdir)):
        os.mkdir(sdir)

    outfn = (streamid + "/img%0" + str(len(str(totalFrames))) + "d") % (frame,) + ".png"
    with open(outfn, "a") as png:
        png.write(request.data)

    hf = hasFrames(streamid)
    print("=== got frame {0} from {1}; has {2}".format(frame, totalFrames, hf))

    if (hf == totalFrames and not os.path.isfile(sdir + "out.mp4")):
        check_and_render(streamid, totalFrames)

    return 'ok'


@app.route("/cdn/<streamid>/mp4")
def sendstaticvideo(streamid):
    return send_file(streamdir(streamid) + "out.mp4")


@app.route("/api/checkandrender/<streamid>/<totalFrames>")
def check_and_render(streamid, totalFrames):
    sdir=streamdir(streamid)
    hf = hasFrames(streamid)
    print("=== {streamid} -- has {framesHas}, total {totalFrames}".format(streamid=streamid, framesHas=hf, totalFrames=totalFrames))
    if (hf == totalFrames):
        print "THEEND for " + streamid

        cmd = "../ffmpeg -framerate 30 -i img%03d.png -c:v libx264 -pix_fmt yuv420p out.mp4"
        print cmd
        subprocess.call(cmd, cwd=streamid, shell=True)
        return True
    else:
        return False


@app.route("/proxy/<path:url>")
def proxy(url):
    url += '?' + '&'.join([arg + "=" + request.args[arg] for arg in request.args.keys()])
    print url

    r = urllib2.urlopen(url)
    return send_file(r, mimetype=r.headers.get('content-type'))


@app.route("/render/<streamid>")
def start_render(streamid):
    url = "/Ssswf.swf?posturl=/upload/" + streamid
    url += "&swf=about.swf&frames=364"
    url += ''.join(["&" + arg + "=" + request.args[arg] for arg in request.args.keys()])

    #TODO: open flash player
    return '<html><body><a href="{0}">ssswf</a></body></html>'.format("/static"+ url)


@app.route("/")
def collect_data():
    return render_template("collect_data.html", streamid=uuid.uuid1().hex)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8043)

