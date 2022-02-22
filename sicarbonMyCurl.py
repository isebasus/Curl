import argparse
import textwrap
import socket
import string
import sys
import re
from urllib.request import urlopen

# REGEX PATTERNS --------------------------------------------------------------------
hostname_pattern = "([a-z]+\.[a-zA-Z0-9]+\.[a-z]+)"
domain_pattern = "([a-zA-Z0-9]+\.[a-z]+)"
ip_pattern = "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"

# Command Line colors ---------------------------------------------------------------
# 
# Resource:
# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
#
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ERROR MESSAGES --------------------------------------------------------------------
ERR1 = bcolors.FAIL + "ERROR: Invalid hostname or ip was given." + bcolors.ENDC
def err2(e): 
    return bcolors.FAIL + "ERROR: " + str(e) + bcolors.ENDC
def err3(addr, e):
    return bcolors.FAIL + "ERROR: something's wrong with " + str(addr) + " Exception is " + str(e) + bcolors.ENDC

class Socket:
    def __init__(self, hostname, ip, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5)
        self.ip = ip
        self.hostname = hostname
        self.port = int(port)
        self.addr = (hostname, int(port))
        self.connect()
    def connect(self):
        # Get and validate ip and port
        try:
            ip = socket.gethostbyname(self.hostname)
            if (self.ip != "" and self.ip != ip):
                self.client.close()
                sys.exit(ERR1)
            self.ip = str(ip)
            self.addr = (self.hostname, self.port)
        except Exception as e:
            self.client.close()
            sys.exit(err2(e))
        try:
            self.client.connect((self.hostname, self.port))
            print("connection sucessful")
        except Exception as e:
            self.client.close()
            sys.exit(err3(self.addr, e))
    def getData(self):
        try:
            self.client.sendall(b"HEAD / HTTP/1.1\r\nHost: "+ str.encode(self.hostname) +"\r\nAccept: text/html\r\n\r\n")
            print(str(self.client.recv(1024), 'utf-8'))
        except Exception as e:
            self.client.close()
            sys.exit(err3(self.addr, e))
    def close(self):
        self.client.close()


# parseUrl
# 
# Description: used to parse URL for valid
# input from the user
#
def parseUrl(args, parser):
    url = args.url
    urlObject = {
        'hostname': None, 
        'ip': None,
        'port': None,
        'url': None,
        'query': None,
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
    hostname = re.findall(hostname_pattern, url)
    domain = re.findall(domain_pattern, url)
    ip = re.findall(ip_pattern, url)
    query = ""
    if (len(hostname) == 0 and len(domain) == 0):
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
        if (len(hostname) == 0):
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

    # Create new URL
    if (urlObject["ip"] == None):
        urlObject["url"] = "http://" + urlObject["hostname"] + urlObject["query"]
    else:
        urlObject["url"] = "http://" + urlObject["ip"] + urlObject["query"]
    return urlObject

# main
# 
# Description: used to parse user
# arguments from command line
#
def main():
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
    args = parser.parse_args()
    urlObject = parseUrl(args, parser)
    print(urlObject)
    ip = ""
    if (urlObject["ip"] != None):
        ip = urlObject["ip"]
    socket = Socket(urlObject["hostname"], ip, urlObject["port"])
    socket.getData()
    socket.close()

if __name__ == "__main__":
    main()
