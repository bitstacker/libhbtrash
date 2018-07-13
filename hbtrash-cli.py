#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from libhbtrash.libhbtrash import Muellplan

def usage():
    text = """usage:
        -S	--street	street name
        -N	--number	street number
        -O	--other		other number
        -A	--alarm		time when the alarm is displayed, in minutes
        				(time before, 0 is exactly at 0:00)
        -n      --next          get only next event in json
        -h	--help		help"""
    print(text)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "S:N:O:A:hn", ["street=","number=","other=","alarm=","help","next"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    street = ""
    number = ""
    other = ""
    alarm = ""
    onlynext = False
    for o, a in opts:
        if o in ("-S", "--street"):
            street = a
        elif o in ("-N", "--number"):
            number = a
        elif o in ("-O", "--other"):
            other = a
        elif o in ("-A", "--alarm"):
            alarm = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-n", "--next"):
            onlynext = True
        else:
            assert False, "unhandled option"

    if street != ""  and number!= "" :
        m = Muellplan()
        if onlynext:
            print(m.getNextDateJson(street, number, other))
        else:
            print(m.getIcal(street, number, other, alarm))

if __name__ == "__main__":
    main()
