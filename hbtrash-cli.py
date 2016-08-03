#!/usr/bin/env python
# -*- coding: utf-8 -*-
from libhbtrash.libhbtrash import Muellplan
import getopt
import sys



def usage():
    text = """usage:
        -S	--street	street name
        -N	--number	street number
        -O	--other		other number
        -A	--alarm		alarm time
        -h	--help		help"""
    print(text)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "S:N:O:A:h", ["street=","number=","other=","alarm=","help"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    street = ""
    number = ""
    other = ""
    alarm = ""
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
        else:
            assert False, "unhandled option"

    if street != ""  and number!= "" :
        m = Muellplan(street, number, other, alarm)

if __name__ == "__main__":
    main()
