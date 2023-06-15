# -*- coding: utf-8 -*-
import scrapy
import re
import json
from music.items import QqMusicItem
from copy import deepcopy
from logging import getLogger

logger = getLogger(__name__)


class QqSpider(scrapy.Spider):
    name = 'qq'
    allowed_domains = ['qq.com', 'douqq.com', 'aqqmusic.tc.qq.com']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'http://u.y.qq.com/cgi-bin/musicu.fcg?data={"comm":{"ct":24,"cv":0},"singerList":{"module":"Music.SingerListServer","method":"get_singer_list","param":{"area":-100,"sex":-100,"genre":-100,"index":-100,"sin":<sin>,"cur_page":<page>}}}'

    def start_requests(self):
        cookies = 'pgv_pvid=5307134032; pgv_pvi=893788160; pgv_si=s4089027584; RK=S0Y1hPJWX5; ptcz=afe33c791e94dc17648a77ddc62b06265c861af49eb4d6f64150777a53b4e58c; _qpsvr_localtk=0.5914475620477355; o_cookie=1600076368; ts_uid=8275886516; qqmusic_fromtag=66; ptui_loginuin=1600076368; ts_refer=www.baidu.com/link; player_exist=1; psrf_access_token_expiresAt=1591412908; yq_playschange=0; yq_playdata=; yq_index=0; yplayer_open=0; userAction=1; yqq_stat=0; ts_last=y.qq.com/n/yqq/singer/00067r4p0wBDDN.html'
        cookies = {i.split("=")[0]: i.split("=")[1] for i in cookies.split(";")}
        for i in range(299):
            url = re.sub(r'<sin>', str(i * 80), self.base_url)
            url = re.sub(r'<page>', str(i + 1), url)
            logger.info(url)
            yield scrapy.Request(
                url=url,
                callback=self.parse_singer_list,
                cookies=cookies
            )

    def parse_singer_list(self, response):
        response = json.loads(response.text)
        singerList = response['singerList']['data'].get('singerlist')
        item = QqMusicItem()
        for singer in singerList:
            item['singerId'] = singer.get('singer_id')
            item['singerMid'] = singer.get('singer_mid')
            item['singerName'] = singer.get('singer_name')
            item['singerImg'] = singer.get('singer_pic')
            url = 'https://y.qq.com/n/yqq/singer/{0}.html'.format(item['singerMid'])
            if url is not None:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_singe,
                    meta={'item': deepcopy(item)}
                )

    def parse_singe(self, response):
        item = response.meta.get('item')
        item['singerDisc'] = response.xpath('//div[@id="short_desc"]/text()').get()
        dq = response.xpath('//ul[@class="mod_data_statistic"]/li[1]//strong/text()').get()
        zj = response.xpath('//ul[@class="mod_data_statistic"]/li[2]//strong/text()').get()
        mv = response.xpath('//ul[@class="mod_data_statistic"]/li[3]//strong/text()').get()
        item['singerAchievement'] = '[单曲:{0}, 专辑:{1}, MV:{2}]'.format(dq, zj, mv)
        item['singerMusic'] = []
        li_music = response.xpath('//div[@id="index_tab"]/div[1]/div[2]/ul[2]/li')
        for li in li_music:
            music = dict()
            music['musicMid'] = li.xpath('./@mid').get()
            music['musicName'] = li.xpath('.//div[@class="songlist__songname"]/span/a/@title').get()
            music['musicHref'] = 'http:{0}'.format(li.xpath('.//div[@class="songlist__songname"]/span/a/@href').get())
            music['musicAlbum'] = li.xpath('.//div[@class="songlist__album"]/a/text()').get()
            item['singerMusic'].append(music)

            data = dict(mid=music.get('musicHref'))
            yield scrapy.FormRequest(
                url='http://www.douqq.com/qqmusic/qqapi.php',
                callback=self.parse_get_music,
                formdata=data,
                meta={'name': deepcopy(music['musicName'])}
            )
        yield item

    def parse_get_music(self, response):
        try:
            name = response.meta.get('name')
            res = json.loads(response.text)
            m4a_url = re.findall(r'.*?"m4a":"http:(.*?)","mp3.*?,', res)[0] if res is not None else None
            m4a_url = 'http:{0}'.format(re.sub(r'\\', '', m4a_url)) if m4a_url is not None else None
            if m4a_url is not None:
                yield scrapy.Request(
                    url=m4a_url,
                    callback=self.parse_save_music,
                    meta={'name': deepcopy(name)}
                )
        except Exception as e:
            pass

    def parse_save_music(self, response):
        name = response.meta.get('name')
        file_name = '{0}/{1}.{2}'.format('F:/QQMusic', name, 'mp3')
        with open(file_name, 'wb') as f:
            f.write(response.body)
            logger.warning('{} 保存为mp3格式成功！'.format(name))
            f.close()
