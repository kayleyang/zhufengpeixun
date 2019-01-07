# -*- coding: utf-8 -*-
import scrapy
import json
import os

import requests

from crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class Course11Spider(scrapy.Spider):
    name = 'course_11'
    allowed_domains = ['zhufengpeixun.cn']
    start_urls = ['http://video.zhufengpeixun.cn/my/course/11']
    cookies_str = '__cfduid=dd1b301315eb0a91893dbd2d71955460a1545644805; REMEMBERME=Qml6XFVzZXJcQ3VycmVudFVzZXI6ZFhObGNsODRjVGsyYTI4MU1YQkFaV1IxYzI5b2J5NXVaWFE9OjE1NzcxODA4MjU6ZTRiMDg3NjY3ODZjNzUyMjEzMGI3MWMxNjY0MDBhMDgxNzJhOThkM2UzOGJlZTk5ZGNkZGVjMjBiYTVkNGIzMQ%3D%3D; PHPSESSID=rp2dee3ekmsssl9orke4vj3aoa; online-uuid=CE0DCC7B-3988-A600-B395-B8B28E6E6FDB; _pk_ses.633.0c05=*; Hm_lvt_5ca1e1efc366a109d783a085499d59d9=1545873726; Hm_lpvt_5ca1e1efc366a109d783a085499d59d9=1545873726; Hm_lvt_418b1c90fa35dc210dd5d2284d9f9f29=1545873733; Hm_lpvt_418b1c90fa35dc210dd5d2284d9f9f29=1545873733; _pk_id.633.0c05=fdaec6a4487f142c.1545644807.5.1545873765.1545873650.'  # 抓包获取
    cookies_dict: dict

    def start_requests(self):  # 重构start_requests方法
        # 这个cookies_str是抓包获取的
        # 将cookies_str转换为cookies_dict
        self.cookies_dict = {i.split('=')[0]: i.split('=')[1] for i in self.cookies_str.split('; ')}
        yield scrapy.Request(
            self.start_urls[0],
            callback=self.parse,
            cookies=self.cookies_dict
        )

    def parse(self, response):
        course_json = response.xpath('//div[@class="hidden js-hidden-cached-data"]/text()').extract_first()
        course = json.loads(course_json)
        # TODO make course dir
        for item in course:
            if item['itemType'] == 'unit':
                # TODO make unit dir
                print(item['title'])
            if item['itemType'] == 'task':
                item_url = 'http://video.zhufengpeixun.cn/course/11/task/' + item['taskId'] + '/activity_show'
                # TODO make task temp dir
                print('|_', item['title'], '<', item_url, '>')
                yield scrapy.Request(
                    item_url,
                    callback=self.parse_task,
                    cookies=self.cookies_dict
                )
        pass

    def parse_task(self, response):
        playlist_url = response.xpath('//div[@id="lesson-video-content"]/@data-url').extract_first()
        access_key = response.xpath('//div[@id="lesson-video-content"]/@data-access-key').extract_first()
        # print(playlist_url)
        yield scrapy.Request(
            playlist_url,
            callback=self.parse_play_list,
            cookies=self.cookies_dict
        )
        pass

    def parse_play_list(self, response):
        # Maybe need decrypt
        play_list = response.text
        if "#EXTM3U" not in play_list:
            raise BaseException("非M3U8的链接")

        if "EXT-X-STREAM-INF" in play_list:  # 第一层
            file_line = play_list.split("\n")
            stream_url = file_line[-1]
            if '.m3u8' in stream_url :
                yield scrapy.Request(
                    stream_url,
                    callback=self.parse_stream_list,
                    cookies=self.cookies_dict
                )
            else:
                print("stream_url 无效", stream_url)
        pass

    def parse_stream_list (self, response):
        stream_list = response.text
        print(stream_list)
        file_line = stream_list.split("\n")
        key = ""
        iv = ""
        for index, line in enumerate(stream_list):  # 第二层
            if "#EXT-X-KEY" in line:
                # 找解密Key
                if key == "":
                    method_pos = line.find("METHOD")
                    comma_pos = line.find(",")
                    method = line[method_pos:comma_pos].split('=')[1]
                    print("Decode Method：", method)

                    uri_pos = line.find("URI")
                    quotation_mark_pos = line.rfind('"')
                    # 拼出key解密密钥URL
                    key_url = line[uri_pos:quotation_mark_pos].split('"')[1]
                    res = requests.get(key_url)
                    key = res.content
                    print("key：", key)

                iv_pos = line.find("IV")
                iv = line[iv_pos + 5:]

            if "EXTINF" in line:  # 找ts地址并下载
                pd_url = file_line[index + 1]  # 拼出ts片段的URL
                print (pd_url)

                # res = requests.get(pd_url)
                # c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]
                #
                # if len(key):  # AES 解密
                #     cryptor = AES.new(a2b_hex(key), AES.MODE_CBC, iv)
                #     with open(os.path.join(download_path, c_fule_name + ".mp4"), 'ab') as f:
                #         f.write(cryptor.decrypt(res.content))
                # else:
                #     with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                #         f.write(res.content)
                #         f.flush()
        pass





