import sqlite3
import json



with open('auctionsdata') as data:
    sqllist = {}
    dbname = 'auctiondata.db'

    cor = sqlite3.connect(dbname)
    conn = cor.cursor()
    for line in data:
        jsondata = json.loads(line)
        time = jsondata['time']
        linedata = jsondata['data']
        print('now doing ', time)
        for index in linedata:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS '{0}' (timetick INTEGER PRIMARY KEY,Minbuyout INTEGER,Buyout TEXT,Marketvalue INTEGER,Quantity INTEGER)".format(
                    index))
            conn.execute("CREATE INDEX IF NOT EXISTS'{0}' ON '{1}'(timetick)  ".format('index'+str(index),str(index)))

            if not (time,) in conn.execute("SELECT timetick FROM '{0}'".format(str(index))).fetchall():
                sqllist.setdefault(index, []).append((time,
                                                  linedata[index]['minbuyout'],
                                              str(linedata[index]['buyout']),
                                                  linedata[index]['marketvalue'],
                                                  linedata[index]['quantity']))
    for index in sqllist:
        #print(sqllist[index])
        conn.executemany("INSERT INTO '{0}' VALUES (?,?,?,?,?)".format(str(index)), sqllist[index])
    cor.commit()
    cor.close()


