#!/usr/bin/python3
#coding=utf-8

import scrapy


class GaodeCrawler(scrapy.Spider):
    name = 'GaoDe'

    def start_requests(self):
        """
        先爬取1km×1km的方格
        :return:
        """
        jinshui_adcode='410105' #金水区的adcode
        start_long_lat = '34.808881,113.652670'
        resolution = 0.01 # 直接加到经纬度上，大概1km

        pass


    def parse(self,response):
        """
        解析response，并保存需要的信息到items
        :param response:
        :return:
        """


