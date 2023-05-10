import json
import urllib.request
import time
import datetime
from selenium import webdriver
import mysql.connector


class http_req_results():
    def __init__(self, date='2016/01/01', Num_day=1):
        self.date_format = '%Y/%m/%d'
        self.date = datetime.datetime.strptime(date, self.date_format)
        self.nextdate = self.date+datetime.timedelta(days=1)
        self.start_date = str(
            self.date+datetime.timedelta(days=0)).replace('-', '')[:8]
        self.end_date = str(
            self.date+datetime.timedelta(days=Num_day)).replace('-', '')[:8]
        self.mark_date = f'{self.end_date[:4]}/{self.end_date[4:6]}/{self.end_date[6:8]}'
        self.today_date = str(datetime.datetime.now()).replace('-', '')[:8]
        self.data_format = {
            'officialID': '',
            'date': '',
            'homeTeam_CH': '',  # 主隊中文名
            'homeTeam_EN': '',  # 主隊英文名
            'awayTeam_CH': '',  # 客隊中文名
            'awayTeam_EN': '',  # 客隊英文名
            'tShortCH': '',  # 聯賽中文名
            'tShortEN': '',  # 聯賽英文名
            'half_score': '',  # 上半比分
            'full_score': '',  # 全埸比分
            'fts': '',  # 首隊入球
            'chl': ''  # 角球
        }
        self.url_findSourse = f'https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate={self.start_date}&enddate={self.end_date}&teamid=default'
        self.header = {'cookie': '',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
        #print(self.start_date, self.end_date, self.mark_date, self.today_date)

    def get_cookie(self):
        cookies_results = ''
        try:
            browser = webdriver.Chrome()
            browser.get('https://bet.hkjc.com/football/')
            time.sleep(5)
            dictcookie = browser.get_cookies()
            for i in dictcookie:
                cookies_results += f"{i['name']}={i['value']}; "
            print(cookies_results)
        except Exception as Error:
            print(Error)
        return cookies_results

    def get_resutls(self):
        page_no = 1
        results_list = []
        while True:
            print(f'page_no | {page_no}')
            url = (self.url_findSourse+'&pageno='+str(page_no))
            with urllib.request.urlopen(urllib.request.Request(url, headers=self.header)) as response:
                data_txt = response.read().decode('utf-8')
            try:
                results = json.loads(data_txt)
            except Exception as Error:
                print(Error)
                self.header['cookie'] = self.get_cookie()
                continue
            if len(results):
                results_ = results[0]['matches']
            else:
                return 0
            for i in results_:
                results_list.append(i)
            if (int(results[0]['matchescount'])/page_no) == 20:
                print(f'get | {len(results_list)}')
                return results_list
            elif len(results_) != 20:
                print(f'get | {len(results_list)}')
                return results_list
            page_no += 1
    # input data

    def input_data(self, target, source):
        if 'matchIDinofficial' in source:
            target['officialID'] = source['matchIDinofficial']
            target['yyyy'] = int(source['matchIDinofficial'][:4])
            target['mm'] = int(source['matchIDinofficial'][4:6])
            target['dd'] = int(source['matchIDinofficial'][6:8])
        if 'homeTeam' in source:
            target['homeTeam_CH'] = source['homeTeam']['teamNameCH']
            target['homeTeam_EN'] = source['homeTeam']['teamNameEN']
        if 'awayTeam' in source:
            target['awayTeam_CH'] = source['awayTeam']['teamNameCH']
            target['awayTeam_EN'] = source['awayTeam']['teamNameEN']
        if 'tournament' in source:
            target['tShortCH'] = source['tournament']['tShortCH']
            target['tShortEN'] = source['tournament']['tShortEN']
        if 'cornerresult' in source:
            target['chl'] = source['cornerresult']
        else:
            target['chl'] = ''
        if 'accumulatedscore' in source:
            if len(source['accumulatedscore']) == 2:
                target['half_score'] = str(
                    source['accumulatedscore'][0][

                        'home'])+'|'+str(source['accumulatedscore'][0]['away'])
                target['full_score'] = str(
                    source['accumulatedscore'][1]['home'])+'|'+str(source['accumulatedscore'][0]['away'])
            else:
                target['half_score'] = ''
                target['full_score'] = ''
        else:
            target['half_score'] = ''
            target['full_score'] = ''
        if 'results' in source:
            if 'FTS' in source['results']:
                target['fts'] = source['results']['FTS']
            else:
                target['fts'] = ''
        else:
            target['fts'] = ''

    def data_Filter(self, gen_file=False, file_name='results'):
        data_list = []
        count = 0
        results_list = self.get_resutls()
        if results_list:
            for i in results_list:
                data_list.append({})
                self.input_data(target=data_list[count], source=i)
                count += 1
            return data_list
        else:
            return 0

    # set & execute sql
    def set_db(self, host, port, user, passwd, database):
        self.db_connect = mysql.connector.connect(
            host=host, port=port, user=user, passwd=passwd, database=database)
        self.cursor = self.db_connect.cursor()

    # up to sql
    def up_to_sql(self):
        data_list = self.data_Filter()
        if not(data_list):
            return
        for match in data_list:
            print(match['officialID'])
            # update data
            self.cursor.execute(
                """select * from `football_results` where `officialID`=%s;""", (match['officialID'],))
            countrow = self.cursor.fetchall()
            if len(countrow):
                self.cursor.execute(
                    '''update `football_results` set yyyy=%s,mm=%s,dd=%s,homeTeam_CH=%s,homeTeam_EN=%s,awayTeam_CH=%s,awayTeam_EN=%s,tShortCH=%s,tShortEN=%s,half_score=%s,full_score=%s,fts=%s,chl=%s where officialID=%s''',
                    (match['yyyy'], match['mm'], match['dd'], match['homeTeam_CH'], match['homeTeam_EN'], match['awayTeam_CH'], match['awayTeam_EN'], match['tShortCH'],
                     match['tShortEN'], match['half_score'], match['full_score'], match['fts'], match['chl'], match['officialID'])
                )
            else:
                self.cursor.execute(
                    '''insert into `football_results` (officialID,yyyy,mm,dd,homeTeam_CH,homeTeam_EN,awayTeam_CH,awayTeam_EN,tShortCH,tShortEN,half_score,full_score,fts,chl) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                    (match['officialID'], match['yyyy'], match['mm'], match['dd'], match['homeTeam_CH'], match['homeTeam_EN'], match['awayTeam_CH'], match['awayTeam_EN'],
                     match['tShortCH'], match['tShortEN'], match['half_score'], match['full_score'], match['fts'], match['chl'])
                )
            self.db_connect.commit()
        data_list.clear()

    def auto_run(self):
        print(self.today_date)
        while True:
            print(self.start_date)
            self.up_to_sql()
            self.date = self.date+datetime.timedelta(days=1)
            self.start_date = str(
                self.date+datetime.timedelta(days=0)).replace('-', '')[:8]
            self.end_date = str(
                self.date+datetime.timedelta(days=1)).replace('-', '')[:8]

            if self.start_date == self.today_date:
                return


if __name__ == '__main__':
    date_ = {'yyyy/mm/dd'}
    while True:
        a = http_req_results(date=date_)
        a.set_db(host={},
                 port={},
                 user={},
                 passwd={},
                 database={})
        a.up_to_sql()
        date_ = a.end_date[:4]+'/'+a.end_date[4:6]+'/'+a.end_date[6:8]
        print(date_)
