
import json

def read_config( fname ):
    try:
        ifile = open( fname, 'r' )
        try:
            data = json.load( ifile )
            return data
        except ValueError as e:
            print "Invalid json file \"%s\": %s" % (fname, e)
    except IOError as e:
        print "Can't open config file ", fname
    return None

if __name__ == "__main__":
    import sys
    data = read_config( sys.argv[1] )
    if data:
        for key in data:
            print "Key: %s, Value: %s" % (key, data[key])

