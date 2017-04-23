import json
import urllib.request,urllib.parse
import Cmath
import sqlite3
import os
import multi,queue
import time
import logging as log
log.basicConfig(format='%(asctime)s %(threadName)s %(levelname)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p',level='INFO')
class WoWauctionAPI:
    def __init__(self,apikey,realm):
        self.apikey = apikey
        self.realm = realm
        self.auctions_api_time=0
        self.auctions_data = {}
        self.auctions_trading_data = {}
        self.auctions_TSM_data = {}
        self.auctions_historical_result = {}
        self.auctions_json_data = ""
    # @profile
    def GetData(self):
        log.info('Getting Data')
        self.auctions_trading_data = {}
        url = 'https://tw.api.battle.net/wow/auction/data/' + urllib.parse.quote(
            self.realm) + '?locale=zh_TW&apikey=' + self.apikey
        log.info('Connect to WoW auction API')
        response = urllib.request.urlopen(url).read().decode('utf-8')
        log.info('Read Json data')
        data = json.loads(response)
        auction_api_url = data["files"][0]["url"]  # array
        self.auctions_api_time = int(data["files"][0]["lastModified"] / 1000)
        auctions_json = urllib.request.urlopen(auction_api_url).read().decode('utf-8')
        self.auctions_data = json.loads(auctions_json)
        for index in self.auctions_data['auctions']:
            if index['buyout'] != 0:
                item = self.auctions_trading_data.setdefault(str(index['item']),
                                                             {'buyout': [], 'minbuyout': 0, 'quantity': 0,
                                                              'marketvalue': 0})
                item['buyout'].append(int(index['buyout'] / index['quantity']))
                item['quantity'] += index['quantity']
        for index in self.auctions_trading_data:
            item = self.auctions_trading_data[index]
            item['minbuyout'] = min(item['buyout'])
            item['marketvalue'] = Cmath.CalculateMarketValue(item['buyout'])
        log.info('GetData Done.')
    # @profile
    def SaveData(self):
        sqllist = {}
        log.info('Saving Data.')
        log.info('Connect to sql database.')
        conn = sqlite3.connect('auctiondata.db')
        cur = conn.cursor()
        for index in self.auctions_trading_data:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS '{0}' (timetick INTEGER PRIMARY KEY,Minbuyout INTEGER,Buyout TEXT,Marketvalue INTEGER,Quantity INTEGER)".format(
                    index))
            cur.execute("CREATE INDEX IF NOT EXISTS'{0}' ON '{1}'(timetick)  ".format('index'+str(index),str(index)))

            if not (self.auctions_api_time,) in cur.execute("SELECT timetick FROM '{0}'".format(str(index))).fetchall():
                sqllist.setdefault(index, []).append((self.auctions_api_time,
                                                  self.auctions_trading_data[index]['minbuyout'],
                                              str(self.auctions_trading_data[index]['buyout']),
                                                  self.auctions_trading_data[index]['marketvalue'],
                                                  self.auctions_trading_data[index]['quantity']))
        for index in sqllist:
            # print(sqllist[index])
            conn.executemany("INSERT INTO '{0}' VALUES (?,?,?,?,?)".format(str(index)), sqllist[index])
        conn.commit()
        conn.close()
        log.info('Saving Data done.')

    # @profile
    def translate(self,day = 7):
        log.info('Translating Data.')
        itemlist = []
        marketvaluedict= {}
        log.info('Connect to sql Database.')
        conn = sqlite3.connect('auctiondata.db')
        cur = conn.cursor()
        tables = cur.execute("SELECT name FROM sqlite_master WHERE type= 'table' AND name != 'IDtoName'").fetchall()
        log.info('Start translating.')
        for i in tables:
            (k,)=i
            itemlist.append(k)
        for item in itemlist:
            marketvalue = cur.execute("SELECT marketvalue FROM '{0}'WHERE (timetick>{1})".format(item,Cmath.Data_Time(self.auctions_api_time,day))).fetchall()
            for (index,) in marketvalue:
                marketvaluedict.setdefault(item,[]).append(index)
        for index in marketvaluedict:
            hisV = int(sum(marketvaluedict[index])/len(marketvaluedict[index]))
            self.auctions_historical_result[index] = hisV
        for item in itemlist:
            #print(item,cur.execute("SELECT Minbuyout,Marketvalue,Quantity FROM '{0}' WHERE timetick = (SELECT MAX(timetick) FROM '{0}')".format(item)).fetchone())
            try:
                (minbuyout, marketvalue, quantity) = cur.execute("SELECT Minbuyout,Marketvalue,Quantity FROM '{0}' WHERE timetick = (SELECT MAX(timetick) FROM '{0}')".format(item)).fetchone()
            except:
                log.info('Drop table {0}'.format(item))
                cur.execute("DROP TABLE '{0}'".format(item))
            if item in self.auctions_historical_result:
                self.auctions_TSM_data[item]={'minbuyout':minbuyout,'marketvalue':marketvalue,'quantity':quantity,'historical':self.auctions_historical_result[item]}
            else:
                self.auctions_TSM_data[item] = {'minbuyout': minbuyout, 'marketvalue': marketvalue,
                                                'quantity': quantity,
                                                'historical': 0}
        log.info('Translating Done.')
    # @profile
    def Save(self,data,u = 'a',dir = "",name ="test"):
            path = dir
            completeName = os.path.join(path,name)
            log.info('Saving to '+completeName)
            #print (completeName)
            try:
                self.file = open(completeName, u, -1,'utf-8')
            except :
                log.info('File not found,new one.')
                self.file = open(completeName, 'w',-1,'utf-8')
            self.file.writelines((str(data) + "\n"))
            self.file.close()
    #@profile
    def SavedatatoTSM(self,dir=""):
        log.info('Saving translated Data to TSM folder')
        TSMDATA = "{"
        TSMdataForm = 'select(2, ...).LoadData("AUCTIONDB_MARKET_DATA","' + self.realm + '",[[return {downloadTime=' + str(
            self.auctions_api_time) + ',fields={"itemString","minBuyout","historical","marketValue","numAuctions"},data='
        for index in self.auctions_TSM_data:
            item = self.auctions_TSM_data[index]
            if index == list(self.auctions_TSM_data.keys())[-1]:
                TSMDATA += "{" + str(index) + "," + str(item['minbuyout']) +","+str(item['historical']) +","+str(item['marketvalue'])+"," + str(item['quantity']) + "}}}]])"
            else:
                TSMDATA += "{" + str(index) + "," + str(item['minbuyout']) +","+str(item['historical']) +","+str(item['marketvalue'])+"," + str(item['quantity']) + "},"
        TSM = TSMdataForm+TSMDATA
        self.Save(TSM,dir=dir,name='AppDATA.lua',u='w')
        log.info('Saving Done.')

    def IDtoChinese(self):
        conn = sqlite3.connect('auctiondata.db')
        cur = conn.cursor()
        conn_item = sqlite3.connect("item.db")
        cur_item = conn_item.cursor()
        tables = cur.execute("SELECT name FROM sqlite_master WHERE type= 'table' AND name != 'IDtoName'").fetchall()
        cur_item.execute("CREATE TABLE IF NOT EXISTS IDtoName ( ID  INTEGER PRIMARY KEY,INAME TEXT)")
        IDtable = cur_item.execute("SELECT ID FROM IDtoName ").fetchall()
        workQueue = queue.Queue(50)
        def run(i):
            name = self.itemAPI(i)
            namelist.append((i, name))
        for (i,)  in tables :
            k = (int(i),)
            if k not in IDtable:
                #print(IDtable)
                (y,) =k
                log.info('finding '+str(y))
                workQueue.put(y)
                if workQueue.full() or (workQueue.empty() is False and (i,) == tables[-1]):
                    namelist = []
                    threads = []
                    for i in range(0,workQueue.qsize()):
                        data = workQueue.get()
                        thread = multi.multithreading(i,run,data)
                        thread.start()
                        threads.append(thread)
                        if workQueue.empty():
                            break
                    #print('test')
                    for t in threads:
                        t.join()
                    cur_item.executemany("INSERT INTO IDtoName VALUES (?,?)", namelist)
                    conn_item.commit()
        conn.close()
        conn_item.close()
        log.info('Scan Done.')


    def itemAPI(self,itemID):
        url = 'https://tw.api.battle.net/wow/item/'+str(itemID)+'?locale=zh_TW&apikey='+self.apikey
        response = urllib.request.urlopen(url).read().decode('utf-8')
        data = json.loads(response)
        print(data['name'])
        return data['name']

    #@profile
    def delete_historical_file(self,period = 60):
        time_day = Cmath.Data_Time((time.time()),period)
        conn = sqlite3.connect('auctiondata.db')
        cur = conn.cursor()
        item_table = cur.execute("SELECT name FROM sqlite_master WHERE type= 'table' AND name != 'IDtoName'").fetchall()
        for (item,) in item_table:
            log.info('now deleting item {0} timetick {1}'.format(item,time_day))
            sqlstring = "DELETE FROM '{0}' WHERE timetick < {1}".format(str(item), time_day)
            #print(sqlstring)
            cur.execute(sqlstring)
        conn.commit()
        conn.close()
        log.info('Deleting Done.')
if __name__ =='__main__':
    test = WoWauctionAPI('akpusnczh3raqmh6ekerq3d4m4gezvxw','米奈希爾')
    # test.GetData()
    # test.SaveData()
    # test.translate()
    # test.SavedatatoTSM()
    # test.IDtoChinese()
    test.delete_historical_file(60)
