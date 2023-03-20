import json
import urllib.request
import copy
import time
import os
from selenium import webdriver


class http_req_results():
    def __init__(self, file_address='football_odds.py'):
        self.data_format = {
            'homeTeam_CH': '',  # 主隊中文名
            'homeTeam_EN': '',  # 主隊英文名
            'awayTeam_CH': '',  # 客隊中文名
            'awayTeam_EN': '',  # 客隊英文名
            'froutEndid': '',  # 馬會顯示ID
            'tShortCH': '',  # 聯賽中文名
            'tShortEN': '',  # 聯賽英文名
            'date': '',  # 日期
            # 全埸主客和 {H:主, A:客, D:和}
            'hadodds': {'H': '', 'A': '', 'D': ''},
            'sgaodds': {},  # 同場過關/事件
            # 半埸主客和 {H:主, A:客, D:和}
            'fhaodds': {'H': '', 'A': '', 'D': ''},
            # 讓球主客和 {H:主, A:客, D:和, AG:客讓, HG:主讓}
            'hhaodds': {'H': '', 'A': '', 'D': '', 'AG': '', 'HG': ''},
            # 讓球{H:主, A:客, AG:客讓, HG:主讓}
            'hdcodds': {'H': '', 'A': '', 'AG': '', 'HG': ''},
            'hilodds': {},  # 入球大小 num:{H:大 L:小}
            'fhlodds': {},  # 半場入球大小 num:{H:大 L:小}
            'chlodds': {},  # 角球大小 num:{H:大 L:小}
            'crsodds': {},  # 波膽 {MH:主其他, MA:客其他, MD:和其他} 31 item
            'fcsodds': {},  # 半場波膽 {MH:主其他, MA:客其他, MD:和其他} 31 item
            # 首隊入球 {H:主, N:無入球, A:客}
            'ftsodds': {'H': '', 'N': '', 'A': ''},
            # 總入球
            'ttgodds': {'P0': '', 'P1': '', 'P2': '', 'P3': '', 'P4': '', 'P5': '', 'P6': '', 'M7': ''},
            'ooeodds': {'E': '', 'O': ''},  # 入球單雙 {E:雙, O:單}
            # 半全埸 {H:主, A:客, D:和}
            'hftodds': {'HH': '', 'AH': '', 'DH': '', 'HA': '', 'AA': '', 'DA': '', 'HD': '', 'AD': '', 'DD': ''}
        }
        self.url_findSourse = 'https://bet.hkjc.com/football/getJSON.aspx?jsontype=odds_allodds.aspx&matchid='
        self.url_findID = 'https://bet.hkjc.com/football/getJSON.aspx?jsontype=odds_had.aspx'
        self.header = {'cookie': '',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
        self.url_findResult_copy = []
        self.url_findResult = []
        self.url_finded_tmp = []
        self.file_name = file_address

    def get_cookie(self):
        browser = webdriver.Chrome()
        browser.get('https://bet.hkjc.com/football/')
        time.sleep(10)
        dictcookie = browser.get_cookies()
        cookies_results = ''
        for i in dictcookie:
            cookies_results += (f"{i['name']}={i['value']}; ")
        print(cookies_results)
        return cookies_results

    def input_base_data(self, target, source):  # 基本資料/主客和
        for tmp_A, tmp_B in [
            ('officialID', source['matchIDinofficial']),
            ('MatchID', source['matchID']),
            ('awayTeam_CH', source['awayTeam']['teamNameCH']),
            ('awayTeam_EN', source['awayTeam']['teamNameEN']),
            ('froutEndid', source['frontEndId']),
            ('homeTeam_CH', source['homeTeam']['teamNameCH']),
            ('homeTeam_EN', source['homeTeam']['teamNameEN']),
            ('tShortEN', source['tournament']['tShortEN']),
            ('tShortCH', source['tournament']['tShortCH']),
                ('date', source['matchIDinofficial'][:8])]:
            try:
                target[tmp_A] = tmp_B
            except Exception as Error:
                print('Error | {} {}'.format(source['frontEndId'], Error))

    def input_type1_data(self, target, source):
        # hadodds,hdcodds,hhaodds,crsodds,fcsodds,ooeodds,ftsodds,ttgodds,fhaodds,hftodds
        for name, item in [
            ('hadodds', ['H', 'A', 'D']),
            ('hdcodds', ['H', 'A', 'AG', 'HG']),
            ('hhaodds', ['H', 'A', 'D', 'HG', 'AG']),
            ('crsodds', ['SM1MH', 'SM1MA', 'SM1MD', 'S0000', 'S0001', 'S0002', 'S0003', 'S0004', 'S0005', 'S0100', 'S0101', 'S0102', 'S0103', 'S0104', 'S0105',
                         'S0200', 'S0201', 'S0202', 'S0203', 'S0204', 'S0205', 'S0300', 'S0301', 'S0302', 'S0303', 'S0400', 'S0401', 'S0402', 'S0500', 'S0501', 'S0502']),
            ('fcsodds', ['SM1MH', 'SM1MA', 'SM1MD', 'S0000', 'S0001', 'S0002', 'S0003', 'S0004', 'S0005', 'S0100', 'S0101', 'S0102', 'S0103', 'S0104', 'S0105',
                         'S0200', 'S0201', 'S0202', 'S0203', 'S0204', 'S0205', 'S0300', 'S0301', 'S0302', 'S0303', 'S0400', 'S0401', 'S0402', 'S0500', 'S0501', 'S0502']),
            ('ooeodds', ['O', 'E']),
            ('ftsodds', ['H', 'A']),
            ('ttgodds', ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'M7']),
            ('fhaodds', ['H', 'A', 'D']),
            ('hftodds', ['HH', 'HA', 'HD', 'AH', 'AA', 'AD', 'DH', 'DA', 'DD'])
        ]:
            try:
                target[name] = {}
                for i in item:
                    target[name][i] = source[name][i]
            except Exception as Error:
                print('Error | {} {}'.format(source['frontEndId'], Error))

    def input_type2_data(self, target, source):
        # hilodds,fhlodds,chlodds
        for name in ['hilodds', 'fhlodds', 'chlodds']:
            try:
                target[name] = {}  # reset ojb
                for i in source[name]['LINELIST']:
                    target[name][i['LINE']] = {
                        'H': i['H'], 'L': i['L']}
            except Exception as Error:
                print('Error | {} {}'.format(source['frontEndId'], Error))

    def input_sgaodds_data(self, target, source):  # 同場過關/事件 sgaodds
        try:
            target['sgaodds'] = {}  # reset ojb
            # global source_sgaodds_mark // cannot find this ojb
            tmp_list = source['sgaodds']
            tmp_count = 1
            for j in tmp_list:
                for i in j['SELLIST']:
                    target['sgaodds'].setdefault(
                        tmp_count, {i['CONTENTCH']: i['ODDS']})
                    tmp_count += 1
        except Exception as Error:
            print('Error | {} {}'.format(source['frontEndId'], Error))

    def find_matches(self):  # find match link
        count_times = 0
        self.header['cookie'] = self.get_cookie()
        while True:
            #print(f'Find | {count_times}')
            try:
                request = urllib.request.Request(
                    self.url_findID, headers=self.header)
                with urllib.request.urlopen(request) as response:
                    data_txt = response.read().decode('utf-8')
                data_txt = json.loads(data_txt, strict=False)
                post = data_txt['matches']
                for i in post:
                    self.url_findResult.append(
                        self.url_findSourse+i['matchID'])
                    self.url_findResult_copy = copy.copy(self.url_findResult)
                try:
                    with open('url_findResult', 'w', encoding='utf-8')as txt:
                        txt.write(self.url_findResult[0]+'\n')
                    with open('url_findResult', 'a', encoding='utf-8')as txt:
                        for i in self.url_findResult[1:]:
                            txt.write(i+'\n')
                except Exception as Error:
                    print(Error)
                print(f'matches | {len(self.url_findResult)} ')
            except:
                pass
            else:
                if len(self.url_findResult) != 0:
                    break
                else:
                    count_times += 1
                    if count_times > 20:
                        print('Error | not url')
                        break

    def find_matches_data(self):  # find/input data
        tmp_count = 0
        tmp_total_count = 0
        print(f'Start | {len(self.url_findResult)} matches')
        # while True:
        for url_page_data in self.url_findResult:
            tmp_results_dict = self.data_format
            try:
                index_page = self.url_findResult_copy.index(url_page_data)
                with urllib.request.urlopen(urllib.request.Request(url_page_data, headers=self.header)) as response:
                    data_txt1 = response.read()
                results_finded = json.loads(data_txt1)
                page = results_finded['matches'][index_page]
                time.sleep(1)
                for function in [self.input_base_data, self.input_type1_data, self.input_type2_data, self.input_sgaodds_data]:
                    try:
                        function(target=tmp_results_dict,
                                 source=page)  # input data
                    except Exception as Error:
                        if str(Error.__class__.__name__) != 'KeyError':
                            print(Error)

                with open(self.file_name, 'a', encoding='utf-8') as txt:  # save data
                    txt.write(str(tmp_results_dict)+"\n")
                self.url_finded_tmp.append(url_page_data)
                tmp_results_dict['sgaodds'] = {}
            except Exception as Error:
                # print(Error)
                pass
            
    def start(self):
        self.find_matches()
        self.find_matches_data()
        # self.read_miss_file()

"""
            if len(self.url_finded_tmp) == 0:
                pass
            else:
                try:
                    for i in self.url_finded_tmp:
                        self.url_findResult.remove(i)
                except Exception as Error:
                    print(Error)
            url_finded_tmp = []  # 清空已記場次
            if len(self.url_findResult) == 0:
                try:
                    os.remove('miss_matches_url')
                except Exception as Error:
                    print(Error)
                    print('Finished | Thanks for use')
                break
            if len(self.url_findResult) == tmp_total_count:
                tmp_count += 1
            else:
                tmp_total_count = len(self.url_findResult)
                tmp_count = 0
            if tmp_count >= 0:
                print('completed | {} matches'.format(
                    len(self.url_findResult_copy) - len(self.url_findResult)))
                print(f'End | {len(self.url_findResult)} missed')
                with open('miss_matches_url', 'w', encoding='utf-8') as txt:
                    txt.write(str(self.url_findResult.pop()))
                for i in self.url_findResult:
                    with open('miss_matches_url', 'a', encoding='utf-8') as txt:
                        txt.write('\n'+str(i))
                self.url_findResult = []
                break

    def read_miss_file(self):
        try:
            with open('miss_matches_url', 'r') as txt:
                for i in txt.readlines():
                    self.url_findResult.append(str(i).replace('\n', ''))
                print('=====================================')
                print(f'Load | {len(self.url_findResult)} matches')
                print('=====================================')
        except Exception as Error:
            print(str(Error))
            print(f'completed | {len(self.url_findResult_copy)} matches')"""

    

if __name__ == '__main__':
    http_req_results().start()
