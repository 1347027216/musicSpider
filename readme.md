# 网易云和QQ音乐歌单爬虫

- **启动网易爬虫**

~~~bash
python start_wy.py
~~~

- **启动QQ爬虫**

~~~bash
python start_qq.py
~~~

- **配置mongo数据库**
~~~python 
# music/settings.py

MONGO_URL = '127.0.0.1'
MONGO_DB = 'music'

~~~

- **配置UA**
~~~python
DEFAULT_REQUEST_HEADERS = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-language': 'zh-CN,zh;q=0.9,und;q=0.8',
}
~~~
