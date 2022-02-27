# Sebastian Carbonero
# sicarbon
# Final Project
# © 2022

import argparse
import textwrap
import socket
import sys
import re

"""Definitions"""
HTTP_DELIMITER = b'\r\n\r'
CONTENT_LENGTH = b'Content-Length:'
SUCCESS_DELIMITER = b'HTTP/1.1 200 OK'
CHUNK_DELIMITER = b'Transfer-Encoding: chunked'
BUFFER_LENGTH = 1
TIMEOUT = 10

"""Regex Patterns"""
HOSTNAME_PATTERN = "([a-z]+\.[a-zA-Z0-9]+\.[a-z]+)"
DOMAIN_PATTERN = "([a-zA-Z0-9]+\.[a-z]+)"
IP_PATTERN = "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"

"""Command Line Colors"""
class bcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

"""Error Messages"""
ERR1 = bcolors.FAIL + "ERROR: Invalid hostname or ip was given." + bcolors.ENDC
ERR4 = bcolors.FAIL + "ERROR: Chunk encoding is not supported" + bcolors.ENDC
def err2(e): 
    return bcolors.FAIL + "ERROR: " + str(e) + bcolors.ENDC
def err3(addr, e):
    return bcolors.FAIL + "ERROR: something's wrong with " + str(addr) + " Exception is " + str(e) + bcolors.ENDC

"""
# parseUrl
# 
# This function is used to parse the
# User input.
# 
# Functions:
# - Checks if http is within substring
# - Checks if there is a hostname or ip
# - Checks for a port specified by the
#   user 
"""
def parseUrl(args, parser):
    url = args.url
    urlObject = {
        'hostname': None, 
        'ip': None,
        'port': None,
        'query': None,
        'url': url,
        'listHeader': args.l
    }

    # Check if user input for http is correct
    http = url[0:4]
    if (http != "http"):
        parser.print_help()
        sys.exit(bcolors.FAIL + "Exception: http needs to be specified." + bcolors.ENDC)
    colon_slash = url[4:7]
    if (colon_slash != "://"):
        parser.print_help()
        sys.exit(bcolors.FAIL + "Exception: HTTPS is not supported." + bcolors.ENDC)
    
    # Check for hostname or IP
    hostname = re.findall(HOSTNAME_PATTERN, url)
    domain = re.findall(DOMAIN_PATTERN, url)
    ip = re.findall(IP_PATTERN, url)
    hostOrDomain = url[7:]
    query = ""

    if (not len(domain) == 0 and not hostOrDomain.startswith(domain[0])) or len(domain) == 0:
        domain = None
    if (not len(hostname) == 0 and not hostOrDomain.startswith(hostname[0])) or len(hostname) == 0:
        hostname = None

    if (hostname == None and domain == None):
        if (len(ip) == 0):
            parser.print_help()
            sys.exit(bcolors.FAIL + "Exception: No host name or IP was specified." + bcolors.ENDC)
        if (args.hostname == None):
            parser.print_help()
            sys.exit(bcolors.FAIL + "Exception: IP needs hostname." + bcolors.ENDC)
        urlObject["hostname"] = args.hostname
        urlObject["ip"] = ip[0]
        query = url.replace("http://" + ip[0], "", 1)
    else:
        name = ""
        if (hostname == None or len(hostname) == 0):
            name = domain[0]
        else:
            name = hostname[0]
        urlObject["hostname"] = name
        query = url.replace("http://" + name, "", 1)
    
    # Check for port
    if (len(query) != 0):
        if (query[0] == ":"):
            count = 0
            for c in query:
                if count == 0:
                    count+=1
                    continue
                if not c.isdigit():
                    break
                count+=1
            if count == 0:
                parser.print_help()
                sys.exit(bcolors.FAIL + "Exception: No port was specified." + bcolors.ENDC)
            urlObject["port"] = query[1:count]
            urlObject["query"] = query[count:]
        else:
            urlObject["port"] = "80"
            urlObject["query"] = query
    return urlObject

"""
# Http
# 
# This class is used to create sockets
# and connect to other hosts to perform 
# HTTP requests.
# 
# Functions:
# - Connects to client
# - Sends a request
# - Parses Header for data
# - Fetches HTTP GET request body
"""
class Http:
    """Socket class to perform HTTP requests to hosts"""

    def __init__(self, hostname, ip, port, query, url):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.url = url
        self.port = int(port)
        self.query = query
        self.hostname = hostname
        self.content_length = 0
        self.http_status = ""
        self.useIp = False
        self.header = bytes()
        self.addr = (hostname, int(port))
        self.client.settimeout(TIMEOUT)
        self.connect()

    def connect(self):
        """Creates a new socket connection to a host either using
        IP or hostname"""
        try:
            ip = socket.gethostbyname(self.hostname)
            if (self.ip != "" and self.ip != ip):
                self.client.close()
                sys.exit(ERR1)
            if (self.ip != ""):
                self.useIp = True
            self.ip = str(ip)
            self.addr = (self.hostname, self.port) if self.useIp == False else (self.ip, self.port)
        except Exception as e:
            self.client.close()
            sys.exit(err2(e))
        try:
            self.client.connect(self.addr)
        except Exception as e:
            self.client.close()
            sys.exit(err3(self.addr, e))

    def send_request(self):
        """Used to send a HTTP request to the host, if there was an 
        error in the HTTP request, we would log that error."""
        try:
            get = "GET " + self.query + " HTTP/1.1\r\nHost: "+ self.hostname +"\r\n\r\n"
            b = get.encode('utf-8')
            self.client.sendall(b)
        except Exception as e:
            self.client.close()
            sys.exit(err3(self.addr, e))
        self.get_header()

    def get_header(self):
        """Used to fetch the header from the server. The client will
        get bytes one by one until we find the HTTP_DELIMITER. Once
        we find that, we have fetched the HTTP request header."""
        try: 
            while True:
                chunk = self.client.recv(BUFFER_LENGTH)
                if (chunk == None or HTTP_DELIMITER in self.header):
                    break
                self.header += chunk
        except Exception as e:
            self.client.close()
            sys.exit(err2(e))
        self.read_header()

    def read_header(self):
        """Used to parse the header and check if there were any errors
        and also obtains the content length of the request body."""
        i = 0
        for param in self.header.split(b'\r\n'):
            if i == 0 and SUCCESS_DELIMITER not in param:
                self.http_status = param.decode("utf-8")
                self.status(False)
                self.log("Unsuccessful")
                self.client.close()
                quit()
            elif i == 0:
                self.http_status = param.decode("utf-8")
                self.status(True)
            if (CONTENT_LENGTH in param):
                self.content_length = int(param[len(CONTENT_LENGTH):])
            if (CHUNK_DELIMITER in param):
                self.http_status = "HTTP/1.1 400 Bad Request"
                self.log("Unsuccessful")
                self.client.close()
                quit(ERR4)
            i+=1
    
    def content(self):
        """This function is used to receive the content in chunks
        and write the HTML output to HTTPoutput.html"""
        try: 
            index = 0
            f = open("HTTPoutput.html", "w")
            while True:
                if (index == self.content_length):
                    break
                tmp = self.client.recv(1024)
                f.write(tmp.decode("utf-8"))
                index += len(tmp)
            f.close()
        except Exception as e:
            self.client.close()
            sys.exit(err2(e))

    def log(self, status):
        """Used to log information about the HTTP request."""
        f = open("Log.csv", "a")
        src_ip, src_port = self.client.getsockname()
        status_code = [int(word) for word in self.http_status.split() if word.isdigit()][0]
        info = (
            status + ", " + str(status_code) + ", " + self.url + ", " + self.hostname + ", " + 
            src_ip + ", " + self.ip + ", " + str(src_port) + ", " + str(self.port) + ", " + 
            self.http_status
        )
        f.write(info + "\n\n")
        f.close()

    def status(self, is_success):
        """Used to print the status of the HTTP request to terminal."""
        if (is_success):
            print(bcolors.OKGREEN + "Success " + self.url + " " + self.http_status + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "Unsuccessful " + self.url + " " + self.http_status + bcolors.ENDC)

    def close(self):
        """Used to close the socket."""
        self.client.close()

"""
# main
# 
# Initially parses the user input with
# argparse and creates the object Http
# to handle requests. 
# HTTP requests.
"""
def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        prog='sicarbonMyCurl', 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Curl Replication Program
            --------------------------------
                A Curl Replication for
                users to request HTML
                documents from hosts.
            '''))
    parser.add_argument("url", help='http://hostname[ip]:[port]/[args]')
    parser.add_argument("hostname", nargs='?', help="Optional hostname argument")
    parser.add_argument('-l', default=False, action='store_true', help="List Header Information.")
    if (len(sys.argv) < 2):
        parser.print_help()
        quit()

    # Parse user input
    args = parser.parse_args()
    urlObject = parseUrl(args, parser)
    ip = ""
    query = "/"
    port = "80"
    if (urlObject["ip"] != None):
        ip = urlObject["ip"]
    if (urlObject["query"] != "" and urlObject["query"] != None):
        query = urlObject["query"]
    if (urlObject["port"] != None):
        port = urlObject["port"]

    # Create HTTP object
    http = Http(urlObject["hostname"], ip, port, query, urlObject["url"])
    http.send_request()
    http.content()

    # On success, log and close
    http.log("Success")
    http.close()

if __name__ == "__main__":
    main()
