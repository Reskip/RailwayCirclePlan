HEADER_12306 = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6",
    "Connection": "keep-alive",
    "Host": "kyfw.12306.cn",
    "Referer": "https://kyfw.12306.cn/otn/queryTrainInfo/init",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

HEADER_TRAIN = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6",
    "Connection": "keep-alive",
    "Host": "search.12306.cn",
    "Origin": "https://kyfw.12306.cn",
    "Referer": "https://kyfw.12306.cn/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

HEADER_SUANYA = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
}

STATION_URL = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
STATION_SCREEN_URL = "https://m.suanya.com/restapi/soa2/24635/getScreenStationData"
TRAIN_SEARCH_URL = "https://search.12306.cn/search/v1/train/search?keyword={keyword}&date={date}"
TRAIN_URL = "https://kyfw.12306.cn/otn/queryTrainInfo/query?leftTicketDTO.train_no={train_no}&leftTicketDTO.train_date={date}&rand_code="

TRAIN_TIMEOUT = 10
STATION_TIMEOUT = 10

STATION_FILE = "data/station.json"
RAILS_FILE = "data/rails.json"
COVER_FILE = "data/cover.json"
TRAIN_FILE = "data/train/{train_no}.json"
SCREEN_FILE = "data/screen/{station_name}.json"

COVER_COLOR_MAP = {
    'G': "#F96E2A",
    "K": "#0A5EB0",
    "P": "#1F4529",
}

NON_COVER_COLOR_MAP = {
    'G': "#BCEAF6",
    "K": "#E1FAC7",
    "P": "#D9DFC6",
    "E": "#FDB3C4",
}

NEW_LINE_COLOR_MAP = {
    'G': "#FBA2B7",
    "K": "#FBA2B7",
    "P": "#FBA2B7",
    "E": "#FBA2B7",
}

def RAILS_SPEED_MAP(speed):
    if speed < 100:
        return "P"
    if speed < 200:
        return "K"
    return "G"

def CONN_DIST_TRANS(distance):
    return distance ** 1.5 + 10

def CONN_RAIL_TRANS(train_type, rail_type, distance):
    if train_type == "G":
        if rail_type == "G":
            return distance
        if rail_type == "K":
            return distance * 2
        if rail_type == "P":
            return distance * 4
    if train_type == "K":
        if rail_type == "G":
            return distance * 2
        if rail_type == "K":
            return distance * 1
        if rail_type == "P":
            return distance * 2
    if train_type == "P":
        if rail_type == "G":
            return distance * 3
        if rail_type == "K":
            return distance * 1.5
        if rail_type == "P":
            return distance * 1