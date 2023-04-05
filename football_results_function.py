import json
import urllib.request
import time
import datetime
import ast
import csv
from selenium import webdriver


class http_req_results():
    def __init__(self, date='2016/01/01', Num_day=1, file_address='football_results.py'):
        self.date_format = '%Y/%m/%d'
        self.date = datetime.datetime.strptime(date, self.date_format)
        self.start_date = str(
            self.date+datetime.timedelta(days=0)).replace('-', '')[:8]
        self.end_date = str(
            self.date+datetime.timedelta(days=Num_day)).replace('-', '')[:8]
        self.mark_date = f'{self.end_date[:4]}/{self.end_date[4:6]}/{self.end_date[6:8]}'
        self.today_date = str(datetime.datetime.now()).replace('-', '')[:8]
        self.file = file_address
        self.count = 0
        self.data_format = {
            'officialID': '',
            'MatchID': '',
            'date': '',
            'homeTeam_CH': '',  # 主隊中文名
            'homeTeam_EN': '',  # 主隊英文名
            'awayTeam_CH': '',  # 客隊中文名
            'awayTeam_EN': '',  # 客隊英文名
            'tShortCH': '',  # 聯賽中文名
            'tShortEN': '',  # 聯賽英文名
            'crs': '',  # 全場波膽
            'fcs': '',  # 半場波膽
            'fha': '',  # 半埸主客和
            'fts': '',  # 首隊入球
            'had': '',  # 全場主客和
            'hft': '',  # 半全埸
            'ooe': '',  # 入球單雙
            'ttg': ''  # 總入球
        }
        self.url_findSourse = f'https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate={self.start_date}&enddate={self.end_date}&teamid=default'
        self.header = {'cookie': '',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
        #print(self.start_date, self.end_date, self.mark_date, self.today_date)

    def get_cookie(self):
        browser = webdriver.Chrome()
        browser.get('https://bet.hkjc.com/football/')
        time.sleep(10)
        dictcookie = browser.get_cookies()
        cookies_results = ''
        for i in dictcookie:
            cookies_results += f"{i['name']}={i['value']}; "
        # print(cookies_results)
        return cookies_results

    def matches_count(self, url, header):
        #print(url, header)
        print(f'start | {self.start_date} - {self.end_date}')
        match_count = 0
        for i in range(20):
            try:
                time.sleep(5)
                with urllib.request.urlopen(urllib.request.Request(url, headers=header)) as response:
                    data_txt = response.read().decode('utf-8')
                results = json.loads(data_txt)
                match_count = results[0]['matchescount']
                print(f'count | {match_count}')
                return str(match_count)
            except Exception as Error:
                print(f'matches_count | {Error}')
        return False

    def show_date(self):
        print(f"start_date {self.start_date} - end_date {self.end_date}")

    def matches_url(self):
        page_no = 2  # &pageno=2
        self.header['cookie'] = self.get_cookie()
        match_count=self.matches_count(self.url_findSourse, self.header)
        if match_count:
            count = int(match_count)
            gen_url = []
            gen_url.append(self.url_findSourse)
            count -= 20
            while True:
                try:
                    if count >= 20:
                        tmp_url = (self.url_findSourse+'&pageno='+str(page_no))
                        page_no += 1
                        count -= 20
                        gen_url.append(str(tmp_url))
                    elif count > 0:
                        tmp_url = (self.url_findSourse+'&pageno='+str(page_no))
                        gen_url.append(str(tmp_url))
                        return gen_url, count
                    else:
                        return gen_url, count
                except Exception as Error:
                    print(f'def matches_url | {Error}')
        else:
            return False

    def get_results(self):
        tmp_list = []
        url_link, count = self.matches_url()
        #print(url_link , count)
        for url in url_link:
            with urllib.request.urlopen(urllib.request.Request(url, headers=self.header)) as response:
                data_txt = response.read().decode('utf-8')
            results = json.loads(data_txt)
            page = results[0]['matches']
            while True:
                if url == url_link[-1]:
                    mark = count
                else:
                    mark = 20
                for i in range(mark):
                    tmp_results_dict = self.data_format
                    for tmp_results, source in [('officialID', page[i]['matchIDinofficial']),
                                                ('officialID',
                                                page[i]['matchIDinofficial']),
                                                ('MatchID',
                                                 page[i]['matchID']),
                                                ('date',
                                                page[i]['matchIDinofficial'][:8]),
                                                ('homeTeam_CH',
                                                page[i]['homeTeam']['teamNameCH']),
                                                ('homeTeam_EN',
                                                page[i]['homeTeam']['teamNameEN']),
                                                ('awayTeam_CH',
                                                page[i]['awayTeam']['teamNameCH']),
                                                ('awayTeam_EN',
                                                page[i]['awayTeam']['teamNameEN']),
                                                ('tShortCH',
                                                page[i]['tournament']['tShortCH']),
                                                ('tShortEN',
                                                page[i]['tournament']['tShortEN']),
                                                ('crs', page[i]['results']
                                                ['CRS'].replace(':', '')),
                                                ('fcs', page[i]['results']
                                                ['FCS'].replace(':', '')),
                                                ('fha', page[i]
                                                 ['results']['FHA']),
                                                ('fts', page[i]
                                                 ['results']['FTS']),
                                                ('had', page[i]
                                                 ['results']['HAD']),
                                                ('hft', page[i]['results']
                                                ['HFT'].replace(':', '')),
                                                ('ooe', page[i]
                                                 ['results']['OOE']),
                                                ('ttg', page[i]['results']['TTG'])]:
                        try:
                            tmp_results_dict[tmp_results] = source
                        except Exception as Error:
                            print(Error)
                            pass
                    with open(self.file, 'a', encoding='utf-8') as txt:  # save data
                        txt.write(f'{str(tmp_results_dict)}\n')
                    tmp_list.append(i)
                if len(tmp_list) == 20:  # check finish
                    tmp_list = []
                    break
                elif 20 > len(tmp_list) > 0:  # check count
                    if len(tmp_list) == mark:
                        break
        list = []
        with open(self.file, 'r', encoding='utf-8') as txt:
            for i in txt.readlines():
                list.append(ast.literal_eval(i.replace('\n', '')))
        return list

    def gen_csv(self, csv_name):
        # Open CSV file in write mode
        with open(csv_name, 'w', newline='',encoding='utf-8') as csvfile:
            # Create CSV writer object
            writer = csv.writer(csvfile)
            writer.writerow(['officialID',
            'MatchID',
            'date',
            'homeTeam_CH',
            'homeTeam_EN',
            'awayTeam_CH',
            'awayTeam_EN',
            'tShortCH',
            'tShortEN',
            'crs',
            'fcs',
            'fha',
            'fts',
            'had',
            'hft',
            'ooe',
            'ttg'])
            # Write data to CSV file
            for i in self.get_results():
                writer.writerow([i['officialID'],i['MatchID'],i['date'],i['homeTeam_CH'],i['homeTeam_EN'],i['awayTeam_CH'],i['awayTeam_EN'],i['tShortCH'],i['tShortEN'],i['crs'],i['fcs'],i['fha'],i['fts'],i['had'],i['hft'],i['ooe'],i['ttg']])



if __name__ == "__main__":
    http_req_results('2016/01/01', 1,
                     'football_results').gen_csv('results.csv')
