import socket
import sys
import ssl
import re
from urllib.parse import unquote
import gzip
from http import HTTPStatus
import time
from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)

class URLCache:

    LIMIT = 1
    def __init__(self):
        self.order = []
        self.mapping = {}
    
    def put(self, key, val, maxAge):
        logger.info("Caching response for host %s for %d seconds", key, maxAge)
        if(len(self.order) == URLCache.LIMIT):
            logger.info("Cache full, evicting LRU %s", self.order[URLCache.LIMIT-1])
            del self.mapping[self.order[URLCache.LIMIT-1]]
            self.order.pop()
        expiry = time.time() + maxAge
        self.order.insert(0, key)
        self.mapping[key] = {"expiry": expiry, "content": val}
    
    def get(self, key):
        
        if key in self.mapping:
            currTime = time.time()
            if currTime >= self.mapping[key]["expiry"]:
                logger.info("%s has value in cache but has expired", key)
                del self.mapping[key]
                self.order.remove(key)
            else: return self.mapping[key]["content"]

        #check if time elapsed
        logger.info("Cache miss for %s", key)
        raise ValueError("Cache Miss")
    
DATA_REGEX = '^data:(.*)(;base64)?,(.*)$'
FILE_REGEX = '^file://((\/[\da-zA-Z\s\-_\.]+)+)|([A-Za-z0-9]:(\\\\[a-za-zA-Z\d\s\-_\.]+)+)$'
URL_REGEX = '^([A-Za-z0-9]+\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+(\.([a-zA-Z]){2,6})?([a-zA-Z0-9\.\&\/\?\:@\-_=#])*$'

class URLHandler:
    """Given a url, extracts scheme and returns data based on the protocol
    NEED TO MAKE SURE THAT VIEWSOURCE IS SET/CHECKED SOMEHOW
    There will be a different class responsible for parsing the html into a syntax
    tree I suppose, so that will be the thing that needs to take notice."""
    DEFAULT_PAGE = 'https://timhill.co.za'
    HTTP_VERSION = 'HTTP/1.1'
    MAX_REDIRECTS = 7
    
    #To make more extensible, we can take in options here EG: options related to headers n such 
    def __init__(self):
        #All class variables

        self.redirectCount = 0
        self.requestHeaders = [
            ["Connection", "Keep-alive"],
            ["User-Agent","Meow-Meow-Browser24"],
            ["Accept-Encoding","gzip"]
        ]
        self.connections = {}
        self.cache = URLCache()
        ##---------------------

        #if we really wanted to make this extensible, we would have a strategy pattern or something similar
        #to make it easier to support new schemes. I don't feel like overengineering this though:
        #I know exactly what I am supporting and the list is short
    
    def __del__(self):
        #clean up active connections my son. 
        for key, val in self.connections.items():
            val.close()
    
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
    
    #used to resovle relative urls to the actual url to request
    #resources from. 
    def resolve(self, url, baseURL):

        if not self.validateURL(url):
            raise ValueError("Input URL '{}' is not of a valid format".format(url))      

        scheme, path = self.extractScheme(baseURL) 

        if "/" not in path:
            path = path + "/"
        host, path = path.split("/", 1)
        path = "/" + path

        if scheme == "http":
            port = 80
        elif scheme == "https":
            port = 443
        
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        if "://" in url: return url
        if not url.startswith("/"):
            dir, _ = path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        if url.startswith("//"):
            return scheme + ":" + url
        else:
            return scheme + "://" + host + ":" + str(port) + url
    #given a string url, extracts the http scheme. Throw error if invalid scheme. Returns scheme and 
    #url without scheme
    #https://developer.mozilla.org/en-US/docs/Web/URI/Schemes
    #'The scheme of a URI is the first part of the URI, before the : character.'
    #isViewSource is used to keep track of whether or not we are already in 'view-source' between recursive calls
    def extractScheme(self, url, isViewSource = False):
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
            if isViewSource: #stops multiple view-source:view-source from being valid
                raise ValueError(err)
            junk, url = scheme = url.split(":",1)
            return self.extractScheme(url, True)
        else: 
            raise ValueError(err)

    def isViewSource(self, url):

        scheme = url.split(":",1)[0]
        return scheme.lower() == "view-source"

    #Makes a request based on the input URL. Make this the entry function and move shit from
    #constructor. Implement destructor
    def request(self, url = DEFAULT_PAGE, reset = True):

        if not self.validateURL(url):
            raise ValueError("Input URL is not of a valid format")        

        if reset: #TODO: document why this is here. I know it relates to redirects and such
            self.resetBetweenRequest()
        scheme, path = self.extractScheme(url) #throws an error so match case doesn't need default case?


        match scheme:
            case "file":
                return self.fileRequest(path)
            case "http":
                return self.httpRequest(path, scheme)
            case "https":
                return self.httpRequest(path, scheme)
            case "data":
                return self.dataRequest(path)
    
    def resetBetweenRequest(self):
        self.viewSource = False 
        self.redirectCount = 0

    #Doesn't handle the OSError, that can be handled by lower down/higher up (or maybe we will figure it out
    #eventually
    def fileRequest(self, path):
        content = ""
        with open(path, "r") as f:
            content = f.read()
        return content 
        
    
    #https://http.dev/data-url
    #might need to hold off on implementing this until we know what later rendering is gonna look like
    #since all I can do right now is print characters to a screen
    #TODO: one thing I can do is return the html based on the content
    #eg: if it is an image or video, return img tag with the necessary nonsense set
    #that makes the most sense to me right now. 
    def dataRequest(self, path):
        #so we have 2 main cases:
        #base64 or not base64
        #we also need to support a bunch of different charsets don't we. REEEEEEEEE
        #https://datatracker.ietf.org/doc/html/rfc2045 may help
 
        preamble, data = path.split(",",1)
        
        #default to plain text mediatype with URL encoded string 
        if preamble == "":
            return unquote(data)

        return ""

    #eventually need to handle post requests. But that is a problem for later.
    def httpRequest(self, path, scheme):

        if "/" not in path:
            path = path + "/"
        host, path = path.split("/", 1)
        path = "/" + path

        try:
            content = self.cache.get(scheme + "://" + host + path)
            logger.info("Returning content from cache")
            return content
        except ValueError:
            pass
        
        if scheme == "http":
            port = 80
        elif scheme == "https":
            port = 443
        
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)
        
        s = self.getSocket(scheme, host, port)

        request = "GET {} {}\r\n".format(path, URLHandler.HTTP_VERSION) #may need to change eventually if we do POST requests. 
        request += "Host: {}\r\n".format(host)
        for headerPair in self.requestHeaders:
            request += headerPair[0] + ": " + headerPair[1] + "\r\n"
        request += "\r\n"
        logger.info(request)
        s.send(request.encode("utf8")) #hardcoding utf 8 here technically isn't an issue
        #TODO: send headers related to encodings so we can get gzipped/either compressions and handle them
        #to test different encodings, can use https://en.wikipedia.org/wiki/Tiger_I for gzip encoding (make sure to enable it in request headers)


        response = s.makefile("rb", encoding="utf8", newline="\r\n") #We should actually be extracting the encoding from the response instead of hardcoding
        #TODO: in the above, extract encoding before using makefile to make sure we actually get the content decoded correctly
        statusline = response.readline().decode("utf-8")
        version, status, explanation = str(statusline).split(" ", 2)
        
        response_headers = {}
        while True:
            line = response.readline().decode("utf-8")
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
            
        logger.info("STATUS: %s",status)
        logger.debug(response_headers)

        if str(HTTPStatus.MOVED_PERMANENTLY.value) in status:
            return self.handleRedirect(response_headers, scheme, host)
            
        if "transfer-encoding" in response_headers:
            content = self.handleTransferEncoding(response_headers, response)
        elif "content-length" in response_headers:
                content = response.read(int(response_headers["content-length"]))
        else: content = response.read()

        if "content-encoding" in response_headers:
            content = self.decodeBody(content, response_headers["content-encoding"])
        else: content = content.decode("utf-8")

        if 'cache-control' in response_headers:
            self.cacheResponse(content, response_headers, scheme, host, path)

        return content
    
    def cacheResponse(self, content, response_headers,scheme, host, path):
            directives = response_headers['cache-control'].split(", ")
            #https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control technically we can cache if no-cache 
            #is set but that complicates things so let's just make things simple. 
            noCache = [s for s in directives if 'no-cache' in s or 'no-store' in s]
            logger.debug(directives)
            arr = [s for s in directives if "max-age" in s]
            if len(arr) != 0 and len(noCache) == 0:
                maxAge = int(arr[0].split("=")[1])
                self.cache.put(scheme + "://" + host + path, content, maxAge) #may need to change eventually if we do POST requests
            #elif 'Expires' #TODO: use 'Expires' header if maxAge is missing

    
    def handleRedirect(self, response_headers, scheme, host):
        if self.redirectCount == URLHandler.MAX_REDIRECTS:
            return "<html><body>Maximum redirect limit reached</body></html>"
        newLoc = response_headers["location"]
        logger.info("Redirecting to {}".format(newLoc))
        self.redirectCount += 1

        try: #need to check if absolute or relative path provided
            return self.request(newLoc, False)
        except ValueError:
            return self.request("{}://{}{}".format(scheme,host,newLoc), False)
    
    def getSocket(self, scheme, host, port) -> socket.socket:
        key = "{}://{}".format(scheme, host)
        logger.info("Getting socket for {}".format(key))
        if key in self.connections:
            if not self.isSocketClosed(self.connections[key]):
                logging.info("Socket exists and is open, reusing")
                return self.connections[key]
            else: logger.info("Socket exists but is closed, recreating")
        else: logger.info("No socket exists for host yet, creating")
   
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((host, port))
        if scheme == "https":
            ctx = ssl.create_default_context() #default good enough for most use cases
            s = ctx.wrap_socket(s, server_hostname=host)
        
        self.connections[key] = s 
        return s

    #https://stackoverflow.com/questions/48024720/python-how-to-check-if-socket-is-still-connected
    def isSocketClosed(self, sock: socket.socket) -> bool:
        try:
            # this will try to read bytes without blocking and also without removing them from buffer (peek only)
            data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
            if len(data) == 0:
                return True
        except BlockingIOError:
            return False  # socket is open and reading from it would block
        except ConnectionResetError:
            return True  # socket was closed for some other reason
        except Exception as e:
            logger.exception("unexpected exception when checking if a socket is closed")
            return False
        return False
    
    #generic decode function, takes in body (bytes to decode) and method of encoding
    #TODO: expand to handle more than just compression
    def decodeBody(self, body, method):
        #https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding
        #for now only dealing with gzip compression but deflate could be implemented (compress not really needed)
        match method:
            case 'gzip':
                return gzip.decompress(body).decode('utf-8') #TODO: this won't only be utf-8
            case default:
                err = "Unknown content-encoding in response header: " + method
                raise ValueError(err)

    def handleTransferEncoding(self, headers, response):
        body = b''
        if "chunked" in headers['transfer-encoding']: #pretty much the only thing worth checking
            logger.info("Reading in chunked body")
            while True:
                line = response.readline()
                count = int(line.decode("utf-8"), 16) #this tripped me up, the value is in HEXADECIMAL!!!
                if count == 0:
                    break
                
                next = response.read(count)
                if "gzip" in headers['transfer-encoding']:
                   body += self.decodeBody(next, "gzip")
                else: body += next
                empty = response.readline() #consume empty newline boi
            
        else: raise ValueError("Unknown transfer-encoding")

        return body

@dataclass
class Text:
    def __init__(self, text):
        self.text = text

@dataclass
class Tag:
    def __init__(self, tag):
        self.tag = tag

def lex(body, viewSource):

    if viewSource:
            return [Text(body)] #TODO: test that viewsource still works. 

    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out
        
def load(url):
    u = URL()
    if url == "":
        body = u.request()
    else: body = u.request(url)
    body = u.request('https://www.google.com')
    if url == "":
        body = u.request()
    else: body = u.request(url)
    print(lex(body, u.viewSource))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        load("")
    else: load(sys.argv[1])
    
