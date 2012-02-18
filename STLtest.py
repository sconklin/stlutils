#!/usr/bin/env python

import STL
from sys             import argv

def main():
    infilename = argv[1]

    try:
        stl = STL.STL(infilename)
        #stl.debug = True

        type = stl.type()
        print "Type is: ", type
        if type == "binary":
            print "Length is: ", stl.length()
            print "Header:"
            print stl.header()

        stl.read()
        stl.dump()

    except Exception, e:
        print e

if __name__ == '__main__':
    main()
