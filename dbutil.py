
import sqlite3
import os


class DBUtil(object):
    SHOW_SQL = False
    init_flag = True
        
    def __init__(self, path, show=False, init_flag=False):
        self.DB_FILE_PATH = path
        self.SHOW_SQL = show
        self.init_flag = init_flag
        
        if self.init_flag:
            conn = self.get_conn()
            self.drop_table(conn, "userinfo")
            self.close_all(conn, None)
            conn = self.get_conn()
            self.drop_table(conn, "userread")
            self.close_all(conn, None)
            conn = self.get_conn()
            self.drop_table(conn, "userflag")
            self.close_all(conn, None)
            conn = self.get_conn()
            userinfo_sql = """CREATE TABLE IF NOT EXISTS `userinfo` (
                  `uid` int(11) NOT NULL,
                  `username` var(11) DEFAULT 0,
                  `mobile` varchar(20) NOT NULL,
                  `father` varchar(10) DEFAULT NULL,
                  `balance` varchar(20) NOT NULL,
                  `coin` int(11) DEFAULT 0,
                  `device_code` var(64) NOT NULL,
                  `token` var(256) NOT NULL,
                  `os` var(16) NOT NULL,
                  `brand` var(16) NOT NULL,
                  `mac` var(16) NOT NULL,
                  `android_id` var(32) NOT NULL,
                   PRIMARY KEY (`uid`)
                )"""
            self.create_table(conn, userinfo_sql)

            self.close_all(conn, None)
            conn = self.get_conn()
            userread_sql = """CREATE TABLE IF NOT EXISTS `userread` (
                  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                  `uid` int(11) NOT NULL,
                  `read_time` varchar(20) NOT NULL,
                  `read_count` int(11) DEFAULT 0,
                   FOREIGN KEY(uid) REFERENCES userinfo(uid)
                )"""

            self.create_table(conn, userread_sql)
            self.close_all(conn, None)
            conn = self.get_conn()
            userflag_sql = """CREATE TABLE IF NOT EXISTS `userflag` (
                  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                  `uid` int(11) NOT NULL,
                  `read_flag` int(2) DEFAULT 0,
                   FOREIGN KEY(`uid`) REFERENCES `userinfo`(`uid`)
                )"""

            self.create_table(conn, userflag_sql)
            self.close_all(conn, None)

    def get_conn(self):
        """
        get connection object to database
        :return: connection object
        """
        conn = sqlite3.connect(self.DB_FILE_PATH)
        if os.path.exists(self.DB_FILE_PATH) and os.path.isfile(self.DB_FILE_PATH):
            return conn
        else:
            return sqlite3.connect(':memory:')

    def get_cursor(self, conn):
        """
        get cursor object
        :param conn: connection object
        :return: cursor object
        """
        if conn is not None:
            return conn.cursor()
        else:
            return self.get_conn().cursor()

    def drop_table(self, conn, table):
        """
            drop the table if it exists
        :param conn: connection object
        :param table: table name
        :return: 
        """
        if table is not None and table != '':
            sql = 'DROP TABLE IF EXISTS ' + table
            if self.SHOW_SQL:
                print('execute sql:[{}]'.format(sql))
            cu = self.get_cursor(conn)
            cu.execute(sql)
            conn.commit()
            print('delete table [{}] success!'.format(table))
            self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(table))

    def create_table(self, conn, sql):
        """
        create table 
        :param conn: connection object
        :param sql: sql statement
        :return: 
        """
        if sql is not None and sql != '':
            cu = self.get_cursor(conn)
            if self.SHOW_SQL:
                print('execute sql:[{}]'.format(sql))
            cu.execute(sql)
            conn.commit()
            print('create table [{}] success!'.format("userinfo"))
            self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def close_all(self, conn, cu):
        """
        close the cursor and connection
        :param conn: connection object
        :param cu: cursor object
        :return: 
        """
        try:
            if cu is not None:
                cu.close()
        finally:
            if conn is not None:
                conn.close()

    def save(self, conn, sql, data):
        """
        insert the data into the database
        :param conn: connection object
        :param sql: sql statement
        :param data: required params
        :return: 
        """
        if sql is not None and sql != '':
            if data is not None:
                cu = self.get_cursor(conn)
                for d in data:
                    if self.SHOW_SQL:
                        print('execute sql:[{}], params:[{}]'.format(sql, d))
                    cu.execute(sql, d)
                    conn.commit()
                self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def fetchall(self, conn, sql, data=()):
        """
        fetch all rows
        :param conn: connection object
        :param sql: sql statement
        :param data: required params (tuple)
        :return: the result set if not empty
        """
        if sql is not None and sql != '':
            cu = self.get_cursor(conn)
            if self.SHOW_SQL:
                print('execute sql:[{}]'.format(sql))
            if data:
                cu.execute(sql, data)
            else:
                cu.execute(sql)
            r = cu.fetchall()
            return r
        else:
            print('the [{}] is empty or equal None!'.format(sql)) 
            return []

    def update(self, conn, sql, data):
        """
        update the data in database
        :param conn: connection object
        :param sql: sql statement
        :param data: the required params
        :return: 
        """
        if sql is not None and sql != '':
            if data is not None:
                cu = self.get_cursor(conn)
                for d in data:
                    if self.SHOW_SQL:
                        print('execute sql:[{}], params:[{}]'.format(sql, d))
                    cu.execute(sql, d)
                    conn.commit()
                self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def delete(self, conn, sql, data):
        """
        delte the data in database
        :param conn: connection object
        :param sql: sql statement
        :param data: the required params
        :return: 
        """
        if sql is not None and sql != '':
            if data is not None:
                cu = self.get_cursor(conn)
                for d in data:
                    if self.SHOW_SQL:
                        print('execute sql: [{}], params: [{}]'.format(sql, d))
                    cu.execute(sql, d)
                    conn.commit()
                self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))
