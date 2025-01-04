import matplotlib.pyplot as plt

import src.const as const

plt.rcParams['font.family'] = 'Heiti TC'

def render(stations, paths=[]):
    fig, ax = plt.subplots(figsize=(12, 8))

    lats = list()
    lngs = list()
    text = set()

    for rail_type_selected in const.RAILS_RENDER_RANK:
        for s in stations:
            now_station = stations[s]
            if len(now_station._conn_station) == 0:
                continue
            lng, lat = now_station.get_location()
            lats.append(lat)
            lngs.append(lng)

            for destination in now_station._conn_station:
                if destination >= s:
                    continue
                rail_type = list(now_station._conn_station[destination])
                if rail_type_selected not in rail_type:
                    continue
                color = const.NON_COVER_COLOR_MAP[rail_type_selected]
                dest_lng, dest_lat = stations[destination].get_location()
                plt.plot([lng, dest_lng], [lat, dest_lat], color=color, linewidth=2)
                text.add(s)
                text.add(destination)

    for s in stations:
        if s not in text:
            continue
        now_station = stations[s]
        lng, lat = now_station.get_location()
        # plt.text(lng, lat, s)

    for train in paths:
        path = train._real_path
        now_station = path[0][0]
        for dest_station, rail_type in path[1:]:
            color = const.NEW_LINE_COLOR_MAP[rail_type]
            now_lng, now_lat = stations[now_station].get_location()
            dest_lng, dest_lat = stations[dest_station].get_location()
            plt.plot([now_lng, dest_lng], [now_lat, dest_lat], color=color, linewidth=5)
            now_station = dest_station

    for s in stations:
        now_station = stations[s]
        if len(now_station._conn_station) == 0:
            continue
        lng, lat = now_station.get_location()

        for destination in now_station._covered:
            if destination >= s:
                continue
            rail_type = list(now_station._covered[destination])
            rail_type = sorted(rail_type)

            color = const.COVER_COLOR_MAP[rail_type[0]]
            dest_lng, dest_lat = stations[destination].get_location()

            plt.plot([lng, dest_lng], [lat, dest_lat], color=color)

    # ax.scatter(lngs, lats, s=10)

    # display.clear_output(wait=True)
    plt.show()