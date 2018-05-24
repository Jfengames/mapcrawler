#!/usr/bin/python3
# coding=utf-8

"""
数据库操作接口
"""

import pymysql
from MapCrawler.config import HOST,USER,PASSWD,PORT,DB,CHARSET
import logging

logger = logging.getLogger(__name__)

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
                    name CHAR(50),
                    city_adcode CHAR(20),
                    district CHAR(50),
                    address  CHAR(100),
                    longtitude DOUBLE,
                    lat DOUBLE,
                    type CHAR(100),
                    typecode CHAR(20),
                    classify  CHAR(100),
                    area DOUBLE,
                    shape text
                    );"""%self.TABLE_NAME
        self.cursor.execute(sql_str)



    def insert_items(self, items):
        """

        :param item: items.PoiInfoItem
        :return:
        """
        sql_str = """
            insert into {}(id,
                    province,
                    city,
                    name,
                    city_adcode,
                    district,
                    address ,
                    longtitude,
                    lat,
                    type,
                    typecode,
                    classify ,
                    area,
                    shape) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""".format(self.TABLE_NAME)
        args = []
        for i in items:
            arg = (i['id'],\
                   i['province'],\
                   i['city'],\
                   i['name'],\
                   i['city_adcode'],\
                   i['district'],\
                   i['address'],\
                   i['center_long'],\
                   i['center_lat'],\
                   i['type'],\
                   i['typecode'],\
                   i['classify'],\
                   i['area'],\
                   i['shape'])
            args.append(arg)

        try:
            self.conn.ping(reconnect=True) #确保连接
            self.cursor.executemany(sql_str,args)
            self.conn.commit()
        except:
            self.conn.rollback()

    def is_item_exist_by_id(self,id):
        """

        :param item:
        :return:
        """
        sql_str = """
        select * from {} where id =%s;""".format(self.TABLE_NAME)
        self.conn.ping(reconnect=True) #确保连接
        self.cursor.execute(sql_str,id)

        if self.cursor.fetchone():
            return True
        else:
            return False

    def is_shape_null(self,id):
        """

        :param id:
        :return:
        """
        sql_str = """
        select shape from {} where id =%s;""".format(self.TABLE_NAME)
        self.conn.ping(reconnect=True) #确保连接
        self.cursor.execute(sql_str,id)

        res, = self.cursor.fetchone()
        if res == 'NULL':
            return True
        else:
            return False


    def delete_item(self,items):
        """

        :param item:
        :return:
        """
        pass

    def replace_items(self,items):
        """

        :param items:
        :return:
        """
        sql_str = """
            replace into {}(id,
                    province,
                    city,
                    name,
                    city_adcode,
                    district,
                    address ,
                    longtitude,
                    lat,
                    type,
                    typecode,
                    classify ,
                    area,
                    shape) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""".format(self.TABLE_NAME)
        args = []
        for i in items:
            arg = (i['id'], \
                   i['province'], \
                   i['city'], \
                   i['name'], \
                   i['city_adcode'], \
                   i['district'], \
                   i['address'], \
                   i['center_long'], \
                   i['center_lat'], \
                   i['type'], \
                   i['typecode'], \
                   i['classify'], \
                   i['area'], \
                   i['shape'])
            args.append(arg)
        try:
            self.conn.ping(reconnect=True) #确保连接
            self.cursor.executemany(sql_str,args)
            self.conn.commit()
        except Exception as e:
            logger.warning('数据更新到数据库中有误：%s'%e)
            self.conn.rollback()

    def __del__(self):
        self.conn.close()


# class GaodeDistrictOper():
#     TABLE_NAME = 'districts'
#     def __init__(self):
#
#         self.conn = pymysql.connect(host=HOST,
#                                     port=PORT,
#                                     user=USER,
#                                     passwd=PASSWD,
#                                     db=DB,
#                                     charset=CHARSET)
#         self.cursor = self.conn.cursor()
#
#     def create_table(self):
#         sql_str = """
#         create table %s (adcode char(6),
#                         province  CHAR(20),
#                         name CHAR(20),
#                         center char(50),
#                         shape text)"""

if __name__=='__main__':
    db = GaodeMapSceneDbOper()
    db.drop_table()
    print('drop table;')
    db.create_table()
    print('create talbe;')
    # print(db.is_shape_null('B017304CB1'))




