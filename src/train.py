
import requests
import time
import json
import os
from datetime import datetime
from sklearn.neighbors import KDTree

import src.const as const

class Train(object):
    LAST_QUERY = time.time()

    def __init__(self, train_no, logger=None):
        self._train_no = train_no
        self._logger = logger
        self._parse_train_type()

        file_name = const.TRAIN_FILE.format(
            train_no=self._train_no
        )

        if os.path.exists(file_name):
            self._load_from_file(file_name)
        else:
            if time.time() - Train.LAST_QUERY < 1:
                time.sleep(1)
            self._get_search_no()
            if self._train_search_no != "":
                self._search_train_station()
            if self._train_search_no != "":
                self._dump_to_file(file_name)
            Train.LAST_QUERY = time.time()

    def __repr__(self):
        date_delta = int(self._station_list[-1]["arrive_day_diff"])\
            - int(self._station_list[0]["arrive_day_diff"])
        return "[Train] {id}, [{start_time} - {end_time}{time_add}] {stations}".format(
            id=self._train_no,
            start_time=self._station_list[0]["start_time"],
            end_time=self._station_list[-1]["arrive_time"],
            time_add="" if date_delta==0 else "(+{})".format(date_delta),
            stations=self._station_names
        )

    def _parse_train_type(self):
        if self._train_no[0] in ['G', 'D', 'C', 'S']:
            self._train_type = "G"
        elif self._train_no[0] in ['Z', 'T', 'K', 'Y']:
            self._train_type = "K"
        elif self._train_no[0] in '0123456789':
            self._train_type = "P"
        else:
            print('error train type: {}'.format(self._train_no))
            self._train_type = "E"

    def _get_search_no(self):
        self._train_search_no = ""
        now = datetime.now()
        date_yyyymmdd = now.strftime("%Y%m%d")

        try:
            search = requests.get(
                const.TRAIN_SEARCH_URL.format(
                    keyword=self._train_no,
                    date=date_yyyymmdd
                ),
                headers=const.HEADER_TRAIN
            )
            for train in json.loads(search.text)["data"]:
                if train["station_train_code"] == self._train_no:
                    self._train_search_no = train["train_no"]
                    break
        except Exception as e:
            self._train_search_no = ""
            print("Train {train_no} get temp no error, {e}".format(
                train_no=self._train_no,
                e=e
            ))

    def _search_train_station(self):
        if self._train_search_no == "":
            return

        now = datetime.now()
        date_yyyy_mm_dd = now.strftime("%Y-%m-%d")

        try:
            search = requests.get(
                const.TRAIN_URL.format(
                    train_no=self._train_search_no,
                    date=date_yyyy_mm_dd
                ),
                headers=const.HEADER_12306,
                timeout=const.TRAIN_TIMEOUT
            )

            # "arrive_day_str": "当日到达",
            # "arrive_time": "20:40",
            # "station_name": "金华",
            # "arrive_day_diff": "0",
            # "start_time": "20:46",
            # "running_time": "03:13"
            self._station_list = json.loads(search.text)["data"]["data"]
            self._station_names = [s["station_name"] for s in self._station_list]
        except Exception as e:
            print("Search train {train_no} error, {e}".format(
                train_no=self._train_no, e=e
            ))
            self._train_search_no = ""

    def _load_from_file(self, file_name):
        f = open(file_name)
        data = json.loads(f.read())
        self._station_list = data["station_list"]
        self._station_names = data["station_names"]
        self._train_search_no = data["train_search_no"]

    def _dump_to_file(self, file_name):
        f = open(file_name, "w")
        f.write(json.dumps({
            "station_list": self._station_list,
            "station_names": self._station_names,
            "train_search_no": self._train_search_no
        }, ensure_ascii=False, indent=4))
        f.close()

    def cut_path(self, start_station=None, end_station=None):
        if start_station is not None:
            start_index = self._station_names.index(start_station)
            self._station_names = self._station_names[start_index:]
            self._station_list = self._station_list[start_index:]
        if end_station is not None:
            end_index = self._station_names.index(end_station)
            self._station_names = self._station_names[:end_index+1]
            self._station_list = self._station_list[:end_index+1]

    def get_real_path(self, station_dict):
        for station_name in self._station_names:
            if station_name not in station_dict:
                print("error, station not in list", station_name)
                return None

        kd_tree_pos = list()
        kd_tree_name = list()
        for station_name in station_dict:
            kd_tree_pos.append(station_dict[station_name].get_location())
            kd_tree_name.append(station_name)
        tree = KDTree(kd_tree_pos, leaf_size=2)

        self._real_path = [[self._station_names[0], None]]

        for name in self._station_names[1:]:
            via_path_dict = {self._real_path[-1][0]: [0, None, False, None]}

            while True:
                start_point = None
                min_distance = 1e10
                for point in via_path_dict:
                    if via_path_dict[point][2] == False and via_path_dict[point][0] < min_distance:
                        min_distance = via_path_dict[point][0]
                        start_point = point

                if start_point == name:
                    break
                
                if start_point is None:
                    print("get next point error", self._real_path[-1][0], name)
                    return None
                
                via_path_dict[start_point][2] = True
                for next_point in station_dict[start_point]._conn_station:
                    distance = station_dict[start_point].distance(station_dict[next_point])
                    trans_distance = 1e10
                    real_rail_type = None
                    for rail_type in station_dict[start_point]._conn_station[next_point]:
                        if trans_distance > const.CONN_RAIL_TRANS(self._train_type, rail_type,distance):
                            real_rail_type = rail_type
                            trans_distance = const.CONN_RAIL_TRANS(self._train_type, rail_type,distance)

                    if next_point not in via_path_dict or via_path_dict[next_point][0] > min_distance + trans_distance:
                        via_path_dict[next_point] = [min_distance + trans_distance, start_point, False, real_rail_type]

                _, ind = tree.query([station_dict[start_point].get_location()], k=20)
                for i in ind[0]:
                    next_point = kd_tree_name[i]
                    if next_point == start_point:
                        continue
                    origin_distance = station_dict[start_point].distance(station_dict[next_point])
                    trans_distance = const.CONN_DIST_TRANS(origin_distance)
                    if next_point not in via_path_dict or via_path_dict[next_point][0] > min_distance + trans_distance:
                        via_path_dict[next_point] = [min_distance + trans_distance, start_point, False, "E"]

            backfill_name = name
            appendix = list()
            while True:
                rail_type = via_path_dict[backfill_name][3]
                appendix.append([backfill_name, rail_type])
                backfill_name = via_path_dict[backfill_name][1]
                if backfill_name is None:
                    break
            appendix.reverse()
            self._real_path.extend(appendix[1:])
        return True

if __name__ == "__main__":
    print(Train("D182"))
