
import json

import src.const as const
from src.train import Train


def update_cover_train_obj(train_obj, station_dict):
    resp = train_obj.get_real_path(station_dict)

    if resp is None:
        return False

    last_station = train_obj._real_path[0][0]
    for station_info in train_obj._real_path[1:]:
        now_station = station_info[0]
        rail_type = station_info[1]
        if rail_type == "E":
            continue
        station_dict[last_station].update_cover_station(now_station, rail_type)
        station_dict[now_station].update_cover_station(last_station, rail_type)

        last_station = now_station

    return True

def update_cover(train_name, station_dict, start_station=None, end_station=None):
    train_obj = Train(train_name)
    train_obj.cut_path(start_station, end_station)

    return update_cover_train_obj(train_obj, station_dict)

def dump_cover_to_file(station_dict):
    f = open(const.COVER_FILE, "w")
    dump_json = list()
    for station in station_dict:
        covered = station_dict[station]._covered
        for destination in covered:
            for rail_type in covered[destination]:
                if rail_type == "E":
                    continue
                dump_json.append({
                    "source": station,
                    "destination": destination,
                    "type": rail_type
                })
    f.write(json.dumps(dump_json, ensure_ascii=False, indent=4))
    f.close()

def time_to_min(time_str, day_delta=0):
    return int(time_str.split(":")[0]) * 60 + int(time_str.split(":")[1]) + day_delta * 24 * 60

def get_coverage(station_dict):
    rail_types = ["G", "K", "P"]
    railways = [0, 0, 0]
    coverage = [0, 0, 0]

    for station in station_dict:
        station_info = station_dict[station]
        
        for destination in station_info._conn_station:
            if destination >= station:
                continue
            distance = station_info.distance(
                station_dict[destination]
            )
            for rail_type in station_info._conn_station[destination]:
                if rail_type not in rail_types:
                    continue
                railways[rail_types.index(rail_type)] += distance
        
        for destination in station_info._covered:
            if destination >= station:
                continue
            distance = station_info.distance(
                station_dict[destination]
            )
            for rail_type in station_info._covered[destination]:
                if rail_type not in rail_types:
                    continue
                coverage[rail_types.index(rail_type)] += distance

    return railways, coverage