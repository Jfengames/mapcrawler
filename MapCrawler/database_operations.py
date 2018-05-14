#!/usr/bin/python3
# coding=utf-8

"""
数据库操作接口
"""

import pymysql
from MapCrawler.sql_config import HOST,USER,PASSWD,PORT,DB,CHARSET

class GaodeMapSceneDbOper():
    def __init__(self):
        self.conn = pymysql.connect(host=HOST,
                                    port=PORT,
                                    user=USER,
                                    passwd=PASSWD,
                                    db=DB,
                                    charset='utf8')

    def drop_table(self):
        """

        :return:
        """
        pass

    def create_table(self):
        """

        :return:
        """
        sql_str = """
        create table GaodeMapScene(id CHAR(20) not Null,
                    province CHAR(50),
                    city  CHAR(50),
                    name char(50),
                    city_adcode CHAR(6),
                    district CHAR(50),
                    address  CHAR(100),
                    lang float,
                    lat float,
                    type char(100),
                    typecode char(6),
                    classify  char(100),
                    area float,
                    shape varchar
                    primary key id
                    )
        """

    def insert_item(self,items):
        """

        :param item:
        :return:
        """
        pass

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
