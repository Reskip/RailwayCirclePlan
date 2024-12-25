import requests
import string
import random
import json
import time
import os

import src.const as const
import src.utils as utils

def random_num(num: int):
    all_chars = string.digits
    sign = ''.join(random.choice(all_chars) for _ in range(num))
    return sign

def get_station_screen(station, screen_flag=0):
    """
    获取车站的屏幕信息
    返回值中invalidWaitingScreens为停止检票的车次信息, stationWaitingScreens为正在检票和正在候车的车次信息
    :return:
    """
    file_name = const.SCREEN_FILE.format(station_name=station)
    if os.path.exists(file_name):
        return json.loads(open(file_name).read())

    headers = const.HEADER_SUANYA

    random_str = random_num(20)
    params = {
        "_fxpcqlniredt": f"{random_str}",
        "x-traceID": f"{random_str}-{int(time.time()) * 1000}-{random_num(7)}"
    }
    data = {"stationName": f"{station}", "screenFlag": screen_flag,
            "authentication": {"partnerName": "ZhiXing", "source": "", "platform": "APP"},
            "head": {"cid": f"{random_str}", "ctok": "", "cver": "1005.006", "lang": "01", "sid": "8888",
                        "syscode": "32", "auth": "", "xsid": "", "extension": []}}

    try:
        response = requests.post(const.STATION_SCREEN_URL, headers=headers, params=params, json=data, timeout=const.STATION_TIMEOUT)
        response = json.loads(response.text)
    except Exception as e:
        print("Fetch screen error {station}, {e}".format(
            station=station, e=e
        ))
        return []

    response = [[t["trainNo"], utils.time_to_min(t["departTime"])] for t in response["stationWaitingScreens"] + response["invalidWaitingScreens"]]
    f = open(file_name, "w")
    f.write(json.dumps(response, ensure_ascii=False, indent=4))
    f.close()
    return response


if __name__ == '__main__':
    print(get_station_screen("北京西"))