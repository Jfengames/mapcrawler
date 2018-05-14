#!/usr/bin/python3
# coding=utf-8

"""
数据库操作接口
"""

import pymysql
from MapCrawler.sql_config import HOST,USER,PASSWD,PORT,DB,CHARSET

class GaodeMapSceneDbOper():

    TABLE_NAME="GaodeMapScene"

    def __init__(self):
        self.conn = pymysql.connect(host=HOST,
                                    port=PORT,
                                    user=USER,
                                    passwd=PASSWD,
                                    db=DB,
                                    charset=CHARSET)
        self.cursor = self.conn.cursor()

    def drop_table(self):
        """

        :return:
        """
        self.cursor.execute("drop table if exists %s"%self.TABLE_NAME)


    def create_table(self):
        """

        :return:
        """
        sql_str = """
        create table %s (id CHAR(20) primary key,
                    province CHAR(50),
                    city CHAR(50),
                    name char(50),
                    city_adcode CHAR(6),
                    district CHAR(50),
                    address  CHAR(100),
                    longtitude float,
                    lat float,
                    type11 char(100),
                    typecode char(6),
                    classify  char(100),
                    area float,
                    floor int,
                    shape text
                    );"""%self.TABLE_NAME
        self.cursor.execute(sql_str)



    def insert_item(self,items):
        """

        :param item:
        :return:
        """
        

    def delete_item(self,items):
        """

        :param item:
        :return:
        """
        pass

    def replace_item(self,items):
        """

        :param items:
        :return:
        """
        pass


if __name__=='__main__':
    db = GaodeMapSceneDbOper()
    db.create_table()
    print('create talbe;')
    db.drop_table()
    print('drop table;')
