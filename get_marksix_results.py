import json
import urllib.request
import time
import calendar
import datetime
from selenium import webdriver
class http_req_results():
    def __init__(self, date='1993/01/01', file_address=''):
        self.data_format = {
            'date': '',  # 日期
            'id': '',  # ID
            'inv': '',  # 總投注
            'no': '',  # 開彩號碼
            'sno': '',  # 特別號碼
            'p1': '',  # 一獎彩金
            'p1u': '',  # 一獎人數
            'p2': '',
            'p2u': '',
            'p3': '',
            'p3u': '',
            'p4': '',
            'p4u': '',
            'p5': '',
            'p5u': '',
            'p6': '',
            'p6u': '',
            'p7': '',
            'p7u': ''
        }
        self.date_format = '%Y/%m/%d'
        self.date = datetime.datetime.strptime(date, self.date_format)
        self.start_date = str(self.date).replace('-', '')[:8]
        def get_tmp():
            return calendar.monthrange(int(str(self.date)[:4]), int(str(self.start_date)[4:6]))

        tmp_1, tmp_2 = get_tmp()
        self.end_date = self.start_date[:4]+self.start_date[4:6]+str(tmp_2)
        self.file_name = file_address
        self.today_date = str(datetime.datetime.now()).replace('-', '')[:8]
        self.url_findSourse = f'https://bet.hkjc.com/marksix/getJSON.aspx?sd={self.start_date}&ed={self.end_date}&sb=0'
        self.header = {'cookie': '',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    def get_cookie(self):
        browser = webdriver.Chrome()
        browser.get('https://bet.hkjc.com/marksix/')
        time.sleep(10)
        cookies_results = ''
        dictcookie = browser.get_cookies()
        for i in dictcookie:
            cookies_results += f"{i['name']}={i['value']}; "
        #print(cookies_results)
        return cookies_results

    def get_results(self):
        self.header['cookie'] = self.get_cookie()
        with urllib.request.urlopen(urllib.request.Request(url=self.url_findSourse, headers=self.header)) as response:
            data_txt = response.read().decode('utf-8')
        results = json.loads(data_txt)
        for source in results:
            tmp_results_dict = self.data_format
            for type in ['date', 'id', 'inv', 'no', 'p1', 'p1u', 'p2', 'p2u', 'p3', 'p3u', 'p4', 'p4u', 'p5', 'p5u', 'p6', 'p6u', 'p7', 'p7u', 'sno']:
                try:
                    tmp_results_dict[type] = source[type]
                except Exception as Error:
                    print('Error | {} {}'.format(source['id'], Error))
            with open(self.file_name, 'a', encoding='utf-8') as txt:  # save data
                txt.write(f'{str(tmp_results_dict)}\n')
        print('Finish | Thanks for use')


if __name__ == "__main__":
    http_req_results('2023/01/01', 'A:\\Python_notes\\jbet_proj\\marksix_results.py').get_results()
