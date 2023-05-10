import json
import urllib.request
import time
import calendar
import datetime
from selenium import webdriver
import mysql.connector


class http_req_results():
    def __init__(self, date='1993/01', file_address='marksix_results.py'):
        self.data_format = {
            'date': '',  # 日期
            'id': '',  # ID
            'inv': '',  # 總投注
            'no_1': '',  # 開彩號碼
            'no_2': '',
            'no_3': '',
            'no_4': '',
            'no_5': '',
            'no_6': '',
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
        self.date = datetime.datetime.strptime(
            f'{date}/01', self.date_format)
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
        cookies_results = ''
        try:
            browser = webdriver.Chrome()
            browser.get('https://bet.hkjc.com/marksix/')
            time.sleep(5)
            dictcookie = browser.get_cookies()
            for i in dictcookie:
                cookies_results += f"{i['name']}={i['value']}; "
            print(cookies_results)
        except Exception as Error:
            print(Error)
        return cookies_results

    def get_results(self):
        while True:
            with urllib.request.urlopen(urllib.request.Request(self.url_findSourse, headers=self.header)) as response:
                data_txt = response.read().decode('utf-8')
            try:
                results_ = json.loads(data_txt)
                print(f'get | {len(results_)}')
                return results_
            except Exception as Error:
                print(Error)
                self.header['cookie'] = self.get_cookie()

    def data_filter(self, gen_file=False, file_name='results_marksix'):
        
        data_list = []
        count = 0
        results_list = self.get_results()
        for i in results_list:
            data_list.append(self.data_format.copy())
            data_list[count]['id'] = i['id']
            data_list[count]['date'] = i['date']
            data_list[count]['dd']=int(i['date'][:2])
            data_list[count]['mm']=int(i['date'][3:5])
            data_list[count]['yyyy']=int(i['date'][6:])
            if 'inv' in i:
                data_list[count]['inv'] = i['inv'].replace(',', '')
            if 'p1' in i:
                data_list[count]['p1'] = i['p1'].replace(',', '')
                data_list[count]['p1u'] = i['p1u'].replace(',', '')
            if 'p2' in i:
                data_list[count]['p2'] = i['p2'].replace(',', '')
                data_list[count]['p2u'] = i['p2u'].replace(',', '')
            if 'p3' in i:
                data_list[count]['p3'] = i['p3'].replace(',', '')
                data_list[count]['p3u'] = i['p3u'].replace(',', '')
            if 'p4' in i:
                data_list[count]['p4'] = i['p4'].replace(',', '')
                data_list[count]['p4u'] = i['p4u'].replace(',', '')
            if 'p5' in i:
                data_list[count]['p5'] = i['p5'].replace(',', '')
                data_list[count]['p5u'] = i['p5u'].replace(',', '')
            if 'p6' in i:
                data_list[count]['p6'] = i['p6'].replace(',', '')
                data_list[count]['p6u'] = i['p6u'].replace(',', '')
            if 'p7' in i:
                data_list[count]['p7'] = i['p7'].replace(',', '')
                data_list[count]['p7u'] = i['p7u'].replace(',', '')
            data_list[count]['sno'] = i['sno']
            no_list = str(i['no']).split('+')
            data_list[count]['no_1'] = no_list[0]
            data_list[count]['no_2'] = no_list[1]
            data_list[count]['no_3'] = no_list[2]
            data_list[count]['no_4'] = no_list[3]
            data_list[count]['no_5'] = no_list[4]
            data_list[count]['no_6'] = no_list[5]
            count += 1
        print(f'filter | {len(data_list)}')
        return data_list

    # set & execute sql
    def set_db(self, host, port, user, passwd, database):
        self.db_connect = mysql.connector.connect(
            host=host, port=port, user=user, passwd=passwd, database=database)
        self.cursor = self.db_connect.cursor()

    def up_to_sql(self):
        list_ = self.data_filter()
        for i in list_:
            print(i['id'])
            self.cursor.execute(
                """select * from `marksix_results` where `id`=%s;""", (i['id'],))
            countrow = self.cursor.fetchall()
            if len(countrow):
                self.cursor.execute(
                    '''update `marksix_results` set date=%s,yyyy=%s,mm=%s,dd=%s,inv=%s,p1=%s,p1u=%s,p2=%s,p2u=%s,p3=%s,p3u=%s,p4=%s,p4u=%s,p5=%s,p5u=%s,p6=%s,p6u=%s,p7=%s,p7u=%s,sno=%s,no_1=%s,no_2=%s,no_3=%s,no_4=%s,no_5=%s,no_6=%s where id=%s''',
                    (i['date'],i['yyyy'],i['mm'],i['dd'], i['inv'], i['p1'], i['p1u'], i['p2'], i['p2u'], i['p3'], i['p3u'], i['p4'], i['p4u'], i['p5'], i['p5u'],
                     i['p6'], i['p6u'], i['p7'], i['p7u'], i['sno'], i['no_1'], i['no_2'], i['no_3'], i['no_4'], i['no_5'], i['no_6'], i['id'])
                )
            else:
                self.cursor.execute(
                    '''insert into `marksix_results` (id,date,yyyy,mm,dd,,inv,p1,p1u,p2,p2u,p3,p3u,p4,p4u,p5,p5u,p6,p6u,p7,p7u,sno,no_1,no_2,no_3,no_4,no_5,no_6) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                    (i['id'], i['date'],i['yyyy'],i['mm'],i['dd'], i['inv'], i['p1'], i['p1u'], i['p2'], i['p2u'], i['p3'], i['p3u'], i['p4'], i['p4u'], i['p5'],
                     i['p5u'], i['p6'], i['p6u'], i['p7'], i['p7u'], i['sno'], i['no_1'], i['no_2'], i['no_3'], i['no_4'], i['no_5'], i['no_6'])
                )

            self.db_connect.commit()


if __name__ == "__main__":
    year = 1993
    while True:
        for mo in [1,2,3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            date_ = str(year)+'/'+str(mo)
            print(date_)
            a = http_req_results(date_)

            a.set_db(host={}, port={}, user={},
                     passwd={}, database={})
            a.up_to_sql()
        year += 1
        time.sleep(2)
    
