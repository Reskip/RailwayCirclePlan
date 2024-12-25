import json
import math

import src.const as const

class Station(object):
    def __init__(self, json_obj, logger=None):
        self._logger = logger

        self._lng, self._lat = json_obj["coordinates"]
        self._station_name = json_obj["name"]
        self._train_num = json_obj["train_num"]

        self._conn_station = dict()
        self._covered = dict()

    def __repr__(self):
        return "[Station] {name}".format(name=self._station_name)
    
    def get_key(self):
        return self._station_name
    
    def get_location(self):
        return self._lng, self._lat

    def update_direct_conn_station(self, destination, speed):
        if destination not in self._conn_station:
            self._conn_station[destination] = set()
        self._conn_station[destination].add(
            const.RAILS_SPEED_MAP(speed)
        )

    def update_cover_station(self, destination, rail_type):
        if destination not in self._covered:
            self._covered[destination] = set()
        self._covered[destination].add(rail_type)

    def distance(self, other_station):
        lon1, lat1, lon2, lat2 = map(
            math.radians,
            [self._lng, self._lat, other_station._lng, other_station._lat]
        )
 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 

        return c * 6371
        

def get_station_info(logger=None):
    station_dict = dict()
    station_info = json.loads(open(const.STATION_FILE).read())
    for station in station_info:
        name = station["name"]
        station_dict[name] = Station(station, logger)
    return station_dict


def enable_rails_on_station(station_dict):
    rails_info = json.loads(open(const.RAILS_FILE).read())
    for rail in rails_info:
        info = rails_info[rail]
        stations = info["stations"]
        speed = info["speed"]

        for i in range(len(stations)-1):
            source_station = stations[i]
            destination_station = stations[i+1]
            station_dict[source_station].update_direct_conn_station(destination_station, speed)
            station_dict[destination_station].update_direct_conn_station(source_station, speed)


def enable_cover_on_station(station_dict):
    cover_info = json.loads(open(const.COVER_FILE).read())
    for cover in cover_info:
        source = cover["source"]
        destination = cover["destination"]
        rail_type = cover["type"]

        station_dict[source].update_cover_station(destination, rail_type)
        station_dict[destination].update_cover_station(source, rail_type)

if __name__ == "__main__":
    station_dict = get_station_info(open("test_log", "w"))
    enable_rails_on_station(station_dict)