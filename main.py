
from src.render import render
from src.railway_plan import RailwayPlan
from src.station import get_station_info, enable_cover_on_station, enable_rails_on_station


if __name__ == "__main__":
    station_dict = get_station_info()
    enable_rails_on_station(station_dict)
    enable_cover_on_station(station_dict)

    railway_plan = RailwayPlan(station_dict)
    search_result = railway_plan.plan(
        start_stations=["北京","北京朝阳","北京西","北京南","北京北","北京丰台","清河"],
        end_stations=["北京","北京朝阳","北京西","北京南","北京北","北京丰台","清河"],
        train_type_limit=["G", "K", "P"],
        max_transfer=2,
        random_drop_station=0.7,
        min_run_time=60*5,
        search_result_num=500,
        min_transfer_time=30,
        max_transfer_time=60*10,
        max_time=60*24*4,
        start_time_window=[0, 60*24],
        transfer_time_window=[0, 60*24]
    )

    search_result = [[results, railway_plan.coverage_delta(results)] for results in search_result]
    search_result = filter(lambda x: x[1] is not None, search_result)
    search_result = sorted(search_result, key=lambda x: x[1], reverse=True)

    for results in search_result[:10]:
        print(results[1])
        for train_obj in results[0]:
            print(train_obj)
        render(station_dict, paths=results[0])