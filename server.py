from flask import Flask
from flask import request
app = Flask(__name__)

@app.route("/upload/<filename>",methods=["POST"])
def savepng(filename):
    with open(("img%0" + str(len(request.headers["Frames-Total"])) + "d") % (int(request.headers["Frame"]), ) + ".png", "a") as png:
        png.write(request.data)
    return 'ok'

if __name__ == "__main__":
    print 'gagaga'
    app.run(debug=True)