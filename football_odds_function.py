import json
import urllib.request
import time
from selenium import webdriver
import mysql.connector
import os
import datetime


class http_req_results():
    # set basic info
    def __init__(self, file_address='football_odds'):
        self.data_format = {
            'officialID': "",
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
        self.url_finded_tmp = []
        self.file_name = file_address
        self.results = []
        self.upto_sql = False

    # set & execute sql
    def set_db(self, host, port, user, passwd, database):
        self.db_connect = mysql.connector.connect(
            host=host, port=port, user=user, passwd=passwd, database=database)
        self.cursor = self.db_connect.cursor()

    # get cookie
    def get_cookie(self):
        browser = webdriver.Chrome()
        browser.get('https://bet.hkjc.com/football/')
        time.sleep(5)
        dictcookie = browser.get_cookies()
        cookies_results = ''
        for i in dictcookie:
            cookies_results += (f"{i['name']}={i['value']}; ")
        print(cookies_results)
        return cookies_results

    def get_link_json(self, link):
        try:
            with urllib.request.urlopen(urllib.request.Request(link, headers=self.header)) as txt:
                data = txt.read().decode('utf-8')
            return json.loads(data, strict=False)
        except Exception as Error:
            print(f"get_json | {Error}")

    # find match link
    def find_matches(self):
        if self.header['cookie'] == '':
            self.header['cookie'] = self.get_cookie()
        url_findResult = []
        try:
            data_json = self.get_link_json(
                self.url_findID)
            post = data_json['matches']
            for i in post:
                url_findResult.append(self.url_findSourse+i['matchID'])
            print(f"finded matches | {len(url_findResult)}")
            # mark and save the link
            with open('url_findResult', 'w', encoding='utf-8')as txt:
                txt.write(url_findResult[0]+'\n')
            with open('url_findResult', 'a', encoding='utf-8')as txt:
                for i in url_findResult[1:]:
                    txt.write(i+'\n')
            return url_findResult
        except Exception as Error:
            print(f"find_matches | {Error}")

    # find data follow the format
    def input_base_data(self, target, source):
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
            ('date', source['matchIDinofficial'][:8]),
            ('yyyy', source['matchIDinofficial'][0:4]),
            ('mm', source['matchIDinofficial'][4:6]),
                ('dd', source['matchIDinofficial'][6:8])]:
            try:
                target[tmp_A] = tmp_B
            except Exception as Error:
                if Error.__class__.__name__ == 'KeyError':
                    pass
                else:
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
            ('ftsodds', ['H', 'A', 'N']),
            ('ttgodds', ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'M7']),
            ('fhaodds', ['H', 'A', 'D']),
            ('hftodds', ['HH', 'HA', 'HD', 'AH', 'AA', 'AD', 'DH', 'DA', 'DD'])
        ]:
            try:
                target[name] = {}
                for i in item:
                    target[name][i] = source[name][i].replace(
                        '100@', '').replace('001@', '')
            except Exception as Error:
                if Error.__class__.__name__ == 'KeyError':
                    pass
                else:
                    print('Error | {} {}'.format(source['frontEndId'], Error))

    def input_type2_data(self, target, source):
        # hilodds,fhlodds,chlodds
        for name in ['hilodds', 'fhlodds', 'chlodds']:
            try:
                target[name] = []  # reset ojb
                for i in source[name]['LINELIST']:
                    line = i['LINE']
                    H = i['H'].replace('100@', '')
                    L = i['L'].replace('100@', '')
                    tmp_tuple = (line, H, L)
                    target[name].append(tmp_tuple)
                    '''target[name][i['LINE']] = {
                        'H': i['H'], 'L': i['L']}'''
            except Exception as Error:
                if Error.__class__.__name__ == 'KeyError':
                    pass
                else:
                    print('Error | {} {}'.format(source['frontEndId'], Error))

    def input_sgaodds_data(self, target, source):  # sgaodds
        try:
            target['sgaodds'] = []  # reset ojb
            # global source_sgaodds_mark // cannot find this ojb
            for j in source['sgaodds']:
                for i in j['SELLIST']:
                    contrntCH = i['CONTENTCH']
                    contentEN = i['CONTENTEN']
                    odd = i['ODDS'].replace('100@', '')
                    tmp_tuple = (contrntCH, contentEN, odd)
                    target['sgaodds'].append(tmp_tuple)

                    pass
                    '''target['sgaodds'].setdefault(
                        tmp_count, {i['CONTENTCH']: i['ODDS']})'''
        except Exception as Error:
            if Error.__class__.__name__ == 'KeyError':
                pass
            else:
                print('Error | {} {}'.format(source['frontEndId'], Error))
    # get results in link

    def get_results(self):
        if self.header['cookie'] == '':
            self.header['cookie'] = self.get_cookie()
        page_list = []
        if os.path.exists('url_findResult'):
            with open('url_findResult', 'r') as txt:
                data = [i.replace('\n', '') for i in txt.readlines()]
                matches_list = data
        else:
            matches_list = self.find_matches()
        print(f'loads | {len(matches_list)} matches')
        for link in matches_list:
            page_index = matches_list.index(link)
            try:
                with urllib.request.urlopen(urllib.request.Request(link, headers=self.header)) as response:
                    data = response.read()
                results = json.loads(data)
                page = results['matches'][page_index]
                page_list.append(page)
            except:
                pass
        print(f"get | {len(page_list)} matches")
        return page_list

    # Data_Filter
    def data_Filter(self, gen_results=False, results_file_name='results'):

        total_data_list = []
        results = self.get_results()
        count = 0
        for i in results:
            total_data_list.append({})
            try:
                for founction in [self.input_base_data, self.input_type1_data, self.input_type2_data, self.input_sgaodds_data]:
                    founction(target=total_data_list[count], source=i)
            except Exception as Error:
                print(f'data filter | {Error}')
            count += 1
        print(f'filter | {len(total_data_list)}')
        if gen_results:
            for data in total_data_list:
                with open(results_file_name, 'a', encoding='utf-8') as txt:
                    txt.write(str(data) + '\n')
        now = datetime.datetime.now()
        new_csv_path = os.path.splitext('url_findResult')[
            0] + '_' + now.strftime('%Y-%m-%d_%H-%M-%S') + os.path.splitext('url_findResult')[1]
        os.rename('url_findResult', new_csv_path)
        return total_data_list

    # up to sql
    def up_to_sql(self):
        data_list = self.data_Filter()
        for match in data_list:
            print(match['officialID'])
            # update basic_info
            self.cursor.execute(
                """select * from `basic_info` where `officialID`=%s and date != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                self.cursor.execute('''update `basic_info` set homeTeam_CH =%s,homeTeam_EN =%s,awayTeam_CH =%s,awayTeam_EN =%s,froutEndid =%s,tShortCH =%s,tShortEN =%s,date =%s,yyyy=%s,mm=%s,dd=%s where officialID =%s''',
                                    (match['homeTeam_CH'], match['homeTeam_EN'], match['awayTeam_CH'], match['awayTeam_EN'],
                                     match['froutEndid'], match['tShortCH'], match['tShortEN'], match['date'], int(match['yyyy']), int(match['mm']), int(match['dd']), match['officialID'])
                                    )
            else:
                self.cursor.execute('''insert into `basic_info` (officialID,homeTeam_CH,homeTeam_EN,awayTeam_CH,awayTeam_EN,froutEndid,tShortCH,tShortEN,yyyy,mm,dd,date) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (
                    match['officialID'], match['homeTeam_CH'], match['homeTeam_EN'], match['awayTeam_CH'], match['awayTeam_EN'], match['froutEndid'], match['tShortCH'], match['tShortEN'], int(match['yyyy']), int(match['mm']), int(match['dd']), match['date']))
            # update crsodds
            self.cursor.execute(
                """select * from `crsodds` where `officialID`=%s and SM1MH != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['crsodds']:
                    self.cursor.execute(
                        '''update `crsodds` set SM1MH=%s,SM1MA=%s,SM1MD=%s,S0000=%s,S0001=%s,S0002=%s,S0003=%s,S0004=%s,S0005=%s,S0100=%s,S0101=%s,S0102=%s,S0103=%s,S0104=%s,S0105=%s,S0200=%s,S0201=%s,S0202=%s,S0203=%s,S0204=%s,S0205=%s,S0300=%s,S0301=%s,S0302=%s,S0303=%s,S0400=%s,S0401=%s,S0402=%s,S0500=%s,S0501=%s,S0502=%s where officialID=%s''',
                        (match['crsodds']['SM1MH'], match['crsodds']['SM1MA'], match['crsodds']['SM1MD'], match['crsodds']['S0000'], match['crsodds']['S0001'], match['crsodds']['S0002'], match['crsodds']['S0003'], match['crsodds']['S0004'], match['crsodds']['S0005'], match['crsodds']['S0100'], match['crsodds']['S0101'], match['crsodds']['S0102'], match['crsodds']['S0103'], match['crsodds']['S0104'], match['crsodds']['S0105'], match['crsodds']['S0200'],
                         match['crsodds']['S0201'], match['crsodds']['S0202'], match['crsodds']['S0203'], match['crsodds']['S0204'], match['crsodds']['S0205'], match['crsodds']['S0300'], match['crsodds']['S0301'], match['crsodds']['S0302'], match['crsodds']['S0303'], match['crsodds']['S0400'], match['crsodds']['S0401'], match['crsodds']['S0402'], match['crsodds']['S0500'], match['crsodds']['S0501'], match['crsodds']['S0502'], match['officialID'])
                    )
            else:
                if match['crsodds']:
                    self.cursor.execute(
                        '''insert into `crsodds` (officialID,SM1MH,SM1MA,SM1MD,S0000,S0001,S0002,S0003,S0004,S0005,S0100,S0101,S0102,S0103,S0104,S0105,S0200,S0201,S0202,S0203,S0204,S0205,S0300,S0301,S0302,S0303,S0400,S0401,S0402,S0500,S0501,S0502) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                        (match['officialID'], match['crsodds']['SM1MH'], match['crsodds']['SM1MA'], match['crsodds']['SM1MD'], match['crsodds']['S0000'], match['crsodds']['S0001'], match['crsodds']['S0002'], match['crsodds']['S0003'], match['crsodds']['S0004'], match['crsodds']['S0005'], match['crsodds']['S0100'], match['crsodds']['S0101'], match['crsodds']['S0102'], match['crsodds']['S0103'], match['crsodds']['S0104'], match['crsodds']['S0105'],
                            match['crsodds']['S0200'], match['crsodds']['S0201'], match['crsodds']['S0202'], match['crsodds']['S0203'], match['crsodds']['S0204'], match['crsodds']['S0205'], match['crsodds']['S0300'], match['crsodds']['S0301'], match['crsodds']['S0302'], match['crsodds']['S0303'], match['crsodds']['S0400'], match['crsodds']['S0401'], match['crsodds']['S0402'], match['crsodds']['S0500'], match['crsodds']['S0501'], match['crsodds']['S0502'])
                    )
            # update fcsodds
            self.cursor.execute(
                """select * from `fcsodds` where `officialID`=%s and SM1MH != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['fcsodds']:
                    self.cursor.execute(
                        '''update `crsodds` set SM1MH=%s,SM1MA=%s,SM1MD=%s,S0000=%s,S0001=%s,S0002=%s,S0003=%s,S0004=%s,S0005=%s,S0100=%s,S0101=%s,S0102=%s,S0103=%s,S0104=%s,S0105=%s,S0200=%s,S0201=%s,S0202=%s,S0203=%s,S0204=%s,S0205=%s,S0300=%s,S0301=%s,S0302=%s,S0303=%s,S0400=%s,S0401=%s,S0402=%s,S0500=%s,S0501=%s,S0502=%s where officialID=%s''',
                        (match['fcsodds']['SM1MH'], match['fcsodds']['SM1MA'], match['fcsodds']['SM1MD'], match['fcsodds']['S0000'], match['fcsodds']['S0001'], match['fcsodds']['S0002'], match['fcsodds']['S0003'], match['fcsodds']['S0004'], match['fcsodds']['S0005'], match['fcsodds']['S0100'], match['fcsodds']['S0101'], match['fcsodds']['S0102'], match['fcsodds']['S0103'], match['fcsodds']['S0104'], match['fcsodds']['S0105'],
                         match['fcsodds']['S0200'], match['fcsodds']['S0201'], match['fcsodds']['S0202'], match['fcsodds']['S0203'], match['fcsodds']['S0204'], match['fcsodds']['S0205'], match['fcsodds']['S0300'], match['fcsodds']['S0301'], match['fcsodds']['S0302'], match['fcsodds']['S0303'], match['fcsodds']['S0400'], match['fcsodds']['S0401'], match['fcsodds']['S0402'], match['fcsodds']['S0500'], match['fcsodds']['S0501'], match['fcsodds']['S0502'], match['officialID']))
            else:
                if match['fcsodds']:
                    self.cursor.execute(
                        '''insert into `fcsodds` (officialID,SM1MH,SM1MA,SM1MD,S0000,S0001,S0002,S0003,S0004,S0005,S0100,S0101,S0102,S0103,S0104,S0105,S0200,S0201,S0202,S0203,S0204,S0205,S0300,S0301,S0302,S0303,S0400,S0401,S0402,S0500,S0501,S0502) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                        (match['officialID'], match['fcsodds']['SM1MH'], match['fcsodds']['SM1MA'], match['fcsodds']['SM1MD'], match['fcsodds']['S0000'], match['fcsodds']['S0001'], match['fcsodds']['S0002'], match['fcsodds']['S0003'], match['fcsodds']['S0004'], match['fcsodds']['S0005'], match['fcsodds']['S0100'], match['fcsodds']['S0101'], match['fcsodds']['S0102'], match['fcsodds']['S0103'], match['fcsodds']['S0104'], match['fcsodds']['S0105'],
                         match['fcsodds']['S0200'], match['fcsodds']['S0201'], match['fcsodds']['S0202'], match['fcsodds']['S0203'], match['fcsodds']['S0204'], match['fcsodds']['S0205'], match['fcsodds']['S0300'], match['fcsodds']['S0301'], match['fcsodds']['S0302'], match['fcsodds']['S0303'], match['fcsodds']['S0400'], match['fcsodds']['S0401'], match['fcsodds']['S0402'], match['fcsodds']['S0500'], match['fcsodds']['S0501'], match['fcsodds']['S0502'])
                    )
            # update fhaodds
            self.cursor.execute(
                """select * from `fhaodds` where `officialID`=%s and H != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['fhaodds']:
                    self.cursor.execute(
                        '''update `fhaodds` set H=%s,A=%s,D=%s where officialID=%s''',
                        (match['fhaodds']["H"], match['fhaodds']['A'],
                         match['fhaodds']['D'], match['officialID'])
                    )
            else:
                if match['fhaodds']:
                    self.cursor.execute(
                        '''insert into `fhaodds` (officialID,H,A,D) values (%s,%s,%s,%s)''',
                        (match['officialID'], match['fhaodds']["H"],
                         match['fhaodds']['A'], match['fhaodds']['D'])
                    )
            # update ftsodds
            self.cursor.execute(
                """select * from `ftsodds` where `officialID`=%s and H != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['ftsodds']:
                    self.cursor.execute(
                        '''update `ftsodds` set H=%s,N=%s,A=%s where officialID=%s''',
                        (match['ftsodds']['H'], match['ftsodds']['N'],
                         match['ftsodds']['A'], match['officialID'])
                    )
            else:
                if match['ftsodds']:
                    self.cursor.execute(
                        '''insert into `ftsodds` (officialID,H,N,A) values(%s,%s,%s,%s)''',
                        (match['officialID'], match['ftsodds']['H'],
                         match['ftsodds']['N'], match['ftsodds']['A'])
                    )
            # update hadodds
            self.cursor.execute(
                """select * from `hadodds` where `officialID`=%s and H != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['hadodds']:
                    self.cursor.execute(
                        '''update `hadodds` set H=%s,A=%s,D=%s where officialID=%s''',
                        (match['hadodds']["H"], match['hadodds']['A'],
                         match['hadodds']['D'], match['officialID'])
                    )
            else:
                if match['hadodds']:
                    self.cursor.execute(
                        '''insert into `hadodds` (officialID,H,A,D) values(%s,%s,%s,%s)''',
                        (match['officialID'], match['hadodds']["H"],
                         match['hadodds']['A'], match['hadodds']['D'])
                    )
            # update hdcodds
            self.cursor.execute(
                """select * from `hdcodds` where `officialID`=%s and H != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['hdcodds']:
                    self.cursor.execute(
                        '''update `hdcodds` set H=%s,A=%s,AG=%s,HG=%s where officialID=%s''',
                        (match['hdcodds']['H'], match['hdcodds']['A'], match['hdcodds']
                         ['AG'], match['hdcodds']['HG'], match['officialID'])
                    )
            else:
                if match['hdcodds']:
                    self.cursor.execute(
                        '''insert into `hdcodds` (officialID,H,A,AG,HG) values(%s,%s,%s,%s,%s)''',
                        (match['officialID'], match['hdcodds']['H'], match['hdcodds']
                         ['A'], match['hdcodds']['AG'], match['hdcodds']['HG'])
                    )
            # update hftodds
            self.cursor.execute(
                """select * from `hftodds` where `officialID`=%s and HH != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['hftodds']:
                    self.cursor.execute(
                        '''update `hftodds` set HH=%s,AH=%s,DH=%s,HA=%s,AA=%s,DA=%s,HD=%s,AD=%s,DD=%s where officialID=%s''',
                        (match['hftodds']['HH'], match['hftodds']['AH'], match['hftodds']['DH'], match['hftodds']['HA'], match['hftodds']['AA'],
                         match['hftodds']['DA'], match['hftodds']['HD'], match['hftodds']['AD'], match['hftodds']['DD'], match['officialID'])
                    )
            else:
                if match['hftodds']:
                    self.cursor.execute(
                        '''insert into `hftodds` (officialID,HH,AH,DH,HA,AA,DA,HD,AD,DD) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                        (match['officialID'], match['hftodds']['HH'], match['hftodds']['AH'], match['hftodds']['DH'], match['hftodds']['HA'],
                         match['hftodds']['AA'], match['hftodds']['DA'], match['hftodds']['HD'], match['hftodds']['AD'], match['hftodds']['DD'])
                    )
            # update hhaodds
            self.cursor.execute(
                """select * from `hhaodds` where `officialID`=%s and H != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['hhaodds']:
                    self.cursor.execute(
                        '''update `hhaodds` set H=%s,A=%s,D=%s,AG=%s,HG=%s where officialID=%s''',
                        (match['hhaodds']['H'], match['hhaodds']['A'], match['hhaodds']['D'],
                         match['hhaodds']['AG'], match['hhaodds']['HG'], match['officialID'])
                    )
            else:
                if match['hhaodds']:
                    self.cursor.execute(
                        '''insert into `hhaodds` (officialID,H,A,D,AG,HG) values(%s,%s,%s,%s,%s,%s)''',
                        (match['officialID'], match['hhaodds']['H'], match['hhaodds']['A'],
                         match['hhaodds']['D'], match['hhaodds']['AG'], match['hhaodds']['HG'])
                    )
            # update ooeodds
            self.cursor.execute(
                """select * from `ooeodds` where `officialID`=%s and O != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['ooeodds']:
                    self.cursor.execute(
                        '''update `ooeodds` set E=%s, O=%s where officialID=%s''',
                        (match['ooeodds']['E'], match['ooeodds']
                         ['O'], match['officialID'])
                    )
            else:
                if match['ooeodds']:
                    self.cursor.execute(
                        '''insert into `ooeodds` (officialID,E,O) values(%s,%s,%s)''',
                        (match['officialID'], match['ooeodds']
                         ['E'], match['ooeodds']['O'])
                    )
            # update ttgodds
            self.cursor.execute(
                """select * from `ttgodds` where `officialID`=%s and P0 != %s;""", (match['officialID'], 'null'))
            countrow = self.cursor.fetchall()
            if len(countrow):
                if match['ttgodds']:
                    self.cursor.execute(
                        '''update `ttgodds` set P0=%s,P1=%s,P2=%s,P3=%s,P4=%s,P5=%s,P6=%s,M7=%s where officialID=%s''',
                        (match['ttgodds']['P0'], match['ttgodds']['P1'], match['ttgodds']['P2'], match['ttgodds']['P3'], match['ttgodds']
                         ['P4'], match['ttgodds']['P5'], match['ttgodds']['P6'], match['ttgodds']['M7'], match['officialID'])
                    )
            else:
                if match['ttgodds']:
                    self.cursor.execute(
                        '''insert into `ttgodds` (officialID,P0,P1,P2,P3,P4,P5,P6,M7) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                        (match['officialID'], match['ttgodds']['P0'], match['ttgodds']['P1'], match['ttgodds']['P2'], match['ttgodds']
                         ['P3'], match['ttgodds']['P4'], match['ttgodds']['P5'], match['ttgodds']['P6'], match['ttgodds']['M7'])
                    )
            # update chlodds
            if match['chlodds']:
                for num in range(len(match['chlodds'])):
                    name, H, L = match['chlodds'][num]
                    new_item = name+'|'+H+'|'+L
                    self.cursor.execute(
                        """select * from `chlodds` where `officialID`=%s and `officialID` != %s;""",
                        (match['officialID'], 'null'))
                    countrow = self.cursor.fetchall()
                    if not (len(countrow)):
                        self.cursor.execute(
                            '''insert into `chlodds` (officialID) values (%s)''',
                            (match['officialID'],)
                        )
                        self.db_connect.commit()
                    self.cursor.execute(
                        '''update `chlodds` set item_%s=%s where officialID=%s''',
                        (num+1, new_item, match['officialID'])
                    )

            # update fhlodds
            if match['fhlodds']:
                for num in range(len(match['fhlodds'])):
                    name, H, L = match['fhlodds'][num]
                    new_item = name+'|'+H+'|'+L
                    self.cursor.execute(
                        """select * from `fhlodds` where `officialID`=%s and `officialID` != %s;""",
                        (match['officialID'], 'null'))
                    countrow = self.cursor.fetchall()
                    if not (len(countrow)):
                        self.cursor.execute(
                            '''insert into `fhlodds` (officialID) values (%s)''',
                            (match['officialID'],)
                        )
                        self.db_connect.commit()
                    self.cursor.execute(
                        '''update `fhlodds` set item_%s=%s where officialID=%s''',
                        (num+1, new_item, match['officialID'])
                    )

            # update hilodds
            if match['hilodds']:
                for num in range(len(match['hilodds'])):
                    name, H, L = match['hilodds'][num]
                    new_item = name+'|'+H+'|'+L
                    self.cursor.execute(
                        """select * from `hilodds` where `officialID`=%s and `officialID` != %s;""",
                        (match['officialID'], 'null'))
                    countrow = self.cursor.fetchall()
                    if not (len(countrow)):
                        self.cursor.execute(
                            '''insert into `hilodds` (officialID) values (%s)''',
                            (match['officialID'],)
                        )
                        self.db_connect.commit()
                    self.cursor.execute(
                        '''update `hilodds` set item_%s=%s where officialID=%s''',
                        (num+1, new_item, match['officialID'])
                    )

            # update sgaodds
            if match['sgaodds']:
                for num in range(len(match['sgaodds'])):
                    name_CH, name_EN, L = match['sgaodds'][num]
                    new_item = name_CH+'|'+name_EN+'|'+L
                    self.cursor.execute(
                        """select * from `sgaodds` where `officialID`=%s and `officialID` != %s;""",
                        (match['officialID'], 'null'))
                    countrow = self.cursor.fetchall()
                    if not (len(countrow)):
                        self.cursor.execute(
                            '''insert into `sgaodds` (officialID) values (%s)''',
                            (match['officialID'],)
                        )
                        self.db_connect.commit()
                    self.cursor.execute(
                        '''update `sgaodds` set item_%s=%s where officialID=%s''',
                        (num+1, new_item, match['officialID'])
                    )

        self.db_connect.commit()


if __name__ == "__main__":
    c = http_req_results()
    c.set_db(host={},
             port={},
             user={},
             passwd={},
             database={})
    c.up_to_sql()
