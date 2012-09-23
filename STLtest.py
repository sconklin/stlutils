#!/usr/bin/env python
#
# Copyright (C) 2012 Steve Conklin
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation version 3.
#
# This program is distributed "as is" WITHOUT ANY WARRANTY of any kind,
# whether express or implied; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#

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
