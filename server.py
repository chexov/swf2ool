#!/usr/bin/env python

import os
import shutil

from flask import Flask
from flask import request
app = Flask(__name__)

@app.route("/crossdomain.xml")
def cdxml():
    return app.send_static_file('crossdomain.xml')

@app.route("/upload/<filename>",methods=["POST"])
def savepng(filename):
    totalFrames = request.headers["Frames-Total"]
    frame = int(request.headers["Frame"])
    streamid = "mystreamid"
    streamdir = streamid + "/"

    if (not os.path.isdir(streamdir)):
        os.mkdir(streamdir)

    framesHas = len(filter(lambda f: f.endswith('.png'), os.listdir(streamid + '/')))

    outfn = (streamid + "/img%0" + str(len(totalFrames)) + "d") % (frame,) + ".png"
    with open(outfn, "a") as png:
        png.write(request.data)
    print("=== got frame {0} from {1}. has {2}".format(frame,totalFrames, framesHas))

    if (totalFrames == framesHas):
        print "THEEND for " + streamid

    return 'ok'

if __name__ == "__main__":
    app.run(debug=True)

