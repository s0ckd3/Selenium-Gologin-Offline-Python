import os
import pathlib
import random
import json
import time
import sys
import subprocess
import tempfile
from sys import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import requests
import socket


def getRandomPort():
    while True:
        port = random.randint(1000, 35000)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            continue
        else:
            return port
        sock.close()


class Product(object):
    def __init__(self, options):
        self.tmpdir = options.get('tmpdir', tempfile.gettempdir())
        self.address = options.get('address', '127.0.0.1')
        self.extra_params = options.get('extra_params', [])
        self.port = options.get('port', 3500)  # port mặc định
        self.local = options.get('local', False)
        self.spawn_browser = options.get('spawn_browser', True)
        self.credentials_enable_service = options.get('credentials_enable_service')

        home = str(pathlib.Path.home())
        self.executablePath = options.get('executablePath',
                                          'gologin\\browser\\orbita-browser-105\chrome.exe')  # Orbita Path
        if not os.path.exists(self.executablePath) and sys.platform == "darwin":
            self.executablePath = os.path.join(home, '.gologin/browser/Orbita-Browser.app/Contents/MacOS/Orbita')
        if self.extra_params:
            print('extra_params', self.extra_params)
        self.setProfileId(options.get('profile_id'))

    def setProfileId(self, profile_id):
        self.profile_id = profile_id
        if self.profile_id == None:
            return
        self.profile_path = os.path.join(self.tmpdir, self.profile_id)

    def spawnBrowser(self, Proxy):
        self.port = getRandomPort() #Get port Free
        proxy = ''
        proxy_host = ''
        username = ''
        password = ''
        try:
            schema = Proxy.split('://')[0]
            proxies = Proxy.split('://')[1].split(':')
            proxy_host = proxies[0]
            port = proxies[1]
            proxy = f"{proxy_host}:{port}"
        except Exception as re:
            print(re)

        params = [
            self.executablePath,
            f'--remote-debugging-port={str(self.port)}',
            '--user-data-dir=' + self.profile_path,
            '--password-store=basic',
            '--lang=en',

        ]
        # print(proxy)
        if proxy:
            hr_rules = '"MAP * 0.0.0.0 , EXCLUDE %s"' % (proxy_host)
            params.append('--proxy-server=' + proxy)
            params.append('--host-resolver-rules=' + hr_rules)

        for param in self.extra_params:
            params.append(param)
        # print(params)
        subprocess.Popen(params, start_new_session=True, shell=True)
        try_count = 1
        url = str(self.address) + ':' + str(self.port)

        while try_count < 100:
            try:
                data = requests.get('http://' + url + '/json').content
                print(data)
                break
            except:
                try_count += 1
                time.sleep(1)
        return url

    def start(self):
        profile_path = os.path.join(self.tmpdir, self.profile_id)
        # print(profile_path)
        if self.spawn_browser == True:
            return self.spawnBrowser(Proxy)
        return profile_path

    def Change_Proxy(self, Proxy):
        schema = host = port = username = password = ''
        if Proxy:
            username = ''
            password = ''
            try:
                schema = Proxy.split('://')[0]
                host_port = Proxy.split('://')[1].split(':')
                host = host_port[0]
                port = host_port[1]
                if len(host_port) == 4:
                    username = host_port[2]
                    password = host_port[3]

                # print(schema)
            except Exception as re:
                print(re)

            with open(f"{self.profile_path}\\Default\\Preferences", 'r', encoding="utf8") as aa:
                data_profile = json.load(aa)
                data_profile['gologin']['proxy'] = {
                    "id": None,
                    "mode": schema,
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password,
                    "changeIpUrl": str('null'),
                    "autoProxyRegion": "us",
                    "torProxyRegion": "us"
                }
                if data_profile:
                    pfile = open(f"{self.profile_path}\\Default\\Preferences", 'w')
                    json.dump(data_profile, pfile)
                    pfile.close()


    def formatProxyUrl(self, proxyzz):
        return proxyzz.get('mode', 'http') + '://' + proxyzz.get('host', '') + ':' + str(proxyzz.get('port', 80))

    def formatProxyUrlPassword(self, proxyzz):
        if proxyzz.get('username', '') == '':
            return proxyzz.get('mode', 'http') + '://' + proxyzz.get('host', '') + ':' + str(
                proxyzz.get('port', 80))
        else:
            return proxyzz.get('mode', 'http') + '://' + proxyzz.get('username', '') + ':' + proxyzz.get(
                'password') + '@' + proxyzz.get('host', '') + ':' + str(proxyzz.get('port', 80))

    def getTimeZone(self, ):
        with open(f"{self.profile_path}\\Default\\Preferences", 'r') as f:
            data_profile = json.load(f)
            modes = data_profile['gologin']['proxy']['mode']
            hosts = data_profile['gologin']['proxy']['host']
            ports = data_profile['gologin']['proxy']['port']
            try:
                username = data_profile['gologin']['proxy']['username']
                password = data_profile['gologin']['proxy']['password']
            except:
                username = ''
                password = ''

            if (modes == "none"):
                proxyzz = None
            elif (modes == "socks5"):
                proxyzz = {
                    'mode': 'socks5h',
                    'host': hosts,
                    'port': ports,
                    'username': username,
                    'password': password
                }
            elif (username == None):
                proxyzz = {
                    'mode': modes,
                    'host': hosts,
                    'port': ports,
                    'username': username,
                    'password': password
                }
            elif (username == 'Null'):
                proxyzz = {
                    'mode': modes,
                    'host': hosts,
                    'port': ports,
                    'username': username,
                    'password': password
                }
            else:
                proxyzz = data_profile['gologin']['proxy']
        # print(proxyzz)
        headers = {
            'User-Agent': 'gologin-api'
        }
        if proxyzz:
            proxies = dict(
                http=self.formatProxyUrlPassword(proxyzz),
                https=self.formatProxyUrlPassword(proxyzz)
            )
            data = requests.get('https://time.gologin.com', proxies=proxies, headers=headers)
        else:
            data = requests.get('https://time.gologin.com')
        return json.loads(data.content.decode('utf-8'))

    def update(self, profile_id):
        self.tz = self.getTimeZone()
        self.ChangeTimezone()

    def ChangeTimezone(self):
        ips = self.tz.get('ip')
        timezons = self.tz.get('timezone')
        # print(timezons)
        try:
            with open(f"{self.profile_path}\\Default\\Preferences", 'r') as q:
                preferences = json.load(q)
                preferences['gologin']['webRTC']['publicIp'] = ips
                preferences['gologin']['webRtc']['publicIP'] = ips
                preferences['gologin']['webRtc']['public_ip'] = ips
                preferences['gologin']['timezone']['id'] = timezons

                preferences['gologin']['geoLocation']['latitude'] = self.tz.get('ll', [0, 0])[0]
                preferences['gologin']['geoLocation']['longitude'] = self.tz.get('ll', [0, 0])[1]
                preferences['gologin']['geoLocation']['accuracy'] = self.tz.get('accuracy', 0)

                preferences['gologin']['geolocation']['latitude'] = self.tz.get('ll', [0, 0])[0]
                preferences['gologin']['geolocation']['longitude'] = self.tz.get('ll', [0, 0])[1]
                preferences['gologin']['geolocation']['accuracy'] = self.tz.get('accuracy', 0)
                q.close()
                if preferences:
                    pfiles = open(f"{self.profile_path}\\Default\\Preferences", 'w')
                    json.dump(preferences, pfiles)
                    pfiles.close()
        except Exception as e:
            print(e)


# Khởi chạy Profile offline

starts = Product({
    "tmpdir": 'F:\profile_test',  # Đường dẫn folder profile
    "local": False,
    "credentials_enable_service": False,
    "extra_params": ['--disable-site-isolation-trials']
})
Proxy = None
Proxy_data = ['http://192.168.1.111:7101', 'http://192.168.1.111:7102']
# Proxy_data = []
if Proxy_data:
    for Proxy_new in Proxy_data:
        Proxy = Proxy_new

profile_id = '98998097614797189124'
starts.setProfileId(profile_id)
if Proxy:
    starts.Change_Proxy(Proxy) # Đổi proxy cho profile cần mở. Để cảm bảo vân tay chính xác theo proxy
    starts.update(profile_id) # Cập nhật profile

print('Profile start: ', profile_id)
print('Proxy start: ', Proxy)
debugger_address = starts.start() #Kết nối với profile
print(debugger_address)
chrome_driver_path = Service('chromedriver.exe')
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", debugger_address)
driver = webdriver.Chrome(service=chrome_driver_path, options=chrome_options)
driver.get("https://accounts.google.com/ServiceLogin?hl=vi")

time.sleep(2)
loginBox = driver.find_element(By.ID, 'identifierId')
loginBox.send_keys('huongthuy70483')
time.sleep(2)
loginBox.send_keys(Keys.ENTER)

time.sleep(2)
passWordBox = driver.find_element(By.NAME, 'Passwd')
passWordBox.send_keys('passsss')
time.sleep(2)
passWordBox.send_keys(Keys.ENTER)
