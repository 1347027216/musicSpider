# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import urllib
import re
from hashlib import sha1
from logging import getLogger
from music.items import WyMusicItem

logger = getLogger(__name__)
class WySpider(CrawlSpider):
    name = 'wy'
    allowed_domains = ['music.163.com','m10.music.126.net']
    start_urls = ['https://music.163.com/discover/playlist']

    rules = (
        # 匹配歌单详情
        Rule(LinkExtractor(restrict_xpaths=('//a[@class="tit f-thide s-fc0"]')),callback='parse_music_menu', follow=False),
        # 匹配歌单翻页
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="u-page"]/a[last()]')), follow=True),
    )
    # 外链url  https://music.163.com/song/media/outer/url?id=
    def parse_music_menu(self, response):
        item = WyMusicItem()
        item['musicMenuName'] = response.xpath('//title/text()').get()
        item['musicMenuAuthor'] = response.xpath('//span[@class="name"]/a/text()').get()
        item['musicMenuImg'] = response.xpath('//div[@class="cover u-cover u-cover-dj"]/img/@src').get()
        item['musicMenuTime'] = response.xpath('//span[@class="time s-fc4"]/text()').get()
        item['musicMenuList'] = []
        li_list = response.xpath('//div[@id="song-list-pre-cache"]/ul/li')
        for li in li_list:
            music = dict()
            music['music_name'] = li.xpath('./a/text()').get()
            music['music_href'] = 'https://music.163.com{}'.format(li.xpath('./a/@href').get())
            music['music_id'] = re.findall(r'.*?/song\?id=(\d+)',music['music_href'])[0]
            item['musicMenuList'].append(music)

            # 请求音频数据
            if music['music_id'] is not None:
                yield scrapy.Request(
                    url='https://music.163.com/song/media/outer/url?id={id}'.format(id=music['music_id']),
                    callback=self.parse_save_music,
                    meta={'name': music['music_name']}
                )
        yield item

    def parse_save_music(self, response):
        name = response.meta['name']
        file_path='{0}/{1}.{2}'.format('F:/WyMusic' ,name, 'mp3')
        with open(file_path,'wb') as f:
            f.write(response.body)
            logger.warning("{}保存成功！".format(name))
            f.close()

