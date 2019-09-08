import urllib
import io

class AnywhereFile:
    def __init__(self, path):
        if path.startswith('https://'):
            with urllib.request.urlopen( path ) as data:
                self.data = io.BytesIO( data.read() ) 
        else:
            with open( path, "rb" ) as data:
                self.data = io.BytesIO( data.read() ) 
