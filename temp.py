
from src.render import render
from src.railway_plan import RailwayPlan
from src.station import get_station_info, enable_cover_on_station, enable_rails_on_station

station_dict = get_station_info()
enable_rails_on_station(station_dict)
render(station_dict)