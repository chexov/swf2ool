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

app = Flask(__name__)


@app.route("/crossdomain.xml")
def cdxml():
    return app.send_static_file('crossdomain.xml')


@app.route("/upload/<streamid>", methods=["POST"])
def savepng(streamid):
    totalFrames = request.headers["Frames-Total"]
    frame = int(request.headers["Frame"])
    streamdir = streamid + "/"

    if (not os.path.isdir(streamdir)):
        os.mkdir(streamdir)

    outfn = (streamid + "/img%0" + str(len(totalFrames)) + "d") % (frame,) + ".png"
    with open(outfn, "a") as png:
        png.write(request.data)
    print("=== got frame {0} from {1}. has {2}".format(frame, totalFrames, framesHas))

    framesHas = len(filter(lambda f: f.endswith('.png'), os.listdir(streamid + '/')))
    if (totalFrames == framesHas):
        print "THEEND for " + streamid

        cmd = "ffmpeg -framerate 30 -i img%03d.png -c:v libx264 -pix_fmt yuv420p out.mp4"
        subprocess.call(cmd, cwd=streamid, shell=True)

    return 'ok'


@app.route("/proxy/<path:url>")
def proxy(url):
    url += '?' + '&'.join([arg + "=" + request.args[arg] for arg in request.args.keys()])
    print url

    r = urllib2.urlopen(url)
    return send_file(r, mimetype=r.headers.get('content-type'))

@app.route("/render/<streamid>")
def start_render(streamid):
    url = "/Ssswf.swf?posturl=http://localhost:5000/upload/" + streamid


    url += "&swf=about.swf&frames=364"
    #url += "&swf=ogo.swf&frames=150"


    url += ''.join(["&" + arg + "=" + request.args[arg] for arg in request.args.keys()])


    #TODO: open flash player
    return "file:///" + os.path.realpath(os.path.curdir) + "/static" + url


@app.route("/")
def collect_data():
    return render_template("collect_data.html", streamid=uuid.uuid1().hex)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

