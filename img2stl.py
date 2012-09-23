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

from   STL            import STL
import os
import Image
from   ImageChops     import invert
from   ImageOps       import expand

from sys              import argv, exit
from getopt           import getopt, GetoptError
#from datetime        import datetime, date

# Treat every image as greyscale, convert if needed
# --geometry=XSIZExYSIZE
# --thickest=
# --thinnest=
# --border=
# --invert-thickness
# --twotone (only two levels)
# --threshhold=
#
# By default, thickest is darkest


class IMG2STL():

    def __init__(self):
        self.debug = False
        # Sizes are in mm
        self.xsize = 80
        self.ysize = 80
        self.pointspermm = 4
        self.thickest = 4.0
        self.thinnest = 0.2
        self.geometry = False
        self.border = 3
        self.pad = False
        self.invert = False
        self.twotone = False
        self.threshhold = None
        self.infile = ""
        self.outfile = ""
        self.inputImage = None
        self.outfp = None
        self.outputType = 'ascii'
        return

    def usage(self, myname):
        print "                                                                                             \n",
        print "    %s                                                                                       \n" % argv[0],
        print "        Processes an image, and generates a .stl file based on that image.                   \n",
        print "    Usage:                                                                                   \n",
        print "        %s [options] <imagefile> <outputfile>                                                \n" % argv[0],
        print "                                                                                             \n",
        print "    Options:                                                                                 \n",
        print "        --help                           Prints this text.                                   \n",
        print "        --geometry=XSIZExYSIZE           Sets the size of the output in mm                   \n",
        print "        --thickest=<thickness>           The thickest output in mm                           \n",
        print "        --thinnest=<thickness>           The thinnest output in mm                           \n",
        print "        --border=<width>                 Output border in mm (defaults to 3)                 \n",
        print "        --invert-thickness               Make darkest parts of the image the thinnest output \n",
        print "        --twotone                        Only make two output levels                         \n",
        print "        --threshhold=<%>                 The image brighness % for twotone                   \n",
        print "                                                                                             \n",
        print "    Examples:                                                                                \n",
        print "        %s infile.bmp outfile.stl                                                            \n" % argv[0],

    def dump_image_info(self, show=False):
        print "Image Format: ", self.inputImage.format
        print "Image Size:   ", self.inputImage.size
        print "Image Mode:   ", self.inputImage.mode
        if show:
            print "Displaying image in separate window"
            self.inputImage.show()

    def z_val(self, pixel_value):
        """
        Scale the Z value, so that the darkest part of the image is the thickest
        and the lightest part is the thinnest
        """
        result = self.thickest - (float(pixel_value)*(self.thickest-self.thinnest))/255.0
        return result
    
    def convert_for_output(self):
        in_x_pixels = self.inputImage.size[0]
        in_y_pixels = self.inputImage.size[1]
        border_pixels = self.border*self.pointspermm
        output_max_x_pixels = self.xsize*self.pointspermm - border_pixels
        output_max_y_pixels = self.ysize*self.pointspermm - border_pixels

        if self.debug:
            print "Converting for output:"
            print "  output pixels per mm: ", self.pointspermm
            print "  input size: %dx%d pixels" % (in_x_pixels,in_y_pixels)
            print "  border pixels: ", border_pixels
            print "  output max size: %dx%d pixels" % (output_max_x_pixels, output_max_y_pixels)

        # Resize if needed
        if (in_x_pixels > output_max_x_pixels) or (in_y_pixels > output_max_y_pixels):
            # We have to reduce the image resolution
            xratio = float(output_max_x_pixels)/float(in_x_pixels)
            yratio = float(output_max_y_pixels)/float(in_y_pixels)
            if xratio < yratio:
                newxsize = output_max_x_pixels
                newysize = int(float(self.inputImage.size[1]) * xratio)
            else:
                newysize = output_max_y_pixels
                newxsize = int(float(self.inputImage.size[0]) * yratio)

            if self.debug:
                print "  Resizing to %dx%d pixels" % (newxsize, newysize)
            self.inputImage = self.inputImage.resize((newxsize,newysize))

        if self.twotone:
            # We want a bicolor interpretation
            if self.inputImage.mode != "1":
                if self.debug:
                    print "  Converting to bicolor"
                self.inputImage = self.inputImage.convert("1")
        else:
            # Change to grayscale if needed
            if self.inputImage.mode != "L":
                if self.debug:
                    print "  Converting to grayscale"
                self.inputImage = self.inputImage.convert("L")

        if self.border > 0:
            if self.debug:
                print "  Adding border of %d pixels" % border_pixels
            self.inputImage = expand(self.inputImage, border_pixels)

        if self.invert:
            if self.debug:
                print "  Inverting image tones"
            self.inputImage = invert(self.inputImage)

        if self.debug:
            print "Extrema: ", self.inputImage.getextrema()

        return

    def generate_stl_from_image(self):
        maxInX = self.inputImage.size[0]
        maxInY = self.inputImage.size[1]
        pix = self.inputImage.load()
        Xorigin = -1*(self.xsize/2) # in mm
        Yorigin = -1*(self.ysize/2) # in mm
        Xmax = self.xsize
        Ymax = self.ysize
        Zmax = self.thickest

        # create bottom face of the whole thing
        self.stl.addFace([[Xorigin,Yorigin,0],[Xorigin, Ymax,0],[Xmax, Ymax, 0],[Xmax, 0, 0]])
        # TODO - Y in STL is inverted from image

        # if there's a border, then the side faces are all the same height
        if self.border > 0:
            # Create left side face
            self.stl.addFace([[Xorigin,Ymax,0],[Xorigin,Ymax,pix[0,0]],[Xorigin,Yorigin,pix[0,maxInY], [Xorigin,Yorigin,0]])
            #self.stl.addFacet([[x,y,0],[x,y,z],[x,y,z]])
            # Create right side face
            # Create bottom side face
            # Create top side face
        else:
            # Create left side face
            # Create right side face
            # Create bottom side face
            # Create top side face
    

        #addFacet(self, p, n=[0.0,0.0,0.0], a=0):

        # Walk through all pixels except the outside perimeter, adding triangles
        return

    def process_command_line(self):
        try:
            pname = os.path.basename(argv[0])
            optsShort = ''
            optsLong  = ['help', 'geometry=', 'thickest=', 'thinnest=', 'border=', 'invert-thickness', 'twotone', 'threshhold=', 'binary-stl']
            opts, args = getopt(argv[1:], optsShort, optsLong)

            for opt, val in opts:
                if (opt == '--help'):
                    self.usage(pname)
                    exit()
                elif opt in ('--geometry'):
                    parts = val.split('x')
                    try:
                        self.xsize = int(parts[0])
                        self.ysize = int(parts[1])
                        self.geometry=True
                    except:
                        raise ValueError("Invalid specification of --geometry parameter (should be XXXXxYYYY integers)")
                elif opt in ('--thickest'):
                    try:
                        self.thickest = float(val)
                    except:
                        raise ValueError("Invalid specification of --thickest parameter (should be a float)")
                elif opt in ('--thinnest'):
                    try:
                        self.thinnest = float(val)
                    except:
                        raise ValueError("Invalid specification of --thinnest parameter (should be a float)")
                elif opt in ('--border'):
                    try:
                        self.border = int(val)
                    except:
                        raise ValueError("Invalid specification of --border parameter (should be an int)")
                elif opt in ('--invert-thickness'):
                    self.invert = True
                elif opt in ('--twotone'):
                    self.twotone = True
                elif opt in ('--threshhold'):
                    try:
                        self.threshhold = int(val)
                    except:
                        raise ValueError("Invalid specification of --threshhold parameter (should be an int between 1 and 99)")
                    if (self.threshhold < 1) or  (self.threshhold > 99):
                        raise ValueError("Invalid specification of --threshhold parameter (should be an int between 1 and 99)")
                elif opt in ('--binary-stl'):
                    self.outputType = 'binary'

            if len(args) < 2:
                raise ValueError("You must supply input and output file names")

            if len(args) > 2:
                raise ValueError("Too many command line arguments")

            self.infile = args[0]
            self.outfile = args[1]

            self.inputImage = Image.open(self.infile)

            self.stl = STL(outfile=self.outfile)
            self.stl.setOutputType(self.outputType)

        except ValueError as ex:
            print 'Error: ', ex
            self.usage(pname)
            exit()

#================================================================

def main():

    i2s = IMG2STL()
    i2s.debug = True
    i2s.process_command_line()
    i2s.convert_for_output()
    i2s.dump_image_info(show=False)
    i2s.generate_stl_from_image()

    exit()
    infilename = 'foo'
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
