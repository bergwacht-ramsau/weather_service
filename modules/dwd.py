import requests
from shapely.geometry import Point, Polygon


def createPolygonFromDwdData(dwd):
    result = []
    for i in range(0, int(len(dwd)/2)):
        result.append((dwd[2*i], dwd[2*i + 1]))
    return Polygon(result)


def checkWarningForLocation(warning, location):
    for region in warning["regions"]:
        poly = createPolygonFromDwdData(region["polygon"])
        return location.within(poly)


def getWarningsForLocation(data, latitude, longitude):
    location = Point(latitude, longitude)
    return list(filter(lambda warning: checkWarningForLocation(warning, location), data["warnings"]))


class DWD:

    def __init__(self):
        self.url = "https://s3.eu-central-1.amazonaws.com/app-prod-static.warnwetter.de/v16/gemeinde_warnings_v2.json"

    def getWarnings(self, latitude, longitude, level):
        warning_json = requests.get(self.url).json()
        result = []
        for warning in getWarningsForLocation(warning_json, latitude, longitude):
            result.append({"name": warning["headLine"], "description": warning["description"],
                           "start": warning["start"], "end": warning["end"], "level": warning["level"]})
        if level > 1:
            result = list(
                filter(lambda warning: warning["level"] >= level, result))
        return result
