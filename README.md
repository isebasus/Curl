# 📦  Curl! [![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/isebasus/Curl/blob/master/LICENSE)

## A simple program that replicates Curl
 This project is a simple command line program which fetches HTML pages based on the urls provided by users. The program uses the socket library to process low level http requests to webservers. 

## What you need
You will need [python3](https://www.python.org/downloads/) installed and the `socket` python library installed as dependecies.

## Building this project
Once all dependecies are installed, you will also need the files:
- HTTPoutput.html
- Log.csv

**To run the program:**

```
$ python3 sicarbonMyCurl [-h] url [hostname]
```

**Documentation:**

```
Curl Replication Program

--------------------------------

 A Curl Replication for

 users to request HTML

 documents from hosts.

  

positional arguments:

 url http://hostname[ip]:[port]/[args]

 hostname Optional hostname argument

  

optional arguments:

 -h, --help show this help message and exit

 -l List Header Information.
```

## ❗ Unsupported
- HTTPS 
- Chunk Encoding
- Redirection

## 📋 Log.csv

### Unsuccessful and Successful URLs
```
Unsuccessful, 54, http://www.google.com:443, www.google.com, 192.168.1.11, 142.251.46.228, 50817, 443, [Errno 54] Connection reset by peer

Unsuccessful, 301, http://isebas.us:80, isebas.us, 192.168.1.11, 149.248.9.165, 50931, 80, HTTP/1.1 301 Moved Permanently

Success, 200, http://example.com, example.com, 192.168.1.11, 93.184.216.34, 50963, 80, HTTP/1.1 200 OK

Success, 200, http://pudim.com.br/, pudim.com.br, 192.168.1.11, 54.207.20.104, 51122, 80, HTTP/1.1 200 OK

Unsuccessful, 404, http://www.example.com/anyname.html, www.example.com, 192.168.1.11, 93.184.216.34, 51143, 80, HTTP/1.1 404 Not Found
```
