#!/usr/bin/env python3

import sys
import sqlite3
import csv

def import_data(csv_data, cur, name):
    file = None
    with open(csv_data, mode='r', newline='') as f: file = f.read().splitlines()
    file.pop(0)
    reader = csv.reader(file, delimiter=',')
    f = [tuple(i) for i in reader]
    cur.execute(f"CREATE TABLE IF NOT EXISTS {name} (\
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
                    time INT NOT NULL,\
                    today INT NOT NULL,\
	                yesterday INT NOT NULL,\
	                last_week INT NOT NULL,\
	                avg_last_week FLOAT NOT NULL,\
	                avg_last_month FLOAT NOT NULL)")
    cur.executemany(f"INSERT INTO {name} \
                        VALUES(NULL, ?, ?, ?, ?, ?, ?)",
                    f)

if __name__ == '__main__':
    if len(sys.argv) > 3:
        print('Too many arguments.')
        os.exit()
    if len(sys.argv) < 3:
        print('Too few arguments.')
        os.exit()
    con = sqlite3.connect(sys.argv[1])
    cur = con.cursor()
    name = ''.join(sys.argv[2].split('.')[0:-1])
    for i in sys.argv[2:]:
        import_data(i, cur, name)
    con.commit()
    con.close()
