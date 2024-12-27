import json
import math

import src.const as const

class Station(object):
    def __init__(self, name, json_obj, logger=None):
        self._logger = logger

        self._lng = json_obj["lng"]
        self._lat = json_obj["lat"]
        self._station_name = name
        self._data = json_obj

        self._conn_station = dict()
        self._covered = dict()

    def __repr__(self):
        return "[Station] {name}".format(name=self._station_name)
    
    def get_key(self):
        return self._station_name
    
    def get_location(self):
        return self._lng, self._lat

    def update_direct_conn_station(self, destination, rail_type):
        if destination not in self._conn_station:
            self._conn_station[destination] = set()
        self._conn_station[destination].add(
            const.RAILS_SPEED_MAP[rail_type]
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
    station_info = json.loads(open(const.STATION_FILE, encoding='utf-8').read())
    for name in station_info:
        station = station_info[name]
        station_dict[name] = Station(name, station, logger)
    return station_dict


def enable_rails_on_station(station_dict):
    rails_info = json.loads(open(const.RAILS_FILE, encoding='utf-8').read())
    for rail in rails_info:
        info = rails_info[rail]
        diagram = info["diagram"]
        rail_type = info["railType"]

        for start, end in diagram:
            station_dict[start].update_direct_conn_station(end, rail_type)
            station_dict[end].update_direct_conn_station(start, rail_type)


def enable_cover_on_station(station_dict):
    cover_info = json.loads(open(const.COVER_FILE, encoding='utf-8').read())
    for cover in cover_info:
        source = cover["source"]
        destination = cover["destination"]
        rail_type = cover["type"]

        station_dict[source].update_cover_station(destination, rail_type)
        station_dict[destination].update_cover_station(source, rail_type)
