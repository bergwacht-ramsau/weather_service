import os
import flask
from flask import request, jsonify
from modules.dwd import DWD
from modules.mds import MDS

app = flask.Flask(__name__)

USER = os.environ.get("MDS_USER")
PASSWORD = os.environ.get("MDS_PASSWORD")

if not USER:
    raise ValueError("No MDS_USER set for Flask application")
if not PASSWORD:
    raise ValueError("No MDS_PASSWORD set for Flask application")

mds = MDS(USER, PASSWORD)
dwd = DWD()


@app.route('/', methods=['GET'])
def home():
    latitude = request.args.get("lat", default=0.0, type=float)
    longitude = request.args.get("lon", default=0.0, type=float)

    if latitude == 0.0 or longitude == 0.0:
        stations = mds.getStations()
        response = jsonify(stations)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        nearestStation = mds.getNearestStation(latitude, longitude)
        response = jsonify({nearestStation[0]: nearestStation[1]})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/warnings', methods=['GET'])
def warnings():
    latitude = request.args.get("lat", default=0.0, type=float)
    longitude = request.args.get("lon", default=0.0, type=float)
    level = request.args.get("level", default=1, type=int)
    if latitude == 0.0 or longitude == 0.0:
        return "lat and lon query parameters must be specified"
    result = dwd.getWarnings(latitude, longitude, level)
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

try:
    app.run()
finally:
    mds.deinit()
    dwd.deinit()