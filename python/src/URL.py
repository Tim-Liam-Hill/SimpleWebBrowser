import socket
import sys
import ssl
import re
from urllib.parse import unquote

DATA_REGEX = '^data:(.*)(;base64)?,(.*)$'
FILE_REGEX = '^file://((\/[\da-zA-Z\s\-_\.]+)+)|([A-Za-z0-9]:(\\\\[a-za-zA-Z\d\s\-_\.]+)+)$'
URL_REGEX = '^([A-Za-z0-9]+\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+(\.([a-zA-Z]){2,6})?([a-zA-Z0-9\.\&\/\?\:@\-_=#])*$'

class URL:
    """Given a url, extracts scheme and returns data based on the protocol
    NEED TO MAKE SURE THAT VIEWSOURCE IS SET/CHECKED SOMEHOW
    There will be a different class responsible for parsing the html into a syntax
    tree I suppose, so that will be the thing that needs to take notice."""
    DEFAULT_PAGE = 'https://timhill.co.za'
    
    def __init__(self, url = DEFAULT_PAGE):
        #All class variables
        self.viewSource = False 
        self.scheme = ""
        self.port = 0
        self.host = ""
        self.path = ""
        self.requestHeaders = []
        self.cache = None
        ##---------------------

        if not self.validateURL(url):
            raise ValueError("Input URL is not of a valid format")        

        self.scheme, url = self.extractScheme(url)
        self.path = url 

        #if we really wanted to make this extensible, we would have a strategy pattern or something similar
        #to make it easier to support new schemes. I don't feel like overengineering this though:
        #I know exactly what I am supporting and the list is short
    
    #Validates whether or not the input url is valid.
    def validateURL(self, url):
        if re.search(URL_REGEX, url):
            return True
        #data
        if re.search(DATA_REGEX, url):
            return True 
        if re.search(FILE_REGEX,url):
            return True

        return False 
    
    #given a string url, extracts the http scheme. Throw error if invalid scheme. Returns scheme and 
    #url without scheme
    #https://developer.mozilla.org/en-US/docs/Web/URI/Schemes
    #'The scheme of a URI is the first part of the URI, before the : character.'
    def extractScheme(self, url):
        err = "Input url %s does not contain a supported scheme\n"%(url)
        err += "Accepted schemes are: \n\thttp\n\thttps\n\tfile\n\tdata\n\tview-source\n"

        scheme = url.split(":",1)[0]
        if scheme.lower() in ["http","https", "file"]:
            url = url.split("://",1)[1]
            return scheme.lower(), url 
        elif scheme.lower() in ["data"]:
            url = url.split(":",1)[1]
            return scheme.lower(), url 
        elif scheme.lower() == "view-source":
            if self.viewSource: #stops multiple view-source:view-source from being valid
                raise ValueError(err)
            self.viewSource = True 
            junk, url = scheme = url.split(":",1)
            return self.extractScheme(url)
        else: 
            raise ValueError(err)



    #Makes an HTTP/HTTPS connection to the host and fetches data
    def request(self):
        match self.scheme:
            case "file":
                return self.fileRequest()
            case "http":
                return self.httpRequest()
            case "https":
                return self.httpRequest()
            case "data":
                return self.dataRequest()
    
    #Doesn't handle the OSError, that can be handled by lower down (or maybe we will figure it out
    #eventually
    def fileRequest(self):
        content = ""
        with open(self.path, "r") as f:
            content = f.read()
        return content 
        
    

    def dataRequest(self):
        #so we have 2 main cases:
        #base64 or not base64
        #we also need to support a bunch of different charsets don't we. REEEEEEEEE
        #https://datatracker.ietf.org/doc/html/rfc2045 may help
        print(self.path)
        preamble, data = self.path.split(",",1)
        
        #default to plain text mediatype with URL encoded string 
        if preamble == "":
            return unquote(data)

        return ""

    def httpRequest(self):

        #TODO: setup caching 
        if "/" not in self.path:
            self.path = self.path + "/"
        self.host, self.path = self.path.split("/", 1)
        self.path = "/" + self.path
        
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context() #default good enough for most use cases
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        s.send(request.encode("utf8")) #hardcoding utf 8 here technically isn't an issue
        #TODO: send headers related to encodings so we can get gzipped/either compressions and handle them
        #to test different encodings, can use https://en.wikipedia.org/wiki/Tiger_I for gzip encoding (make sure to enable it in request headers)


        response = s.makefile("r", encoding="utf8", newline="\r\n") #We should actually be extracting the encoding from the response instead of hardcoding
        #TODO: in the above, extract encoding before using makefile to make sure we actually get the content decoded correctly
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers #Remove/change once we send header for accepted encodings
        assert "content-encoding" not in response_headers #Or is it this one, I am not too sure. Either way, do it son

        content = response.read()
        s.close()
        return content


def show(body, viewSource):

    if viewSource:
        print(body)
        return

    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")
        
def load(url):
    body = url.request()
    show(body, url.viewSource)

if __name__ == "__main__":
    url = URL(sys.argv[1])
    load(url)
    
