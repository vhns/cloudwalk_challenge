#!/usr/bin/env python3

import csv
import requests
from time import sleep
from json import dumps

file = None
with open('transactions.csv') as f: file = f.read().splitlines()
file.pop(0)
reader = csv.reader(file,delimiter=',')
f = [tuple(i) for i in reader]
f_sorted = sorted(f, key=lambda x: x[0])
f = [{"time_stamp": timestamp, "status": status, "count": int(count)} for timestamp, status, count in f_sorted]
#print(f[0])

url = 'http://api_gateway:8000/status'
headers = {"Content-Type": "application/json"}
i = len(f) - 1
while i >= 0:
#    print(dumps(f[i]))
    response = requests.post(url, data=dumps(f[i]), headers=headers)
    print(response)
#    print(response.text)
#    sleep(5)
    i -= 1
