import requests
from haversine import haversine
from modules.tableparser import HTMLTableParser


class MDS:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.url = "https://mds.sommer.at/Web-Service-Admintool/"

    def getStations(self):
        headers = {'User-Agent': 'Mozilla/5.0',
                   'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'username': self.username,
                   'password': self.password, 'login': ''}
        session = requests.Session()
        session.post(self.url + "index.php", headers=headers,
                     data=payload, verify=False)

        stationListText = session.get(
            self.url + "forms/showUserStations.php", verify=False).text
        stationListParser = HTMLTableParser()
        stationListParser.feed(stationListText)
        stationListParser.close()
        stationList = (stationListParser.tables[0])
        stations = {}
        for i in range(1, len(stationList)):
            stationName = stationList[i][0].split(" ", 2)[2]
            stationId = stationList[i][1]
            stationText = session.get(
                self.url + "forms/showStationStatus.php?stationID="+stationId, verify=False).text
            stationParser = HTMLTableParser()
            stationParser.feed(stationText)
            stationParser.close()
            station = (stationParser.tables[0])
            id = stationList[i][1]
            time = stationList[i][5]
            latlon = stationList[i][2].split("&")
            lat = float(latlon[0].replace("latitude=", ""))
            lon = float(latlon[1].replace("longitude=", ""))
            values = {}
            for j in range(2, len(station)-1):
                name_height = station[j][0].split("_")
                if len(name_height) == 2:
                    value = station[j][1]
                    unit = station[j][2]
                    name = name_height[0]
                    height = name_height[1].replace("m", "")
                    if not height in values.keys():
                        values[height] = []
                    values[height] = values[height] + \
                        [{"name": name, "value": value, "unit": unit}]

            stations[stationName] = {"time": time, "values": values,
                                     "latitude": lat, "longitude": lon, "stationId": id}
        return stations

    def getNearestStation(self, latitude, longitude):
        point = (latitude, longitude)
        return min(self.getStations().items(), key=lambda x: haversine(point, (x[1]["latitude"], x[1]["longitude"])))
