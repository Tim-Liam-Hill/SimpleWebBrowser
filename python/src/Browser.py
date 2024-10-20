import socket
import sys
import ssl

#Given a url performs a DNS lookup
#Only accepts http protocol urls.
class URL:
    SUPPORTED_SCHEMES ["http","https","data","file","view-source"]
    
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]
        
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        self.requestHeaders = []
    
    #given a string url, extracts the http scheme. Throw error if invalid scheme
    #https://developer.mozilla.org/en-US/docs/Web/URI/Schemes
    #'The scheme of a URI is the first part of the URI, before the : character.'
    def extractScheme(self, url):
        self.scheme = url.split(":",1)[0]
        if ! scheme in 


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
    load(URL(sys.argv[1]))
    