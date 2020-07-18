# -*- coding: utf-8 -*-
import pymysql
import traceback
import threading
from settings import *
mutex = threading.Lock()


class MysqlUtil(object):

    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self):
        self.con = pymysql.connect(host=mysql_host,
                                   user=mysql_user,
                                   password=mysql_password,
                                   port=mysql_port,
                                   database=mysql_db,
                                   charset="utf8mb4")
        self.cur = self.con.cursor()
        # self.filter_users = self.__get_filter_users()

    def query(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def save_data(self, sql):
        try:
            if mutex.acquire():
                self.cur.execute(sql)
                self.con.commit()
                return True
        except pymysql.err.IntegrityError:
            return False
        except Exception:
            e = traceback.format_exc()
            print(e)
            return False
        finally:
            mutex.release()

    def update_data(self, sql):
        try:
            if mutex.acquire():
                self.cur.execute(sql)
                self.con.commit()
                return True
        except pymysql.err.IntegrityError:
            return False
        except Exception:
            e = traceback.format_exc()
            print(e)
            return False
        finally:
            mutex.release()


if __name__ == "__main__":
    mu = MysqlUtil()
    result = mu.query("select id, book_topic_url from t_fw_topic where status=1")
    print(result)
