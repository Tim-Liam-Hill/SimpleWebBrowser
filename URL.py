import socket

#Given a url performs a DNS lookup
#Only accepts http protocol urls.
class URL:
    PORT = 80
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, PORT))

        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        s.send(request.encode("utf8")) #hardcoding utf 8 here technically isn't an issue

        response = s.makefile("r", encoding="utf8", newline="\r\n") #We should actually be extracting the encoding from the response instead of hardcoding
        #TODO: in the above, extract encoding before using makefile
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)


        #to test different encodings, can use https://en.wikipedia.org/wiki/Tiger_I for gzip encoding (make sure to enable it in request headers)

if __name__ == "__main__":
    url = URL("http://google.com")
