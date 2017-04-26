from Translator import WoWauctionAPI
import time
import configparser
import multi

from selfupdate import *
import sys
import os
# todo  check tsm ver
# autoupdate
autoupdate = 1
version = 1.0029
# THIS DEFAULT CONFIG
default_config = """[Setting]
WoWdir =
Key = akpusnczh3raqmh6ekerq3d4m4gezvxw
realm =
history_period = 60
request_timer = 300
"""
# END
config = configparser.ConfigParser()
read = config.read('config.ini', 'utf_8_sig')
print('Now version is '+str(version))
if autoupdate:
        if not update(version):
                print('Update Done,please restart.')
                os.system('pause')
                sys.exit(0)
if read == ['config.ini']:
        WoWdir = config.get('Setting', 'WOWdir')
        Key = config.get('Setting', 'Key')
        realm = config.get('Setting', 'realm')
        period = config.get('Setting', 'history_period')
        timer = config.get('Setting' , 'request_timer')
        API = WoWauctionAPI(Key, realm)
        if WoWdir and Key and realm and period:
                # GET method
                def GET():
                        while 1:
                                try:
                                        API.get_data()
                                        API.save_data()
                                        API.translate()
                                        API.save_data_to_tsm(WoWdir + '\\interface\\addons\TradeSkillMaster_AppHelper')
                                        #print(time.asctime(time.localtime(time.time())))
                                        time.sleep(int(timer))
                                except Exception as e:
                                        print(e)



                # traslate ID to Chinese
                def IDtoChinese():
                        while 1:
                                try:
                                        API.id_to_chinese()
                                        time.sleep(int(timer))
                                except Exception as e:
                                        print(e)


                def delete_history():
                        API.delete_historical_file(int(period))
                        # print('delete history data done by period = ' + str(period))

                delete_history()
                Get_thread = multi.multithreading(1, GET)
                ID_thread = multi.multithreading(2, IDtoChinese)
                # DELETE_thread = multi.multithreading(3, delete_history)
                Get_thread.start()
                ID_thread.start()
                # DELETE_thread.start()


        else:
                print('please config your realm and WoW install Dir in config.ini')
                os.system('pause')
elif not read:
        print('OH,there are no config.ini,create one for you')
        with open('config.ini', encoding='utf_8_sig', mode='w') as configfile:
                configfile.write(default_config)
                print('please config your realm and WoW install Dir in config.ini')
                os.system('pause')
