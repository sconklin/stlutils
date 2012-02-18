import struct
from sys import argv

normals = []
points = []
triangles = []
bytecount = []

fb = [] # debug list

def binary_unpack (f, sig, l):
    s = f.read (l)
    fb.append(s)
    return struct.unpack(sig, s)

def binary_read_triangle(f):
    n = unpack(f,"<3f", 12)
    p1 = unpack(f,"<3f", 12)
    p2 = unpack(f,"<3f", 12)
    p3 = unpack(f,"<3f", 12)
    b = unpack(f,"<h", 2)

    print "Normal: %f %f %f" % (n[0], n[1], n[2])
    print "P1:     %f %f %f" % (p1[0], p1[1], p1[2])
    print "P2:     %f %f %f" % (p2[0], p2[1], p2[2])
    print "P3:     %f %f %f" % (p3[0], p3[1], p3[2])

def binary_read_length(f):
    length = struct.unpack("@i", f.read(4))
    return length[0]

def read_header(f):
    f.seek(80)

def is_it_binary(f):
    retval = False
    pos = f.tell()

    # Try to determine whether this is in binary or ascii format
    f.seek(0)

    # If the first line doesn't start with "solid " it is binary
    tststr = "solid "
    solidtest = f.read(len(tststr))
    if solidtest != tststr:
        retval = True

    # It could still be binary, as first 80 bytes is comment in a binary file
    # each facet is 50 bytes, read one and test it to see if it's all ascii
    f.seek(80)
    facet = f.read(50)
    if not all(ord(c) < 128 for c in facet):
        retval = True

    f.seek(pos)
    return retval

def main():
    infilename = argv[1]

    try:
        f = open ( infilename, "rb")

        binary = is_it_binary(f)
        if binary:
            print "File is in binary format"
        else:
            print "File is in Ascii format"
        return

        read_header(f)
        l = read_length(f)
        try:
            while True:
                read_triangle(f)
        except Exception, e:
            print "Exception",e[0]
        print len(normals), len(points), len(triangles), l
        write_as_ascii()

    except Exception, e:
        print e

if __name__ == '__main__':
    main()
