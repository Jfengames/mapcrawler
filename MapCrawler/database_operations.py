#!/usr/bin/python3
# coding=utf-8

"""
数据库操作接口
"""

import pymysql
import numpy as np
from MapCrawler.config import HOST,USER,PASSWD,PORT,DB,CHARSET
from MapCrawler.toolskit import gcj2wgs
import logging
logger = logging.getLogger(__name__)


class GaodeMapSceneDbOper():

    TABLE_NAME="GaodeMapScene"
    DISTRICT_NAME = 'GaodeMap_DistrictShape'

    def __init__(self):
        self.conn = pymysql.connect(host=HOST,
                                    port=PORT,
                                    user=USER,
                                    passwd=PASSWD,
                                    db=DB,
                                    charset=CHARSET)
        self.cursor = self.conn.cursor()

    # def drop_table(self):
    #     """
    #
    #     :return:
    #     """
    #     self.cursor.execute("drop table if exists %s"%self.TABLE_NAME)


    def create_table(self):
        """

        :return:
        """
        sql_str = """
        create table %s (id CHAR(20) ,
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
                    shape TEXT,
                    wgs_long DOUBLE,
                    wgs_lat DOUBLE,
                    wgs_shape TEXT,
                    PRIMARY KEY (id,city_adcode)
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
                    shape,
                    wgs_long,
                    wgs_lat,
                    wgs_shape) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""".format(self.TABLE_NAME)
        args = []
        for i in items:
            wgs_long,wgs_lat,wgs_shape = self.get_wgs_from_item(i['center_long'],
                                                                i['center_lat'],
                                                                i['shape'])
            arg = (i['id'],\
                   i['province'],\
                   i['city'],\
                   i['name'],\
                   i['city_adcode'],\
                   i['district'],\
                   i['address'],\
                   i['center_long'],
                   i['center_lat'],\
                   i['type'],\
                   i['typecode'],\
                   i['classify'],\
                   i['area'],\
                   i['shape'],\
                   wgs_long,
                   wgs_lat,
                   wgs_shape)
            args.append(arg)

        try:
            self.conn.ping(reconnect=True) #确保连接
            self.cursor.executemany(sql_str,args)
            self.conn.commit()
        except:
            self.conn.rollback()

    def is_item_exist_by_id_city_adcode(self,id,city_adcode):
        """

        :param item:
        :return:
        """
        sql_str = """
        select * from {} where id =%s and city_adcode=%s;""".format(self.TABLE_NAME)
        self.conn.ping(reconnect=True) #确保连接
        self.cursor.execute(sql_str,(id,city_adcode))

        if self.cursor.fetchone():
            return True
        else:
            return False

    def select_city_polyline(self, adcode):
        """

        :param item:
        :return:
        """
        sql_str = """
        select * from {} where adcode =%s;""".format(self.DISTRICT_NAME)
        self.cursor.execute(sql_str,adcode)
        res = self.cursor.fetchone()
        return res[5]

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
                    shape,
                    wgs_long,
                    wgs_lat,
                    wgs_shape) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""".format(self.TABLE_NAME)
        args = []
        for i in items:
            wgs_long,wgs_lat,wgs_shape = self.get_wgs_from_item(i['center_long'],
                                                                i['center_lat'],
                                                                i['shape'])
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
                   i['shape'],\
                   wgs_long,
                   wgs_lat,
                   wgs_shape)
            args.append(arg)
        try:
            self.conn.ping(reconnect=True) #确保连接
            self.cursor.executemany(sql_str,args)
            self.conn.commit()
        except Exception as e:
            logger.warning('数据更新到数据库中有误：%s'%e)
            self.conn.rollback()



    def get_wgs_from_item(self,long,lat,shape):
        wgs_long, wgs_lat = gcj2wgs(float(long),
                                    float(lat))
        wgs_shape = []
        if shape == 'NULL':
            wgs_shape = None
        else:
            vertexes = np.array(
                [float(i) for i in shape.replace('|', ',').replace(';', ',').split(',')]).reshape(-1, 2)
            for lo, la in vertexes:
                _lo, _la = gcj2wgs(lo, la)
                wgs_shape.append(','.join([str(_lo), str(_la)]))

            wgs_shape = ';'.join(wgs_shape)
        return wgs_long,wgs_lat,wgs_shape


    def  add_wgs_to_item(self):
        NUM_TO_COMMIT = 100

        query_str = """
                select * from {}
                """.format(self.TABLE_NAME)

        update_str="""
            update {} set wgs_long=%s,wgs_lat=%s,wgs_shape=%s
            where id = %s and wgs_long is NULL;""".format(self.TABLE_NAME)

        with self.conn.cursor(pymysql.cursors.DictCursor) as query_cursor:
            query_cursor.execute(query_str)
            count = 0
            for one in query_cursor:
                wgs_long,wgs_lat,wgs_shape = self.get_wgs_from_item(one['longtitude'],
                                                                    one['lat'],
                                                                    one['shape'])

                self.cursor.execute(update_str,(wgs_long,wgs_lat,wgs_shape,one['id']))
                count+=1
                if count < NUM_TO_COMMIT:
                    continue
                else:
                    print('提交数据库增加%s条数据的wgc信息'%count)
                    self.conn.commit()
                    count=0

            self.conn.commit()

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
    # db.drop_table()
    # print('drop table;')
    # db.create_table()
    # print('create talbe;')
    # print(db.is_shape_null('B017304CB1'))
    db.add_wgs_to_item()




