from dbutil import DBUtil
import time
import random
from sys import argv


class UserInfoService(object):
    """
    UserInfo Service
    """

    def __init__(self, init_flag=False):
        """
        init 
        """
        path = 'data/userinfo.db'
        self.query_result = ""
        self.db = DBUtil(path, init_flag=init_flag)

    def save(self, data):
        """
            save one userinfo record
            
            data = [( (uid (int), name (string), mobile (string),  
                    father (string), balance (string), coin (int), 
                    device_code (string), token (string), os (string)
                    brand (string), mac (string), android_id (string) )]
        """
        save_sql = """INSERT INTO userinfo 
            (uid , username, mobile, father, balance, coin, device_code, token, os, brand, mac, android_id) 
            VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self.db.get_conn()
        self.db.save(conn, save_sql, data)

    def save_flag(self, data):
        """
            save one userflag record
            args: data = [(uid(int),)]
        """
        save_sql = """INSERT INTO userflag
                (uid) VALUES (?)
            """
        conn = self.db.get_conn()
        self.db.save(conn, save_sql, data)

    def save_read_record(self, data):
        """
            save one read record
            
            arg: data = [(uid(int), read_time(string), read_count(int))]
        """
        save_sql = """INSERT INTO userread
                (uid, read_time, read_count)
                VALUES
                (?, ?, ?)
            """
        conn = self.db.get_conn()
        self.db.save(conn, save_sql, data)

    def update(self, data):
        """
            update one userinfo record
            
            data = [
                (balance (string), coin (int), token (string), device_code(string), uid (int))
            ]
        """
        update_sql = """UPDATE userinfo 
                    SET balance=?, coin=?, token=?, device_code=?
                    WHERE uid=?
                """
        conn = self.db.get_conn()
        self.db.update(conn, update_sql, data)

    def update_read_flag(self, data):
        """
            update one userflag record
            
            data = [(read_flag(int{0,1,2}), (uid(int))]
        """
        update_sql = """UPDATE userflag
                    SET read_flag=?
                    WHERE uid=?
                """
        conn = self.db.get_conn()
        self.db.update(conn, update_sql, data)

    def clear_all_flag(self):
        """
            clear all userflag record
        """
        update_sql = """ UPDATE userflag
                    SET read_flag=?
                """
        conn = self.db.get_conn()
        self.db.update(conn, update_sql, [(0,)])

    def get_all(self):
        """
            query all userinfo records
        """
        sql = """SELECT * FROM userinfo"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql)
        return self.query_result

    def get_all_user_read(self):
        """
            query all userread
        """
        sql = """SELECT * FROM userread"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql)
        return self.query_result

    def get_all_user_flag(self, read_flag):
        """
            query all userinfo by read_flag
            
            args: read_flag(0, 1, 2)
            return: userinfo list
        """
        sql = """SELECT * FROM userflag WHERE read_flag=?"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql, (read_flag,))
        return self.query_result

    def get_one(self, uid):
        """
            query one userinfo record by uid
            arg: uid (int)
            return one userinfo or None
        """
        sql = """SELECT * FROM userinfo WHERE uid=?"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql, (uid,))

        if len(self.query_result) > 0:
            return self.query_result[0]
        else:
            return None

    def get_user_mobile(self, mobile):
        """
            query one userinfo record by mobile
            
            arg: mobile (string)
            :return one userinfo or None
        """
        sql = """SELECT * FROM userinfo WHERE mobile=?"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql, (mobile,))

        if len(self.query_result) > 0:
            return self.query_result[0]
        else:
            return None

    def get_one_user(self):
        """
            query one userinfo record where read_flag=0
            :return one userinfo or None
        """

        sql = """SELECT * FROM userinfo ui, userflag uf
            WHERE ui.uid = uf.uid AND uf.read_flag=0"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql)
        if len(self.query_result) > 0:
            return self.query_result[random.randint(0, len(self.query_result) - 1)]
        else:
            return None

    def get_all_already_read_user(self):
        """
            query userinfo records where read_flag=1
            :return  userinfo list
        """
        sql = """SELECT * 
            FROM userinfo ui, userflag uf
            WHERE ui.uid = uf.uid AND uf.read_flag=2"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql)
        return self.query_result

    def get_all_not_read_user(self):
        """
            query userinfo records where read_flag=0
            :return userinfo list
        """
        sql = """SELECT * FROM userinfo ui, userflag uf
            WHERE ui.uid = uf.uid AND uf.read_flag=0"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql)
        return self.query_result

    def get_all_reading_user(self):
        """
            query userinfo records where read_flag=1
            :return userinfo list 
        """
        sql = """SELECT * FROM userinfo ui, userflag uf
            WHERE ui.uid = uf.uid AND uf.read_flag = 1"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql)
        return self.query_result

    def get_user_read_count(self, uid):
        """
            query total read count by uid
            :return read_count (int)
        """
        time_ms = int(time.time())
        time_local = time.localtime(time_ms)
        time_format = "%Y-%m-%d"
        time_str = time.strftime(time_format, time_local)
        time_local = time.strptime(time_str, time_format)
        time_ms = int(time.mktime(time_local))
        sql = """SELECT sum(read_count) FROM userread
                WHERE uid = ? AND read_time > ?
            """
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql, (uid, time_ms))
        if self.query_result[0][0]:
            return self.query_result[0][0]
        else:
            return 0

    def get_user_coin(self, coin):
        """
            query userinfo records where coin >= coin
        """
        sql = """SELECT * FROM userinfo
                WHERE coin >= ?"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql, (coin,))
        return self.query_result

    def get_user_balance(self, balance):
        """
            query userinfo records where balance >= balance
            :return userinfo list 
        """
        sql = """SELECT * FROM userinfo
                WHERE balance >= ?"""
        conn = self.db.get_conn()
        self.query_result = self.db.fetchall(conn, sql, (balance,))
        return self.query_result

    def get_time_str(self, time_ms, time_format="%Y-%m-%d"):
        """
            transfer the time_ms to some format
            :return format_time string
        """
        time_local = time.localtime(time_ms)
        time_str = time.strftime(time_format, time_local)
        return time_str


def main():
    uis = UserInfoService(init_flag=False)
    if len(argv) > 1:
        if argv[1] == "clear":
            uis.clear_all_flag()
        elif argv[1] == "coin":
            query_result = uis.get_user_coin(argv[2])
            for user in query_result:
                print(
                    "UID: {}, Name: {}, Mobile: {}, Father: {}, Balance: {}, Coin:{}".format(user[0], user[1], user[2],
                                                                                             user[3], user[4],
                                                                                             user[5]))
        elif argv[1] == "balance":
            query_result = uis.get_user_balance(argv[2])
            for user in query_result:
                print(
                    "UID: {}, Name: {}, Mobile: {}, Father: {}, Balance: {}, Coin:{}".format(user[0], user[1], user[2],
                                                                                             user[3], user[4],
                                                                                             user[5]))
        elif argv[1] == "mobile":
            query_result = uis.get_user_mobile(argv[2])
            for user in query_result:
                print(
                    "UID: {}, Name: {}, Mobile: {}, Father: {}, Balance: {}, Coin:{}".format(user[0], user[1], user[2],
                                                                                             user[3], user[4],
                                                                                             user[5]))
        elif argv[1] == "all":
            all_user = uis.get_all()
            for user in all_user:
                print(
                    "UID: {}, Name: {}, Mobile: {}, Father: {}, Balance: {}, Coin:{}".format(user[0], user[1], user[2],
                                                                                             user[3], user[4], user[5]))
    else:
        all_user = uis.get_all()
        already_user = uis.get_all_already_read_user()
        not_user = uis.get_all_not_read_user()
        reading_user = uis.get_all_reading_user()

        all_user_num = len(all_user)
        already_user_num = len(already_user)
        print("Total User Count: {}".format(all_user_num))
        print("Done: %d Rate: %.3f" % (already_user_num, (already_user_num / float(all_user_num))))
        print("Undone: {}".format(len(not_user)))
        print("Doing: {}".format(len(reading_user)))

        for user in already_user:
            query_result = uis.get_user_read_count(user[0])
            print("Mobile: %s, Total_read: %s" % (user[2], query_result))
            if query_result < 7:
                uis.update_read_flag([(0, user[0])])
            else:
                uis.update_read_flag([(2, user[0])])

        for user in all_user:
            query_result = uis.get_user_read_count(user[0])
            if query_result < 7:
                uis.update_read_flag([(0, user[0])])
            else:
                uis.update_read_flag([(2, user[0])])
            # print(
            #     "UID: {}, Name: {}, Mobile: {}, Father: {}, Balance: {}, Coin:{}".format(user[0], user[1], user[2],
            #                                                                            user[3], user[4], user[5]))


# def init_data_base():
#     uis = UserInfoService(init_flag=True)

if __name__ == "__main__":
    main()
    # init_data_base()
