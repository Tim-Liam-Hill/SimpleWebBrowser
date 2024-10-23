import socket
import sys
import ssl
import re
import validators

DATA_REGEX = '^data:(.*)(;base64)?,(.*)$'
FILE_REGEX = '^file://((\/[\da-zA-Z\s\-_\.]+)+)|([A-Za-z0-9]:(\\\\[a-za-zA-Z\d\s\-_\.]+)+)$'
URL_REGEX = '^([A-Za-z0-9]+\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+(\.([a-zA-Z]){2,6})?([a-zA-Z0-9\.\&\/\?\:@\-_=#])*$'

class URL:
    """Given a url, extracts scheme and returns data based on the protocol
    NEED TO MAKE SURE THAT VIEWSOURCE IS SET/CHECKED SOMEHOW
    There will be a different class responsible for parsing the html into a syntax
    tree I suppose, so that will be the thing that needs to take notice."""
    
    def __init__(self, url):
        #All class variables
        self.viewSource = False 
        self.scheme = ""
        self.port = 0
        self.host = ""
        self.path = ""
        self.requestHeaders = []
        self.cache = None
        ##---------------------

        #url = url.lower() I don't think I can do this due to base64 strings and such. 
        if not self.validateURL(url):
            raise ValueError("Input URL is not of a valid format")
        

        self.scheme, url = self.extractScheme(url)

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        
        #TODO: setup caching 
    
    #Validates whether or not the input url is valid.
    def validateURL(self, url):
        print(url)
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
            if self.viewSource: #stops multiple view-source:view-source
                raise ValueError(err)
            self.viewSource = True 
            junk, url = scheme = url.split(":",1)
            return self.extractScheme(url)
        else: 

            raise ValueError(err)
    
    # DO THE SAME FOR EXTRACT PORT!!!!! 



    #Makes an HTTP/HTTPS connection to the host and fetches data
    def request(self):
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


def show(body):
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
    show(body)

if __name__ == "__main__":
    URL(sys.argv[1])
    
