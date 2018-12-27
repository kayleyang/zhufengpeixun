# -*- coding: utf-8 -*-
import scrapy
import json


class Course11Spider(scrapy.Spider):
    name = 'course_11'
    allowed_domains = ['zhufengpeixun.cn']
    start_urls = ['http://video.zhufengpeixun.cn/my/course/11']

    def start_requests(self):  # 重构start_requests方法
        # 这个cookies_str是抓包获取的
        cookies_str = '__cfduid=dd1b301315eb0a91893dbd2d71955460a1545644805; REMEMBERME=Qml6XFVzZXJcQ3VycmVudFVzZXI6ZFhObGNsODRjVGsyYTI4MU1YQkFaV1IxYzI5b2J5NXVaWFE9OjE1NzcxODA4MjU6ZTRiMDg3NjY3ODZjNzUyMjEzMGI3MWMxNjY0MDBhMDgxNzJhOThkM2UzOGJlZTk5ZGNkZGVjMjBiYTVkNGIzMQ%3D%3D; PHPSESSID=rp2dee3ekmsssl9orke4vj3aoa; online-uuid=CE0DCC7B-3988-A600-B395-B8B28E6E6FDB; _pk_ses.633.0c05=*; Hm_lvt_5ca1e1efc366a109d783a085499d59d9=1545873726; Hm_lpvt_5ca1e1efc366a109d783a085499d59d9=1545873726; Hm_lvt_418b1c90fa35dc210dd5d2284d9f9f29=1545873733; Hm_lpvt_418b1c90fa35dc210dd5d2284d9f9f29=1545873733; _pk_id.633.0c05=fdaec6a4487f142c.1545644807.5.1545873765.1545873650.'  # 抓包获取
        # 将cookies_str转换为cookies_dict
        cookies_dict = {i.split('=')[0]: i.split('=')[1] for i in cookies_str.split('; ')}
        yield scrapy.Request(
            self.start_urls[0],
            callback=self.parse,
            cookies=cookies_dict
        )

    def parse(self, response):
        course_json = response.xpath('//div[@class="hidden js-hidden-cached-data"]/text()').extract_first()
        course = json.loads(course_json)
        for item in course:
            if item['itemType'] == 'unit':
                print(item['title'])
            if item['itemType'] == 'task':
                item_url = 'http://video.zhufengpeixun.cn/course/11/task/' + item['taskId'] + '/activity_show'
                print('|_', item['title'], '<', item_url, '>')
                yield scrapy.Request(
                    item_url,
                    callback=self.parse_task
                )

    def parse_task(self, response):
        m3u8_url = response.xpath('//div[@id="lesson-video-content"]/@data-url').extract()
        print(m3u8_url)




