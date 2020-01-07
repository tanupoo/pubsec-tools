#!/usr/bin/env python

from climate_stations import ClimateStation
import requests
import argparse
import re

base_url = "https://www.data.jma.go.jp/gmd/cpd/monitor/climatview/download.php"
re_period = re.compile("^(\d{4})(\d{2}),(\d{4})(\d{2})$")

def get_csv_jmagov(station_id, ys, ms, ye, me, debug=False):
    url = f"{base_url}?n={station_id}&ys={ys}&ms={ms}&ye={ye}&me={me}"
    if debug:
        print("URL: {}".format(url))

    try:
        ret = requests.get(url, verify=True)
    except Exception as e:
        print("ERROR: {}".format(e))
        exit(1)

    if not ret.ok:
        print("ERROR: {} {}\n{}".format(ret.status_code, ret.reason, ret.text))
        exit(1)
    #
    if debug:
        print("text encoding: ", ret.apparent_encoding)
    ret.encoding = ret.apparent_encoding
    return ret.text

def save_data(csv_text, file_name=None, station_id=None, period=None,
              debug=False):
    """
    save data into the file.
    file_name is always used if specified (not None). 
    """
    if file_name is None and station_id is not None:
        if period is None:
            period = "000000-000000"
        file_name = f"jma-{station_id}-{period}.csv"
    elif file_name is None:
        raise ValueError(
                "ERROR: both file_name and station_id are not specified.")
    if debug:
        print("saved:", file_name)
    with open(file_name, "w") as fd:
        fd.write(csv_text)

ap = argparse.ArgumentParser(
        description=""" hoge """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("--station", "-i", action="store", dest="station_id",
                help="specify a station id.")
ap.add_argument("--output", action="store", dest="output_file",
                help="specify a file name stroing the response.")
ap.add_argument("--period", action="store", dest="period",
                help="specify a period. e.g. --period 201501,201912")
ap.add_argument("--all", action="store_true", dest="get_all",
                help="specify to retrieve all data in the list.")
ap.add_argument("--list", action="store_true", dest="list_stations",
                help="show the list of stations and exit.")
ap.add_argument("--force", action="store_true", dest="force_retrieve",
                help="force to retrieve data if not existed in the list.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

station = ClimateStation()

if opt.list_stations:
    station.show_stations()
    exit(0)

# make period.
ys, ms, ye, me = (2015, 1, 2019, 12) # default
if opt.period:
    r = re_period.match(opt.period)
    if r:
        ys, ms, ye, me = (int(r.group(1)), int(r.group(2)), int(r.group(3)),
                          int(r.group(4)))
    else:
        print("ERROR: invalid format of period")
        exit(0)
period = f"{ys:04d}{ms:02d}-{ye:04d}{me:02d}"

# get data.
if not ((opt.get_all is True) ^ (opt.station_id is not None)):
    ap.print_help()
    exit(1)

if opt.get_all is True:
    for sid in station.get_id_list():
        csv_text = get_csv_jmagov(sid, ys, ms, ye, me, opt.debug)
        save_data(csv_text, station_id=sid, period=period, debug=opt.debug)

elif opt.station_id is not None:
    if (station.get_name(opt.station_id) is False and
        opt.force_retrieve is False):
        print("ERROR: {} is not in the list.")
        exit(1)
    csv_text = get_csv_jmagov(opt.station_id, ys, ms, ye, me, opt.debug)
    save_data(csv_text, file_name=opt.output_file,
              station_id=opt.station_id, period=period, debug=opt.debug)
