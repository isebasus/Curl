#!/bin/bash

echo "Testing Given URLs"
python3 curl.py http://www.example.com/anyname.html
python3 curl.py https://www.google.com
python3 curl.py http://www.google.com/somedoc1.html:80
python3 curl.py http://www.google.com:443
python3 curl.py http://wwwexample.com/index.html
python3 curl.py http://www.google.com/index.html
python3 curl.py http://neverssl.com/
python3 curl.py http://pudim.com.br/
python3 curl.py http://www.softwareqatest.com/
python3 curl.py http://www.testingmcafeesites.com/
python3 curl.py https://datatracker.ietf.org/doc/html/rfc2616
python3 curl.py http://www.soe.ucsc.edu:443

cat out/Log.csv
