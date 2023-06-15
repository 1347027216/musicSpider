# -*- coding: utf-8 -*-

from scrapy.exceptions import DropItem
from logging import getLogger
from pymongo import MongoClient
import re

logger = getLogger(__name__)


class MusicPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'wy':
            item = self.__clean_date_wy(item)
            return item
        if spider.name == 'qq':
            item = self.__clean_date_qq(item)
            return item
        else:
            raise DropItem

    def __clean_date_wy(self, item):
        item['musicMenuTime'] = item['musicMenuTime'][:-3] if item['musicMenuTime'] is not None else None
        for music in item['musicMenuList']:
            music['music_name'] = music['music_name'].strip() if music['music_name'] is not None else None
        return item

    def __clean_date_qq(self, item):
        item['singerDisc'] = re.sub(r'\n|\s', '', str(item['singerDisc'])) if item['singerDisc'] is not None else None
        return item


class MongoPipeline(object):
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db
        self.db = None
        self.client = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_url)
        self.mongo_db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        # 存在则更新否则插入
        if spider.name == 'wy':
            name = item.__class__.__name__
            self.mongo_db[name].update_one({'musicMenuName': item.get('musicMenuName')}, {'$set': dict(item)}, upsert=True)
            logger.warning('wy: {}歌单信息保存到MongoDB成功！'.format(item.get('musicMenuName')))
        if spider.name == 'qq':
            name = item.__class__.__name__
            self.mongo_db[name].update_one({'singerId': item.get('singerId')}, {'$set': dict(item)}, upsert=True)
            logger.warning('qq: {}歌手信息保存到MongoDB成功！'.format(item.get('singerName')))
        else:
            raise DropItem

    def close_spider(self, spider):
        client = self.client
        client.close()
