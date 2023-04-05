import csv
import sqlite3
import datetime
import os

class CSVtoSQLite():
    def __init__(self, db_path='database.db'):
        self.db_path = db_path

    def upload_csv(self, csv_path, table_name):
        # 
        conn = sqlite3.connect(self.db_path)

        # 
        with open(csv_path, encoding='utf-8', newline='') as csvfile:
            data = csv.reader(csvfile)
            header = next(data)
            num_cols = len(header)
            print("cols | ", num_cols)

            # check table
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            table_exists = c.fetchone() is not None

            # if not have table
            if not table_exists:
                # create table
                create_table_sql = "CREATE TABLE {} (".format(table_name)
                for i in range(num_cols):
                    create_table_sql += "col{} TEXT,".format(i+1)
                create_table_sql = create_table_sql.rstrip(',') + ")"

                c.execute(create_table_sql)

            # upload
            for row in data:
                if len(row) == num_cols: 
                    c.execute("INSERT INTO {} VALUES ({})".format(table_name, ','.join(['?']*num_cols)), row)

        conn.commit()
        conn.close()

        
        now = datetime.datetime.now()
        new_csv_path = os.path.splitext(csv_path)[0] + '_' + now.strftime('%Y-%m-%d_%H-%M-%S') + os.path.splitext(csv_path)[1]
        os.rename(csv_path, new_csv_path)
        print("new csv |", new_csv_path)


if __name__=="__main__":
    csv_to_sqlite = CSVtoSQLite('database.db')
    csv_to_sqlite.upload_csv('odds.csv', 'odds')
