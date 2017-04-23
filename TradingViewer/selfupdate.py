import urllib.request
import json
import logging as log
import zipfile
import os
log.basicConfig(format='%(asctime)s %(threadName)s %(levelname)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p',level='INFO')
Github_Release = 'https://api.github.com/repos/yesmider/TradingViewer/releases/latest'
def download(url):
    data = urllib.request.urlopen(url).read()
    with open('update.zip','wb') as new:
        new.write(data)
def unzip():
    with zipfile.ZipFile('update.zip','r') as updatefile:
        for member in updatefile.namelist():
            if 'Runner.exe' in member:
                with updatefile.open(member) as f:
                    with open('Runner_new.exe','wb') as d:
                        d.write(f.read())

def change_name():
    if 'Runner_new.exe' in os.listdir('.'):
        os.rename('Runner.exe','Runner_old')
        os.rename('Runner_new.exe','Runner.exe')

def remove_files():
    for filename in os.listdir():
        if filename == 'Runner_old':
            os.remove('Runner_old')
        elif filename == 'update.zip':
            os.remove('update.zip')





def update(ver):
    request = urllib.request.urlopen(Github_Release).read().decode('utf-8')
    j = json.loads(request)
    if float(j['tag_name']) > ver:
        download(j["zipball_url"])
        unzip()
        change_name()
        return False
    else:
        remove_files()
        log.info('No Update')
        return True



if __name__ == '__main__':
    #update(123)
    #download('https://api.github.com/repos/yesmider/TradingViewer/zipball/1.001')
    #unzip()
    #change_name()
    remove_files()