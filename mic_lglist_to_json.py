#!/usr/bin/env python

import json
import xlrd
import magic
import tempfile
import bz2
import argparse

def parse_wb(xls_wb):
    lg_data = {}
    # R1.5.1
    # 011002    北海道  札幌市  ﾎｯｶｲﾄﾞｳ ｻｯﾎﾟﾛｼ
    xls_rows = xls_wb.sheet_by_index(0).get_rows()
    xls_rows.__next__() # skip the header.
    for row in xls_rows:
        if row[2].value == "":
            lg_data.update({ row[1].value : row[0].value[:5] })
        else:
            lg_data.update({ "{}{}".format(row[1].value, row[2].value) :
                            row[0].value[:5] })
    # H30.10.1
    # 011011    札幌市中央区    さっぽろしちゅうおうく
    xls_rows = xls_wb.sheet_by_index(1).get_rows()
    for row in xls_rows:
        lg_data.update({ row[1].value : str(row[0].value)[:5] })
    #
    print(json.dumps(lg_data, indent=4, ensure_ascii=False))

def parse_lgcode_xls(given_file):
    ftype = magic.from_file(given_file)
    print(f"ftype: {ftype}")
    if "bzip2 compressed" in ftype:
        with bz2.open(given_file, mode="rb") as src:
            with tempfile.NamedTemporaryFile() as dst:
                dst.write(src.read())
                dst.seek(0,0)
                xls_wb = xlrd.open_workbook(dst.name)
                if opt.debug:
                    print("sheets =", xls_wb.sheet_names())
                parse_wb(xls_wb)
    elif "Microsoft Excel" in ftype:
        xls_wb = xlrd.open_workbook(given_file)
        if opt.debug:
            print("sheets =", xls_wb.sheet_names())
        parse_wb(xls_wb)

#
# main
#
ap = argparse.ArgumentParser()
ap.add_argument("xls_file", help="XLS file taken from MIC.")
ap.add_argument("-i", action="store", dest="indent", type=int,
                help="specify the number of columns for indent. e.g. -i 4")
ap.add_argument("-s", action="store", dest="skip_lines", type=int, default=1,
                help="""specify the number of lines at the header
                in the file to skip.""")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

parse_lgcode_xls(opt.xls_file)

