#!/usr/bin/env python

import os
import shutil
import uuid
import subprocess
import urllib2
import json


from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from flask import abort, redirect, url_for


app = Flask(__name__)

def streamdir(streamid):
    return streamid + "/"


def hasFrames(streamid):
    sdir = streamdir(streamid)
    if (not os.path.isdir(sdir)):
        return 0
    return len(filter(lambda f: f.endswith('.png'), os.listdir(sdir)))


def submit_task(sid, url):
    open ("tasks/"+sid, "w").write(json.dumps(dict(sid=sid, url=url)))
    return True

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


@app.route('/api/hasvideo/<sid>/mp4')
def hasvideo(sid):
    f = streamdir(sid) + "out.mp4"
    if (os.path.isfile(f)):
        return json.dumps(dict(sid=sid, url="/cdn/"+sid+"/mp4"))
    else:
        return json.dumps(dict(sid=sid, progress=hasFrames(sid)))


@app.route("/api/checkandrender/<streamid>/<totalFrames>")
def check_and_render(streamid, totalFrames):
    sdir=streamdir(streamid)
    hf = hasFrames(streamid)
    print("=== {streamid} -- has {framesHas}, total {totalFrames}".format(streamid=streamid, framesHas=hf, totalFrames=totalFrames))
    if (hf == totalFrames):
        print "THEEND for " + streamid

        cmd = "../ffmpeg -tune zerolatency -preset ultrafast -framerate 30 -i img%03d.png -c:v libx264 -pix_fmt yuv420p tmp.out.mp4"
        print cmd
        subprocess.call(cmd, cwd=streamid, shell=True)
        shutil.move(sdir + "tmp.out.mp4", sdir + "out.mp4")
        return True
    else:
        return False


@app.route("/proxy/<path:url>")
def proxy(url):
    url += '?' + '&'.join([arg + "=" + request.args[arg] for arg in request.args.keys()])
    print url

    r = urllib2.urlopen(url)
    return send_file(r, mimetype=r.headers.get('content-type'))


@app.route("/video/<streamid>")
def vidos(streamid):
    return render_template("vidos.html", streamid=streamid)


@app.route("/render/<streamid>")
def start_render(streamid):
    url = "/Ssswf.swf?posturl=/upload/" + streamid
    url += "&swf=about.swf&frames=364"
    url += ''.join(["&" + arg + "=" + request.args[arg] for arg in request.args.keys()])
    submit_task(streamid, url)

    return redirect('/video/' + streamid)
    #return '<html><body><a href="{0}">ssswf</a></body></html>'.format("/static"+ url)


@app.route("/api/engine/tasks")
def apitasks():
    tasks = []
    for t in os.listdir("tasks"):
        tf = "tasks/" +t
        if (not os.path.isfile(tf)):
            continue
        print(tf)
        task = open(tf).read()
        sid = json.loads(task).get("sid")
        if (os.path.isfile(streamdir(sid) + "out.mp4")):
            shutil.move(tf, streamdir(sid) + "task.json")
        else:
            tasks.append(json.loads(task))
    return json.dumps(tasks)


@app.route("/engine")
def engine():
    return render_template("engine.html")

@app.route("/")
def collect_data():
    return render_template("collect_data.html", streamid=uuid.uuid1().hex)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8043)

