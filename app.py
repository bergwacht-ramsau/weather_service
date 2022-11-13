import requests
import re
from html_table_parser.parser import HTMLTableParser
import flask
from flask import request, jsonify
import os

app = flask.Flask(__name__)

USER = os.environ.get("MDS_USER")
PASSWORD = os.environ.get("MDS_PASSWORD")

if not USER:
    raise ValueError("No MDS_USER set for Flask application")
if not PASSWORD:
    raise ValueError("No MDS_PASSWORD set for Flask application")

@app.route('/', methods=['GET'])
def home():
	headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'username': USER, 'password': PASSWORD, 'login': ''}
	link    = "https://mds.sommer.at/Web-Service-Admintool/index.php"
	session = requests.Session()
	session.post(link,headers=headers,data=payload)

	stationListText = session.get("https://mds.sommer.at/Web-Service-Admintool/forms/showUserStations.php").text
	stationListParser = HTMLTableParser()
	stationListParser.feed(stationListText)
	stationListParser.close()
	stationList = (stationListParser.tables[0])
	stations = {}
	for i in range (1, len(stationList)-1):
		stationName = stationList[i][0].split(" ", 2)[2]
		stationId = stationList[i][1]
		stationText = session.get("https://mds.sommer.at/Web-Service-Admintool/forms/showStationStatus.php?stationID="+stationId).text
		stationParser = HTMLTableParser()
		stationParser.feed(stationText)
		stationParser.close()
		station = (stationParser.tables[0])
		time = stationList[i][5]
		values = {}
		for j in range (2, len(station)-1):
			name_height = station[j][0].split("_")
			if len(name_height) == 2:
				value = station[j][1]
				unit = station[j][2]
				name = name_height[0]
				height = name_height[1].replace("m","")
				if not height in values.keys():
					values[height] = []
				values[height] = values[height] + [{"name": name, "value": value, "unit": unit}]
		
		stations[stationName] = {"time": time, "values": values}
	return jsonify(stations)

app.run()
