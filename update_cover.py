from src.render import render
from src.station import get_station_info, enable_cover_on_station, enable_rails_on_station
from src.train import Train
from src.utils import update_cover, dump_cover_to_file


if __name__ == "__main__":
    station_dict = get_station_info()
    enable_rails_on_station(station_dict)
    update_cover("K1456", station_dict, "北京丰台", "承德")
    render(station_dict)

    enable_cover_on_station(station_dict)

    if input("INPUT Y/N: ") == "Y":
        dump_cover_to_file(station_dict)
        render(station_dict)