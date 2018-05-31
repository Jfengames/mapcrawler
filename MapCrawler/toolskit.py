#!/usr/bin/python3
# coding =urt-8


"""
坐标系转换……
网格生成
"""
import numpy as np
import requests
import time
import math
from matplotlib.path import Path
from pymysql.cursors import DictCursor
import logging
logger = logging.getLogger(__name__)

#import sys
#sys.path.append('C:\\Users\\X1Carbon\\MapCrawler')
from MapCrawler.config import ADSL_SERVER_AUTH,ADSL_SERVER_URL

# from MapCrawler.database_operations import GaodeMapSceneDbOper

def gcj2wgs(long,lat):
    assert type(long) in [float, np.float64], '经度数据类型需要为浮点型 '
    assert type(lat) in [float, np.float64], '维度数据类型需要为浮点型 '
    a = 6378245.0  # 克拉索夫斯基椭球参数长半轴a
    ee = 0.00669342162296594323  # 克拉索夫斯基椭球参数第一偏心率平方
    PI = 3.14159265358979324  # 圆周率
    # 以下为转换公式
    x = long - 105.0
    y = lat - 35.0
    # 经度
    dLon = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x));
    dLon += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0;
    dLon += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0;
    dLon += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0;
    # 纬度
    dLat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x));
    dLat += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0;
    dLat += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0;
    dLat += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0;
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI);
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI);
    _long = long - dLon
    _lat = lat - dLat

    return _long,_lat

def wgc2gcj(long,lat):
    assert type(long)==float,'经度数据类型需要为浮点型 '
    assert type(lat)==float,'维度数据类型需要为浮点型 '
    pass

    return round(_long,6),round(_lat,6)


def generate_grids(start_long,start_lat,end_long,end_lat,resolution):
    """
    根据起始的经纬度和分辨率，生成需要需要的网格.
    方向为左上，右下，所以resolution应为 负数，否则未空
    :param start_long:
    :param start_lat:
    :param end_long:
    :param end_lat:
    :param resolution:
    :return:
    """
    assert start_long < end_long,'需要从左上到右下设置经度，start的经度应小于end的经度'
    assert start_lat > end_lat,'需要从左上到右下设置纬度，start的纬度应大于end的纬度'
    assert resolution>0,'resolution应大于0'


    grids_lib=[]
    longs = np.arange(start_long,end_long,resolution)
    if longs[-1] != end_long:
        longs = np.append(longs,end_long)

    lats = np.arange(start_lat,end_lat,-resolution)
    if lats[-1] != end_lat:
        lats = np.append(lats,end_lat)
    for i in range(len(longs)-1):
        for j in range(len(lats)-1):
            # grids_lib.append([round(float(longs[i]),6),round(float(lats[j]),6),round(float(longs[i+1]),6),round(float(lats[j+1]),6)])
            yield [round(float(longs[i]),6),round(float(lats[j]),6),round(float(longs[i+1]),6),round(float(lats[j+1]),6)]
    # return grids_lib

def bounding_box(json):
    polyline=json['polyline'].split(';')
    polyline_s=[]
    polyline_s1=[]
    polyline_s2=[]
    bounding=[]
    for i in range(len(polyline)):
        polyline_s.append(polyline[i].split(','))
    
    for j in range(len(polyline_s)):
        polyline_s1.append(float(polyline_s[j][0]))
        polyline_s2.append(float(polyline_s[j][1]))
    
    bounding=[max(polyline_s1),min(polyline_s1),max(polyline_s2),min(polyline_s2)]
    print(bounding)
    return bounding


def IsPtInPoly(aLon, aLat, pointList):  
    ''''' 
    :param aLon: double 经度 
    :param aLat: double 纬度 
    :param pointList: list [(lon, lat)...] 多边形点的顺序需根据顺时针或逆时针，不能乱 
    '''  
      
    iSum = 0  
    iCount = len(pointList)  
      
    if(iCount < 3):  
        return False  
      
      
    for i in range(iCount):  
          
        pLon1 = pointList[i][0]  
        pLat1 = pointList[i][1]  
          
        if(i == iCount - 1):  
              
            pLon2 = pointList[0][0]  
            pLat2 = pointList[0][1]  
        else:  
            pLon2 = pointList[i + 1][0]  
            pLat2 = pointList[i + 1][1]  
          
        if ((aLat >= pLat1) and (aLat < pLat2)) or ((aLat>=pLat2) and (aLat < pLat1)):  
              
            if (abs(pLat1 - pLat2) > 0):  
                  
                pLon = pLon1 - ((pLon1 - pLon2) * (pLat1 - aLat)) / (pLat1 - pLat2);  
                  
                if(pLon < aLon):  
                    iSum += 1  
  
    if(iSum % 2 != 0):  
        return True  
    else:  
        return False 


class AdslProxyServer():
    def __init__(self):
        self.adsl_server_url = ADSL_SERVER_URL
        self.auth = ADSL_SERVER_AUTH
        self.used_proxies = []
        self.get_proxy()

    def get_proxy(self):
        proxy = self._get_proxy()
        if not proxy in self.used_proxies:
            self.used_proxies.append(proxy)
        self.proxy = proxy
        return proxy

    def _get_proxy(self):
        proxy = requests.get(self.adsl_server_url,auth=self.auth).text
        return proxy

    def refresh_proxy(self):
        proxy = self._get_proxy()
        while proxy in self.used_proxies:
            # 代理地址已经使用过,等待1分钟
            time.sleep(60)
            proxy = self._get_proxy()
        self.proxy = proxy
        self.used_proxies.append(proxy)
        return proxy



def is_contained(shape,points):
    """
    判断点是否包含在边界内
    :param shape: np.array,n*2
    :param points: np.array,n*2
    :return:
    """

    assert isinstance(shape,np.ndarray) ,'输入应该是np.array格式，并且是N×2维'
    assert isinstance(points,np.ndarray) ,'输入应该是np.array格式，并且是N×2维'

    pth = Path(shape, closed=False) #边界上的判断有误
    return pth.contains_points(points,radius=-0.00001)


def generate_city_grids(city_polyline, resolution):
    """
    输入城市边界，根据栅格长度返回在城市边界内的栅格
    :param city_polyline:
    :param resolution:
    :return:
    """
    city_vertexes =np.array([float(i) for i in city_polyline.replace(';',',').split(',')]).reshape(-1,2)
    max_long = max(city_vertexes[:,0])
    min_long = min(city_vertexes[:,0])
    max_lat = max(city_vertexes[:,1])
    min_lat = min(city_vertexes[:,1])

    for grid in generate_grids(min_long,max_lat,max_long,min_lat,resolution):
        points = np.array(grid).reshape(-1,2)
        if any(is_contained(city_vertexes,points)):
            yield grid



# class AddWgsToDB(GaodeMapSceneDbOper):
#     """
#     往数据库里添加wgs坐标。
#     前提：需要数据里增加三列，wgc_long,wgc_lat,wgc_shape
#     """
#     def save_wgs_to_db(self):
#         NUM_TO_COMMIT = 100
#
#         query_str = """
#                 select * from {}
#                 """.format(self.TABLE_NAME)
#
#         update_str="""
#             update {} set wgc_long=%s,wgc_lat=%s,wgc_shape=%s
#             where id = %s and wgc_long is NULL;""".format(self.TABLE_NAME)
#
#         with self.conn.cursor(DictCursor) as query_cursor:
#             query_cursor.execute(query_str)
#             count = 0
#             for one in query_cursor:
#                 wgc_long,wgc_lat = gcj2wgs(float(one['longtitude']),
#                                            float(one['lat']))
#                 wgs_shape = []
#                 if one['shape'] == 'NULL':
#                     wgs_shape = 'NULL'
#                 else:
#                     vertexes = np.array([float(i) for i in one['shape'].replace('|',',').replace(';',',').split(',')]).reshape(-1,2)
#                     for lo,la in vertexes:
#                         _lo,_la = gcj2wgs(lo,la)
#                         wgs_shape.append(','.join([str(_lo),str(_la)]))
#
#                 wgs_shape = ','.join(wgs_shape)
#
#                 self.cursor.execute(update_str,(wgc_long,wgc_lat,wgs_shape,one['id']))
#                 count+=1
#                 if count < NUM_TO_COMMIT:
#                     continue
#                 else:
#                     print('提交数据库增加%s条数据的wgc信息'%count)
#                     self.conn.commit()
#                     count=0
#
#             self.conn.commit()




# 西安
# CITY_ADCODE = '310100'

if __name__ == '__main__':
    # scrope = [113.652670, 34.808881, 113.692670, 34.758881]
    # a = generate_grids(*scrope,0.01)
    # shape = np.array([[1,1],[1,3],[3,3],[3,1],[1,1]])
    # # points = np.array([[2,2],[2.9,2.9]])
    # points = np.array([[2,2],[3,3.1]])
    #
    # a = is_contained(shape,points)
    # print(CITY_POLYLINE)
    # # print([i for i in a])
    # a = generate_city_grids(CITY_POLYLINE,0.01)
    # count = 0
    # for i in a:
    #    print(count)
    #    count+=1
    #    print(i)

    # ad = AddWgsToDB()
    # ad.save_wgs_to_db()
    pass;
