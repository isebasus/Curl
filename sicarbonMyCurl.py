import argparse
import textwrap
import socket
import string
import sys
import re
from urllib.request import urlopen

# REGEX PATTERNS -----------------------------------------------------------------------------------------------------------------
# Rest of the patterns used from https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address
host_port = "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5})|([a-z]+\.[a-zA-Z0-9]+\.[a-z]+\:[0-9]{1,5})"
hostname_pattern = "([a-z]+\.[a-zA-Z0-9]+\.[a-z]+)"
ip_pattern = "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
url_pattern = "(http(s)?://)?([\w-]+\.)+[\w-]+(/])?"



# Command Line colors
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

    http = re.findall("http[s]?", url)
    if (len(http) == 0):
        parser.print_help()
        sys.exit(bcolors.FAIL + "Exception: http needs to be specified." + bcolors.ENDC)
    if (http[0] == "https"):
        parser.print_help()
        sys.exit(bcolors.FAIL + "Exception: HTTPS is not supported." + bcolors.ENDC)
    hostnamePort = re.findall(host_port, url)
    if (len(hostnamePort) == 0):
        urlObject["port"] = 80
    else:
        parsed = hostnamePort[0].split(":")
        urlObject["port"] = parsed[1]
    hostname = re.findall(hostname_pattern, url)
    ip = re.findall(ip_pattern, url)
    if (len(hostname) == 0):
        if (len(ip) == 0):
            parser.print_help()
            sys.exit(bcolors.FAIL + "Exception: No host name or IP was specified." + bcolors.ENDC)
        if (args.hostname == None):
            parser.print_help()
            sys.exit(bcolors.FAIL + "Exception: IP needs hostname." + bcolors.ENDC)
        urlObject["hostname"] = args.hostname
        urlObject["ip"] = ip
    else:
        urlObject["hostname"] = hostname[0]
    url_match = re.findall(url_pattern, url)
    print(url_match[0])
    print(urlObject["hostname"])
    print(urlObject["port"])
    print(urlObject["url"])
    #query = url.replace(url_match[0], '')
    #print(query)
    


    
    print(args.url)
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

if __name__ == "__main__":
    main()
