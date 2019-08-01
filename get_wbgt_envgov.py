#!/usr/bin/env python

import sys
from datetime import date
import requests
from html.parser import HTMLParser
import json

class HTMLParserWBGTEnvGoJp(HTMLParser):
    """
    html pserver class for the html text taken from WBGT daily in env.go.jp
    such as http://www.wbgt.env.go.jp/day_list.php?region=04&prefecture=49&point=49161&day=20190722
    """
    def __init__(self, debug, *args, **kwargs):
        self.debug = debug
        if self.debug:
            HTMLParser.__init__(self, convert_charrefs = True)
        HTMLParser.__init__(self)
        self.is_target_table = False
        self.is_hour = False
        self.is_wbgt = False
        self.hour = None
        self.wbgt_table = { "hour":[], "wbgt":[] }

    def handle_starttag(self, tag, attrs):
        if self.debug:
            print("TAG: [{}]".format(tag))
            print("attrs =", attrs)
        if tag == "table" and ("class", "asc_tbl_daylist") in attrs:
            self.is_target_table = True
        elif self.is_target_table and tag == "td":
            if ("class", "asc_body") in attrs and len(attrs) == 2:
                self.is_hour = True
            elif attrs[0][1].startswith("asc_body wbgt_lv"):
                self.is_wbgt = True

    def handle_endtag(self, tag):
        if self.debug:
            print("=== END TAG:[{}]".format(tag))
        if self.is_target_table and tag == "table":
            self.is_target_table = False

    def handle_data(self, data):
        if self.debug:
            print("DATA:[{}]".format(data))
        if self.is_hour is True:
            self.wbgt_table["hour"].append(data)
            self.hour = data
            self.is_hour = False
        elif self.is_wbgt is True:
            assert(self.hour is not None)
            self.wbgt_table["wbgt"].append(data)
            self.is_wbgt = False
            self.hour = None

    def get_result(self):
        self.wbgt_table["hour"] = [int(v) for v in self.wbgt_table["hour"]]
        self.wbgt_table["wbgt"] = [float(v) for v in self.wbgt_table["wbgt"]]
        assert(len(self.wbgt_table["hour"]) == 24)
        nb_wbgt = len(self.wbgt_table["wbgt"])
        for i in range(nb_wbgt, 24):
            self.wbgt_table["wbgt"].append(None)
        return self.wbgt_table

def parse_html_wbgt_envgojp(html_text, debug=False):
    """
    parsing the html text taken from WBGT daily in env.go.jp
    such as http://www.wbgt.env.go.jp/day_list.php?region=04&prefecture=49&point=49161&day=20190722
    return a list of wbgt in each hour.
    """
    p = HTMLParserWBGTEnvGoJp(debug=debug)
    p.feed(html_text)
    result = p.get_result()
    p.close()
    return result

def get_html_wbgt_envgojp(query, date_str=None, debug=False):
    """
    HTTP GET a page of the url like below:
    http://www.wbgt.env.go.jp/day_list.php?region=04&prefecture=49&point=49161&day=20190722
    return a html text.
    """
    if date_str is None:
        date_str = date.today().strftime("%Y%m%d")
    url = "http://www.wbgt.env.go.jp/day_list.php?{}&day={}".format(query,
                                                                    date_str)

    try:
        ret = requests.get(url, verify=False)
    except Exception as e:
        print("ERROR: {}".format(e))
        exit(1)

    if not ret.ok:
        print("ERROR: {} {}\n{}".format(ret.status_code, ret.reason, ret.text))
        exit(1)
    #
    ret.encoding = ret.apparent_encoding
    return ret.text

def get_id_by_ename(ename=None):
    """
    if ename is None, return the whole of point_list.
    the list is taken from below url:
        http://www.wbgt.env.go.jp/pdf/H31_point_list.pdf
    """
    point_list = {
            "otsuki": {
                    "name": "大月市大月",
                    "query": "region=04&prefecture=49&point=49161",
                    },
            "tokyo": {
                    "name": "東京都文京区白山小石川植物園",
                    "query": "region=03&prefecture=44&point=44132",
                    },
            }
    if ename is None:
        return point_list
    for k,v in point_list.items():
        if k == ename:
            return v
    return None

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
            description="""get wbgt from env.go.jp.  it will take the data
            of today when date_str is not specified.""",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("point_name", help="specify the point name, or 'list'.")
    ap.add_argument("-t", action="store", dest="date_str",
                    help="specify date such as 20190722.")
    ap.add_argument("--save-html-file", action="store", dest="save_html_file",
                    help="specify a file name to save the html text.")
    ap.add_argument("--read-html-file", action="store", dest="read_html_file",
                    help="specify a file name containing HTML text of WBGT table.")
    ap.add_argument("-d", action="store_true", dest="debug",
                    help="enable debug mode.")
    opt = ap.parse_args()
    #
    if opt.point_name == "list":
        print(json.dumps(get_id_by_ename()))
        exit(0)
    #
    if opt.read_html_file:
        html_text = open(opt.read_html_file, "r").read()
    else:
        point = get_id_by_ename(opt.point_name)
        if point is None:
            ap.print_help()
            exit(0)
        html_text = get_html_wbgt_envgojp(point["query"], date_str=opt.date_str,
                                        debug=opt.debug)
    #
    if opt.save_html_file:
        with open(opt.save_html_file, "w") as fd:
            fd.write(html_text)
    result = parse_html_wbgt_envgojp(html_text, debug=opt.debug)
    print(json.dumps(result))

