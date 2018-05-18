#!/usr/bin/python3
# coding =urt-8


"""
坐标系转换……
网格生成
"""
import numpy as np
import requests
import time

from MapCrawler.config import ADSL_SERVER_AUTH,ADSL_SERVER_URL


def gcj2wgs(long,lat):
    assert type(long)==float,'经度数据类型需要为浮点型 '
    assert type(lat)==float,'维度数据类型需要为浮点型 '
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

    return _long,_lat


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
            grids_lib.append([round(float(longs[i]),6),round(float(lats[j]),6),round(float(longs[i+1]),6),round(float(lats[j+1]),6)])
    return grids_lib


class AdslProxyServer():
    def __init__(self):
        self.adsl_server_url = ADSL_SERVER_URL
        self.auth = ADSL_SERVER_AUTH
        self.get_proxy()

    def get_proxy(self):
        proxy = requests.get(self.adsl_server_url,auth=self.auth).text
        self.proxy = proxy
        return proxy

    def refresh_proxy(self,old_proxy=None):
        old_proxy = old_proxy or self.proxy
        proxy = self.get_proxy()
        while proxy ==  old_proxy:
            # 代理地址没变,等待1分钟
            time.sleep(60)
            proxy = self.get_proxy()
        self.proxy = proxy
        return proxy





if __name__ == '__main__':
    scrope = [113.652670, 34.808881, 113.692670, 34.758881]
    a = generate_grids(*scrope,0.01)

    print(a)
