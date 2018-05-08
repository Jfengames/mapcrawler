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
        pass


