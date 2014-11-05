#!/usr/bin/env python

import os
import shutil
import uuid

from flask import Flask
from flask import render_template
from flask import request
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

    framesHas = len(filter(lambda f: f.endswith('.png'), os.listdir(streamid + '/')))

    outfn = (streamid + "/img%0" + str(len(totalFrames)) + "d") % (frame,) + ".png"
    with open(outfn, "a") as png:
        png.write(request.data)
    print("=== got frame {0} from {1}. has {2}".format(frame, totalFrames, framesHas))

    if (totalFrames == framesHas):
        print "THEEND for " + streamid

    return 'ok'

@app.route("/render/<streamid>")
def start_render(streamid):
    url = "/Ssswf.swf?posturl=http://localhost:5000/upload/" + streamid


    url += "&swf=about.swf&frames=364"
    #url += "&swf=ogo.swf&frames=150"


    url += ''.join(["&" + arg + "=" + request.args[arg] for arg in request.args.keys()])


    #TODO: open flash player
    return url

@app.route("/")
def collect_data():
    return render_template("collect_data.html", streamid=uuid.uuid1().hex)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

