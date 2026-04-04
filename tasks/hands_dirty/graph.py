#!/usr/bin/env python3

import sqlite3
import sys
import matplotlib.pyplot as plt

def fetch_tables(db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    result = cur.fetchall()
    tables = {} 
    for table in result:
        tables[table[0]]={}
    con.close()
    return tables

def graph(tables, db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    for table in tables.keys():
        cur.execute(f"SELECT * FROM {table} ORDER BY time")
        result = cur.fetchall()
        tables[table]['data']=result
        
    fig, ax = plt.subplots(2,figsize=(10,10))
    i = 0

    for key in tables.keys():
        foo = tables[key]['data'][0:]
        data = [x[1:3] for x in foo]
        time, amount = zip(*data)
        print(time, amount)
        ax[i].plot(time, amount, label='Today\'s transactions')
        ax[i].set(xlabel='Hour', ylabel='Amount', title=f'{key}')
        ax[i].grid()
        data = [[x[1], x[3]] for x in foo]
        time, amount = zip(*data)
        ax[i].plot(time, amount, label='Yesterday\'s transactions')
        data = [[x[1], x[4]] for x in foo]
        time, amount = zip(*data)
        ax[i].plot(time, amount, label='Same day last week\'s transactions')
        data = [[x[1], x[5]] for x in foo]
        time, amount = zip(*data)
        ax[i].plot(time, amount, label='Avg last week\'s transactions', marker='o', linestyle='')
        data = [[x[1], x[6]] for x in foo]
        time, amount = zip(*data)
        ax[i].plot(time, amount, label='Avg last month\'s transactions', marker='o', linestyle='')
        i += 1
    
    plt.legend(loc='lower right')
    fig.savefig('test.svg')
    plt.show()



if __name__ == '__main__':
    db = sys.argv[1]
    tables = fetch_tables(db)
    graph(tables, db)
