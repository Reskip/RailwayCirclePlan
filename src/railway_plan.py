
import random
import copy

import src.utils as utils
from src.train import Train
from src.station_screen import get_station_screen

class RailwayPlan(object):
    def __init__(self, station_dict):
        self._station_dict = station_dict
        self._station_screens = dict()
        self._search_result = list()

    def coverage_delta(self, result):
        _, before_coverage = utils.get_coverage(self._station_dict)
        station_dict_copy = copy.deepcopy(self._station_dict)
        status = True

        for train_obj in result:
            status = status and utils.update_cover_train_obj(train_obj, station_dict_copy)

        _, new_coverage = utils.get_coverage(station_dict_copy)
        if status:
            return sum(new_coverage) - sum(before_coverage)
        else:
            return None
        
    def _get_valid_train(
            self,
            valid_train_list,
            train_type_limit,
            min_run_time,
            transfer_time_window,
            start_time,
            path_to_here,
            current_time_cnt,
            end_stations
            ):
        for train, start_station, train_start in valid_train_list:
            train_obj = Train(train)

            if train_obj._train_search_no == "":
                continue

            if train_obj._train_type not in train_type_limit:
                continue

            train_obj.cut_path(start_station=start_station)
            train_start_time = utils.time_to_min(
                train_obj._station_list[0]["start_time"],
                int(train_obj._station_list[0]["arrive_day_diff"])
            )

            if start_time is None:
                start_time = train_start
            if train_start < start_time:
                train_start += 24 * 60
            waiting_time = train_start - start_time

            for next_station in train_obj._station_list:
                if next_station["station_name"] == start_station:
                    continue
                if "arrive_time" not in next_station:
                    continue

                run_time = utils.time_to_min(
                    next_station["arrive_time"],
                    int(next_station["arrive_day_diff"])
                ) - train_start_time

                if run_time < min_run_time:
                    continue

                next_start_time = utils.time_to_min(
                    next_station["arrive_time"]
                )

                if next_station["station_name"] not in end_stations:
                    if next_start_time > transfer_time_window[1]:
                        continue
                    if next_start_time < transfer_time_window[0] and\
                        next_start_time + 60*24 > transfer_time_window[1]:
                        continue

                new_train_obj = copy.deepcopy(train_obj)
                new_train_obj.cut_path(end_station=next_station["station_name"])
                _path_to_here = copy.deepcopy(path_to_here)
                _path_to_here.append(new_train_obj)
                yield {
                    "path_to_here": _path_to_here,
                    "run_time": current_time_cnt+run_time+waiting_time,
                    "start_station": next_station["station_name"],
                    "start_time": next_start_time
                }

    def _random_dfs(self,
                   path_to_here,
                   current_time_cnt,
                   max_time,
                   search_result_num,
                   start_station,
                   end_stations,
                   start_time,
                   train_type_limit,
                   min_transfer_time,
                   max_transfer_time,
                   transfer_time_window,
                   min_run_time,
                   max_transfer,
                   random_drop_station
                ):
        if current_time_cnt > max_time:
            return
        if len(self._search_result) >= search_result_num:
            return

        if start_station in end_stations:
            self._search_result.append(path_to_here)
            return

        if random.random() > random_drop_station:
            return
        if len(path_to_here) > max_transfer:
            return

        print(start_station, start_time, current_time_cnt, len(path_to_here), len(self._search_result))

        if start_station not in self._station_screens:
            screen = get_station_screen(start_station)
            self._station_screens[start_station] = screen

        valid_train = list()
        for train_no, train_start in self._station_screens[start_station]:
            if train_start > start_time + max_transfer_time:
                continue
            if train_start < start_time + min_transfer_time and\
                train_start + 60*24 > start_time + max_transfer_time:
                continue
            valid_train.append([train_no, start_station, train_start])
        random.shuffle(valid_train)

        for valid_train_info in self._get_valid_train(
            valid_train_list=valid_train,
            train_type_limit=train_type_limit,
            min_run_time=min_run_time,
            transfer_time_window=transfer_time_window,
            start_time=start_time,
            path_to_here=path_to_here,
            current_time_cnt=current_time_cnt,
            end_stations=end_stations
        ):
            self._random_dfs(
                path_to_here=valid_train_info["path_to_here"],
                current_time_cnt=valid_train_info["run_time"],
                max_time=max_time,
                search_result_num=search_result_num,
                start_station=valid_train_info["start_station"],
                end_stations=end_stations,
                start_time=valid_train_info["start_time"],
                train_type_limit=train_type_limit,
                min_transfer_time=min_transfer_time,
                max_transfer_time=max_transfer_time,
                transfer_time_window=transfer_time_window,
                min_run_time=min_run_time,
                max_transfer=max_transfer,
                random_drop_station=random_drop_station
            )

    def plan(   self,
                start_stations,
                max_transfer,
                max_time=60*48,
                train_type_limit=["G", "K", "P"],
                end_stations=None,
                min_transfer_time=45,
                max_transfer_time=90,
                min_run_time=120,
                search_result_num=50,
                random_drop_station=0.5,
                start_time_window=[0, 60*24],
                transfer_time_window=[0, 60*24]
                ):
        self._station_screens = dict()
        self._search_result = list()

        _end_stations = end_stations
        if end_stations is None:
            _end_stations = start_stations

        valid_train = list()
        for start_station in start_stations:
            screen = get_station_screen(start_station)
            for train_no, train_start in screen:
                if train_start < start_time_window[0] and train_start + 60*24 > start_time_window[1]:
                    continue
                if train_start > start_time_window[1]:
                    continue
                valid_train.append([train_no, start_station, train_start])
        random.shuffle(valid_train)

        for valid_train_info in self._get_valid_train(
            valid_train_list=valid_train,
            train_type_limit=train_type_limit,
            min_run_time=min_run_time,
            transfer_time_window=transfer_time_window,
            start_time=None,
            path_to_here=[],
            current_time_cnt=0,
            end_stations=end_stations
        ):
            self._random_dfs(
                path_to_here=valid_train_info["path_to_here"],
                current_time_cnt=valid_train_info["run_time"],
                max_time=max_time,
                search_result_num=search_result_num,
                start_station=valid_train_info["start_station"],
                end_stations=_end_stations,
                start_time=valid_train_info["start_time"],
                train_type_limit=train_type_limit,
                min_transfer_time=min_transfer_time,
                max_transfer_time=max_transfer_time,
                transfer_time_window=transfer_time_window,
                min_run_time=min_run_time,
                max_transfer=max_transfer,
                random_drop_station=random_drop_station
            )
        return self._search_result
