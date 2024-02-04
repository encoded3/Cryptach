from flask import Flask, render_template, request, send_file
from main import cryptach
from easygui import fileopenbox

app = Flask(__name__)

@app.route("/")
def index():
   return render_template("index.html")

@app.route('/encrypt', methods=['GET'])
def encrypt():
   args = request.args.to_dict()

   args["file"] = fileopenbox("Choose file")

   cryptach(request.args.to_dict())
   return send_file("output.sb3")

app.run(debug=True, port=6565)
