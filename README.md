tools-pubsec
============

A set of utilities to utilize open data in Japan.

## examples

    python get_wbgt_envgov.py otsuki -t 20190801 | tee 20190801.json | ./plot-wbgt.py 

## debug

    python get_wbgt_envgov.py tokyo -t 20190801 --read-html-file hoge.html 
    python get_wbgt_envgov.py tokyo -t 20190801 --save-html-file hoge.html
