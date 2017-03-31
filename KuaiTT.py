# -*- coding:utf-8 -*-
#
import base64
import urllib

import sys
from Crypto.Cipher import AES
from Crypto import Random
import random
import requests
import time
import json
import pytesseract
from PIL import Image, ImageDraw
from yima import YIMA
import re


class StrUtil(object):
    @staticmethod
    def convert_n_bytes(n, b):
        bits = b * 8
        return (n + 2 ** (bits - 1)) % 2 ** bits - 2 ** (bits - 1)

    @staticmethod
    def convert_4_bytes(n):
        return StrUtil.convert_n_bytes(n, 4)

    @staticmethod
    def convert_8_bytes(num):
        """
            extend the num by sign
        """
        len_cons = 16
        if num[0] == '-':
            pre = "f" * (len_cons - len(num) + 4)
            res = pre + num[3:-1]
        else:
            pre = "0" * (len_cons - len(num) + 3)
            res = pre + num[2:-1]
        return res

    @staticmethod
    def random_str(random_length=20):
        res = ""
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        length = len(chars) - 1

        for i in range(random_length):
            res += chars[random.randint(0, length)]
        return res

    @staticmethod
    def get_hash_code(s):
        """s -> hash code
                """
        h = 0
        n = len(s)
        for i, c in enumerate(s):
            h = h + ord(c) * 31 ** (n - 1 - i)
        return StrUtil.convert_4_bytes(h)


class KTT(object):
    """
        ktt class
    """

    def __init__(self, mobile):
        self.wx_aid = "wx794e012a7127454a"
        self.param = {}
        self.mobile = mobile
        self.device_code = ""
        self.encrypt = Encrypt()
        mobile.get_mobile_info()
        self.cookie = ""
        self.token = ""
        self.guest_info = {}
        self.user_info = {}
        self.channel_list = [
            {u'id': 1, u'name': u'\u63a8\u8350'}, {u'id': 3, u'name': u'\u5a31\u4e50'},
            {u'id': 5, u'name': u'\u641e\u7b11'}, {u'id': 6, u'name': u'\u7f8e\u5973'},
            {u'id': 7, u'name': u'\u60c5\u611f'}, {u'id': 8, u'name': u'\u4f53\u80b2'},
            {u'id': 9, u'name': u'\u8d22\u7ecf'}, {u'id': 10, u'name': u'\u6c7d\u8f66'},
            {u'id': 11, u'name': u'\u7f8e\u98df'}, {u'id': 12, u'name': u'\u79d1\u6280'},
            {u'id': 13, u'name': u'\u65f6\u5c1a'}, {u'id': 14, u'name': u'\u5065\u5eb7'},
            {u'id': 15, u'name': u'\u623f\u4ea7'}, {u'id': 16, u'name': u'\u661f\u5ea7'},
            {u'id': 17, u'name': u'\u80b2\u513f'}
        ]

    def gen_device_code(self):
        """
            generate device code
        """
        device_hash = StrUtil.get_hash_code(self.mobile.device_id)
        sim_hash = StrUtil.get_hash_code(StrUtil.random_str())
        android_hash = StrUtil.get_hash_code(self.mobile.android_id)

        hi64 = hex(android_hash)
        lo64 = hex((device_hash << 32) & 0xffffffff | sim_hash)
        # print("hi64: {}, lo64: {}".format(hi64, lo64))
        hi64 = StrUtil.convert_8_bytes(hi64)
        lo64 = StrUtil.convert_8_bytes(lo64)
        # print("hi64: {}, lo64: {}".format(hi64, lo64))
        # self.device_code = hi64 + lo64
        self.device_code = "ffffffff7b844f0d0000000070677c1d"

    @property
    def get_current_time(self):
        """
            get current time
        """
        return str(int(time.time()))

    def daily_task(self, token=""):
        """
            complete daily taskes
        :return: total_read
        """
        # 0. get cookie
        # self.gen_device_code()
        self.get_api_start()
        self.token = token
        self.cookie += token
        # 1. login
        # time.sleep(3)
        # self.post_login()
        # 2. get_user_info
        time.sleep(3)
        self.get_user_info()

        print(self.user_info)
        # 3. get_task_center
        print("task_status:")
        time.sleep(3)
        task_center_status = self.post_task_center_status()
        print("task_center_status")
        print(task_center_status)
        if task_center_status["new_task_status"] == 0:
            # complete newer task
            time.sleep(3)
            task_status = self.get_task_status()
            print(task_status["status"])
            if task_status["status"][0] == 0:
                time.sleep(3)
                new_task_result = self.post_task_commit_new()
                print("new_task_result:")
                print(new_task_result)
        # add master
        # if task_center_status["invite_task_status"] == 0:
        #    time.sleep(3)
        #    self.post_task_commit_invite("20833")
        # 4. sign task
        # print("task sign")
        time.sleep(3)
        is_sign = self.get_sign_status()
        if is_sign == 0:
            time.sleep(3)
            self.get_sign()
        # 5. packet task
        print("packet")
        time.sleep(3)
        count_down = self.get_timing_packet()
        # print("count_down: %d" % count_down)
        if count_down == 0:
            time.sleep(3)
            res_data = self.post_packet()
            print("get coin: %s" % res_data["money"])
        # 6. get list
        read_count = random.randint(5, 10)
        total_read = 0
        while total_read < read_count:
            time.sleep(3)
            # get article list
            art_list_info = self.get_list()
            while art_list_info["total"] == 0:
                time.sleep(3)
                art_list_info = self.get_list()
            art_list = art_list_info["list"]
            for article in art_list:
                art_id = article["id"]
                # 7. get content
                time.sleep(3)
                res_data = self.get_content(art_id)
                time.sleep(1)
                res_data = self.get_content_by_id(art_id)
                # 8. get reward
                rand_int = random.randint(0, 100)
                if rand_int % 2 == 0:
                    print("get reward")
                    time.sleep(3)
                    res_data = self.get_article_reward(art_id)
                    if res_data["c"] == 0:
                        total_read += 1
                        print("read an article")
                        if total_read >= read_count:
                            return total_read
                    else:
                        return total_read
        return total_read

    def get_api_start(self):
        """
            start get cookie
        """
        url = "http://api.applezhuan.com/api/c/start?&"
        params = {
            "android_id": self.mobile.android_id,
            "platform": "2",
            "av": "2",
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "lon": self.mobile.lon,
            "lat": self.mobile.lat,
            "device_name": "dpi",
            "device_code": self.device_code,
            "brand": self.mobile.brand,
            "mac": self.mobile.mac,
            "vn": "1.0.2",
            "network": self.mobile.network
        }
        params_str = self.encrypt.get_secret_param(params)
        url = url + "s=" + params_str
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": "token="
        }

        res = requests.get(url, headers=headers)
        # print(res.headers)
        self.cookie = res.headers["Set-Cookie"]
        index_semicolon = self.cookie.index(";")
        # print("cookie: {}".format(self.cookie[:index_semicolon]+"; token="))
        self.cookie = self.cookie[:index_semicolon] + "; token="
        # print(res.text)

    def get_api_default_channel_list(self):
        """ get default channel list
        :return: channel list """
        url = "http://api.applezhuan.com/api/c/get_default_channellist?&"
        params = {
            "android_id": self.mobile.android_id,
            "platform": "2",
            "av": "2",
            "type": "1",
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "lon": self.mobile.lon,
            "lat": self.mobile.lat,
            "device_name": "dpi",
            "device_code": self.device_code,
            "brand": self.mobile.brand,
            "mac": self.mobile.mac,
            "vn": "1.0.2",
            "network": self.mobile.network
        }
        params_str = self.encrypt.get_secret_param(params)
        url = url + "s=" + params_str
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        res = requests.get(url, headers=headers)
        # print(res.text)
        result = json.loads(res.text)
        return result["d"]

    def post_login(self):
        """
            login 
            set self.token
            set self.cookie
        :return: 
        """

        url = "http://api.applezhuan.com/api/c/login"
        params = {
            "password": "123456",
            "android_id": self.mobile.android_id,
            "platform": "2",
            "av": "2",
            "cne": "0",
            "father": "0",
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "lon": self.mobile.lon,
            "lat": self.mobile.lat,
            "device_name": "dpi",
            "device_code": self.device_code,
            "brand": self.mobile.brand,
            "mac": self.mobile.mac,
            "vn": "1.0.2",
            "wx_code": "1.0.2",
            "network": self.mobile.network,
            "mobile": self.mobile.mobile,
            "wx_aid": self.wx_aid
        }

        params_str = self.encrypt.get_secret_param(params)
        post_data = {
            "s": params_str
        }
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }
        res = requests.post(url, headers=headers, data=post_data)
        print("device_code: %s" % self.device_code)
        # print(res.text)
        result = json.loads(res.text)
        self.token = result["d"]["token"]
        self.cookie = self.cookie + self.token

    def get_sign_status(self):
        """
        get sign status
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/user_sign"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/task_center.html",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        res = requests.get(url, headers=headers)
        result = json.loads(res.text)
        return result["d"]["is_sign"]

    def get_sign(self):
        """
            sign
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/user_sign_commit"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/task_center.html",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        res = requests.get(url, headers=headers)
        result = json.loads(res.text)
        print("get coin: %s" % result["d"]["coin"])
        # return result["d"]["coin"]

    def get_timing_packet(self):
        """
            get time packet
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/timing_packet"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/task_center.html",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        res = requests.get(url, headers=headers)
        result = json.loads(res.text)
        # print("count down: %s" % result["d"]["count_down"])
        return result["d"]["count_down"]

    def post_packet(self):
        """
            packet
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/packet"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/task_center.html",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        post_data = {
            "type": "3"
        }
        res = requests.post(url, headers=headers, data=post_data)
        result = json.loads(res.text)
        return result["d"]

        # return result["d"]["coin"]

    def get_guest_info(self):
        """ Get guest info
        Set self.guest_info
        :return: 
        """
        url = "http://api.applezhuan.com/api/c/get_guestinfo?&"
        params = {
            "android_id": self.mobile.android_id,
            "platform": "2",
            "av": "2",
            "token": "",
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "lon": self.mobile.lon,
            "lat": self.mobile.lat,
            "device_name": "dpi",
            "device_code": self.device_code,
            "brand": self.mobile.brand,
            "mac": self.mobile.mac,
            "vn": "1.0.2",
            "network": self.mobile.network
        }
        params_str = self.encrypt.get_secret_param(params)
        url = url + "s=" + params_str
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        res = requests.get(url, headers=headers)
        # print(res.text)
        result = json.loads(res.text)
        print(result)
        self.guest_info = result["d"]
        self.guest_info.pop("h5_url")
        self.guest_info.pop("banner")
        self.guest_info.pop("menu")
        self.guest_info.pop("headimg")

    def get_img_captcha(self):
        """Get captcha image
            
        :return: code or None
        """
        url = "http://api.applezhuan.com/api/c/get_img_captcha?&"
        params = {
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "device_code": self.device_code
        }
        params_str = self.encrypt.get_secret_param(params)
        url = url + "s=" + params_str
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        res = requests.get(url, headers=headers)
        # print(res.text)
        result = json.loads(res.text)
        # print(result["d"])
        img_str = result["d"]["data"]
        img_ts = result["d"]["ts"]
        index_comma = img_str.index(",")
        img_str = img_str[index_comma + 1:]
        # img_str = base64.decodestring(img_str.encode())
        # print(img_str)
        path = "tmp.png"
        decode_png = base64.decodestring(img_str.encode())
        with open(path, "wb") as f:
            f.write(decode_png)

        image = Image.open("tmp.png")
        draw = ImageDraw.Draw(image)
        white_color = (255, 255, 255)
        for x in range(0, image.size[0]):
            for y in range(0, image.size[1]):
                color = image.getpixel((x, y))
                if color[2] == 0:
                    draw.point((x, y), white_color)
        code = pytesseract.image_to_string(image, lang="ktt")
        code = code.replace("|", "l")
        # image.save("tifs/%s_code.tif" % code)
        if len(code) == 4:
            return img_ts, code
        else:
            return img_ts, None

    def get_sms_captcha(self, img_ts, img_captcha):
        """
            accept the img captcha and request send sms captcha
        :return: 
        """
        url = "http://api.applezhuan.com/api/get_sms_captcha?&"
        params = {
            "img_captcha": img_captcha,
            "time": self.get_current_time,
            "ts": img_ts,
            "device_code": self.device_code,
            "mobile": self.mobile.mobile
        }
        params_str = self.encrypt.get_secret_param(params)
        url = url + "s=" + params_str
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        res = requests.get(url, headers=headers)
        # print(res.text)
        result = json.loads(res.text)
        return result

    def post_register(self, sms_captcha):
        """
            register a user
        :return: 
        """
        url = "http://api.applezhuan.com/api/c/register"
        params = {
            "android_id": self.mobile.android_id,
            "platform": "2",
            "password": "123456",
            "av": "2",
            "cne": "0",
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "lon": self.mobile.lon,
            "lat": self.mobile.lat,
            "device_name": "dpi",
            "device_code": self.device_code,
            "brand": self.mobile.brand,
            "mac": self.mobile.mac,
            "vn": "1.0.2",
            "father": "0",
            "mobile": self.mobile.mobile,
            "captcha": sms_captcha,
            "network": self.mobile.network
        }
        params_str = self.encrypt.get_secret_param(params)
        post_data = {
            "s": params_str
        }

        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        res = requests.post(url, headers=headers, data=post_data)
        print(res.text)
        result = json.loads(res.text)
        uid = result["d"]["uid"]
        self.token = result["d"]["token"]
        self.cookie += self.token

    def post_update_user_info(self):
        """
        update user info
        :return: 
        """
        url = "http://api.applezhuan.com/api/c/update_user_info"
        sexes = ["0", "1"]
        sex = sexes[random.randint(0, 1)]
        name = StrUtil.random_str(3)
        year = random.randint(1980, 2003)
        months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
        day = random.randint(10, 28)
        birth = "%s-%s-%s" % (year, months[random.randint(0, 11)], day)
        jobs = ["学生", "教师", "上班族", "公务员", "自由工作者", "其他"]
        job = jobs[random.randint(0, len(jobs)-1)]
        params = {
            "sex": sex,
            "name": name,
            "birth": birth,
            "job": job
        }
        params_str = self.encrypt.get_secret_param(params)
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        post_data = {
            "s": params_str
        }
        res = requests.post(url, headers=headers, data=post_data)
        print(res.text)
        result = json.loads(res.text)

    def get_user_info(self):
        """ Get user info
        Set self.user_info
        :return: 
        """
        url = "http://api.applezhuan.com/api/c/get_userinfo?&"
        params = {
            "android_id": self.mobile.android_id,
            "platform": "2",
            "av": "2",
            "token": self.token,
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "lon": self.mobile.lon,
            "lat": self.mobile.lat,
            "device_name": "dpi",
            "device_code": self.device_code,
            "brand": self.mobile.brand,
            "mac": self.mobile.mac,
            "vn": "1.0.2",
            "network": self.mobile.network
        }
        params_str = self.encrypt.get_secret_param(params)
        url = url + "s=" + params_str
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        res = requests.get(url, headers=headers)
        # print(res.text)
        result = json.loads(res.text)

        self.user_info = result["d"]
        self.user_info.pop("h5_url")
        self.user_info.pop("banner")
        self.user_info.pop("menu")
        self.user_info.pop("headimg")
        self.user_info.pop("token")
        # print(self.user_info)

    def post_task_commit_invite(self, father):
        """
        input the invite code
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/task_commit_invite"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/task_invite_num.html",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        post_data = {
            "father": father
        }
        res = requests.post(url, headers=headers, data=post_data)
        result = json.loads(res.text)
        print("get money: %s" % result["d"]["money"])
        return result

    def get_task_status(self):
        """
            get task status
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/task_status?id=33"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/task_new.html",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        res = requests.get(url, headers=headers)
        result = json.loads(res.text)
        return result["d"]
        # print("get money: %s" % result["d"]["money"])

    def post_task_commit_new(self):
        """
            newer task
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/task_commit"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/task_invite_num.html",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"

        }

        post_data = {
            "id": 33
        }
        res = requests.post(url, headers=headers, data=post_data)
        result = json.loads(res.text)
        # print("post new task result: ")
        # print(result)
        return result["d"]

    def post_task_center_status(self):
        """
            center task status
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/task_center_status"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/task_center.html",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        res = requests.post(url, headers=headers)
        result = json.loads(res.text)
        # print("post new task result:")
        # print(result)
        return result["d"]

    def get_list(self):
        """
         get content list
        :return: 
        """
        url = "http://api.applezhuan.com/api/c/getlist?&"
        cid = random.randint(0, len(self.channel_list) - 1)
        print("channel: %s" % self.channel_list[cid])
        params = {
            "android_id": self.mobile.android_id,
            "platform": "2",
            "av": "2",
            "cid": cid,
            "page": "1",
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "lon": self.mobile.lon,
            "lat": self.mobile.lat,
            "device_name": "dpi",
            "device_code": self.device_code,
            "brand": self.mobile.brand,
            "mac": self.mobile.mac,
            "vn": "1.0.2",
            "content_type": "1, 3, 4, 5",
            "network": self.mobile.network
        }
        params_str = self.encrypt.get_secret_param(params)
        url = url + "s=" + params_str
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        res = requests.get(url, headers=headers)
        result = json.loads(res.text)
        return result["d"]

    def get_content(self, content_id):
        """
            get content by id
        :return: 
        """
        url = "http://api.applezhuan.com/api/c/get_content?&"
        params = {
            "android_id": self.mobile.android_id,
            "platform": "2",
            "av": "2",
            "content_id": content_id,
            "time": self.get_current_time,
            "ov": self.mobile.os,
            "device_name": "dpi",
            "device_code": self.device_code,
            "brand": self.mobile.brand,
            "mac": self.mobile.mac,
            "vn": "1.0.2",
            "network": self.mobile.network
        }
        params_str = self.encrypt.get_secret_param(params)
        url = url + "s=" + params_str
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Host": "api.applezhuan.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie
        }

        res = requests.get(url, headers=headers)
        result = json.loads(res.text)
        # print("get content id= %s" % content_id)
        # print(result)
        return result["d"]

    def get_content_by_id(self, content_id):
        """
            get content info by id
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/get_content?content_id=%s" % content_id
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/article_detail.html?content_id=%s" % content_id,
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        res = requests.get(url, headers=headers)
        result = json.loads(res.text)
        # print("get content id")
        # print(result)
        return result["d"]

    def get_article_reward(self, content_id):
        """
            get article reward
        :return: 
        """
        url = "http://api.applezhuan.com/api/m/article_get_reward"
        headers = {
            "Host": "api.applezhuan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Origin": "http://m.applezhuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://m.applezhuan.com/article_detail.html?content_id=%s" % content_id,
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android " + self.mobile.os + "; zh-cn; GT-N7100 Build/" + self.mobile.brand + ") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Cookie": self.cookie,
            "X-Requested-With": "com.shuishi.kuai"
        }

        post_data = {
            "content_id": content_id
        }
        res = requests.post(url, headers=headers, data=post_data)
        result = json.loads(res.text)
        # print("get article reward:")
        # print(result)
        # return result["d"]
        return result


def pad(s):
    """Padding s to 16bits."""
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)


def un_pad(s):
    """Delete padding from s to original s"""
    return s[0:-ord(s[-1])]


class Mobile(object):
    """
        mobile info :
            device_code (128bits)0x0000000035d7eb3f000000007f86fefe
            lat  40.41276437615495
            lon 116.67200895325377
            mac
            net_work
            android_id [HUAWEIFRD-AL00, KOT49H]
            brand [honor, samsung]
    """

    brands = ["honor", "samsung", "xiaomi"]
    android_ids = {
        "honor": ["HUAWEIFRD-AL00", "HUAWEIFRD-DL00", "HONORKIW-TL00H", "HONORKIW-UL00", "HONORKIW-AL10",
                  "HONORKIW-AL20"],
        "samsung": ["KOT49H", "G9300", "C5000"],
        "xiaomi": ["MI4LTE-CT", "MI4LTE-CT", "MI3", "MI5"]
    }
    TACs = {
        "honor": ['867922', '862915'],
        "samsung": ['355065', '354066'],
        "xiaomi": ['353068', '358046']
    }
    FACs = ['00', '01', '02', '03', '04', '05']

    os_versions = ["4.4.2", "4.4.5", "5.0.1", "5.1.1", "6.0", "7.0"]

    def __init__(self, mobile="18844196047"):
        self.mobile = mobile
        self.lon = 116
        self.lat = 40
        self.brand = ""
        self.android_id = ""
        self.network = "WIFI"
        self.os = ""
        self.device_id = ""
        self.mac = ""

    def select_brand(self):
        """
            select a brand
        """
        brand_num = len(self.brands)
        self.brand = self.brands[random.randint(0, brand_num - 1)]
        aids = self.android_ids[self.brand]
        aid_num = len(self.android_ids)
        self.android_id = aids[random.randint(0, aid_num - 1)]

    def select_os(self):
        """
            select os version
        """
        os_num = len(self.os_versions)
        self.os = self.os_versions[random.randint(0, os_num - 1)]

    def gen_device_id(self):
        """
            generate device id 
        """
        ts = self.TACs[self.brand]
        tac_len = len(ts)
        tac = ts[random.randint(0, tac_len - 1)]
        fac_len = len(self.FACs)
        fac = self.FACs[random.randint(0, fac_len - 1)]
        snr = random.randint(10000, 599999)
        num = tac + fac + str(snr)
        digits = [int(x) for x in reversed(str(num))]
        check_sum = sum(digits[1::2]) + sum((dig // 10 + dig % 10) for dig in [2 * el for el in digits[::2]])
        check_bit = (10 - check_sum % 10) % 10
        self.device_id = num + str(check_bit)

    def gen_lat_lon(self):
        """
            generate lat and lon
        """
        delta = round(random.random() * random.randint(1, 4), 4)
        sign = random.randint(1, 100)
        if sign % 2 == 0:
            self.lat += delta
        else:
            self.lat -= delta

        delta = round(random.random() * random.randint(1, 4), 4)
        sign = random.randint(1, 100)
        if sign % 2 == 0:
            self.lon += delta
        else:
            self.lon -= delta

    def gen_mac(self):
        """
            gen mac address
        """
        add_list = []
        for i in range(1, 7):
            rand_str = "".join(random.sample("0123456789ABCDEF", 2))
            add_list.append(rand_str)
        self.mac = ":".join(add_list)

    def get_mobile_info(self):
        """
            get a mobile info
        """
        # 1. select brand
        self.select_brand()
        # 2. select os
        self.select_os()
        # 3. device_id
        self.gen_device_id()
        # 4. lat lon
        self.gen_lat_lon()
        # 5. mac
        self.gen_mac()

    def show(self):
        print("Mobile:")
        print("\tdevice_id: {}".format(self.device_id))
        print("\tlat: {}".format(self.lat))
        print("\tlon: {}".format(self.lon))
        print("\tmac: {}".format(self.mac))
        print("\tos_version: {}".format(self.os))
        print("\tnetwork: {}".format(self.network))


class Encrypt(object):
    """
        Encrypt
    """
    char_table = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
                  90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116,
                  117, 118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 43, 47, 61]

    def __init__(self, key="w1215e436fb3c730", iv=""):
        self.key = key
        # self.iv = Random.get_random_bytes(16)
        self.iv = iv

    def dic_to_str(self, params):
        """
            params -> string
            args:
                params dict
            return:
                params_str str
        """
        params_str = urllib.urlencode(params)
        # print("p_str: {}".format(params_str))
        return params_str

    def aes_encrypt(self, params_str):
        """
            params_str -> aes_str
            args:
                params_str str
            return:
                aes_str
        """
        params_str = pad(params_str)
        self.iv = Random.get_random_bytes(16)
        # self.iv = str(bytearray([256-97, 66, 256-89, 91, 256-83, 79, 93, 70, 30, 256-69, 256-25, 256-57, 256-21, 40, 256-33, 256-9]))
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        cipher_str = cipher.encrypt(params_str)
        return self.iv + cipher_str

    def bit_encrypt(self, aes_str):
        """
            aes_str -> bit_str
            args:
                aes_str str
            return:
                bit_str
        """
        aes_str_bytes = bytearray(aes_str)
        len_bytes = len(aes_str_bytes)
        block_num, left_num = divmod(len_bytes, 3)
        aes_bytes = []
        for i in range(block_num):
            bb4_arr = self.three_to_four(
                aes_str_bytes[i * 3],
                aes_str_bytes[i * 3 + 1],
                aes_str_bytes[i * 3 + 2]
            )
            aes_bytes.extend(bb4_arr)

        if left_num == 0:
            bit_str = str(bytearray(aes_bytes).decode("ISO-8859-1"))
        else:
            if left_num == 1:
                b0 = aes_str_bytes[-1]
                bb0 = b0 >> 2 & 0x3f
                bb1 = b0 << 4 & 0x30
                bb2 = -1
                bb3 = -1
            else:
                b0 = aes_str_bytes[-2]
                b1 = aes_str_bytes[-1]
                bb0 = b0 >> 2 & 0x3f
                bb1 = (b0 << 4 & 0x30) + (b1 >> 4 & 0xf)
                bb2 = b1 << 2 & 0x3c
                bb3 = -1
            aes_bytes.extend(
                [self.char_table[bb0], self.char_table[bb1],
                 self.char_table[bb2], self.char_table[bb3]]
            )
            bit_str = str(bytearray(aes_bytes).decode("ISO-8859-1"))
        return bit_str

    def three_to_four(self, b0, b1, b2):
        # type: (int, int, int) -> list
        """
            3bytes --> 4bytes
        """
        bb0 = b0 >> 2 & 0x3f
        bb1 = (b0 << 4 & 0x30) + (b1 >> 4 & 0xf)
        bb2 = (b1 << 2 & 0x3c) + (b2 >> 6 & 0x3)
        bb3 = b2 & 0x3f
        return [
            self.char_table[bb0],
            self.char_table[bb1],
            self.char_table[bb2],
            self.char_table[bb3]
        ]

    def get_secret_param(self, params_dict):
        """
            encrypt the params
            args:
                params dict
            return:
                secret_str str
        """
        # 1. dic to str
        param_str = self.dic_to_str(params_dict)
        # print("len: {}, dic to str: {}".format(len(param_str), param_str))
        # param_str = urllib.quote(param_str)
        # 2. aes
        aes_str = self.aes_encrypt(param_str)
        # print("len: {}, aes str: {}".format(len(aes_str), aes_str))
        # 3. bit_encryptS
        bit_str = self.bit_encrypt(aes_str)
        # print("len: {}, bit str: {}".format(len(bit_str), bit_str))
        return bit_str


class Decrypt(object):
    """
        decrypt
    """
    char_table = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
                  90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116,
                  117, 118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 43, 47, 61]

    def __init__(self, key="w1215e436fb3c730", iv="123"):
        self.key = key
        self.iv = iv

    def url_decrypt(self, param_str):
        """
            url -> param
        """
        return urllib.unquote(param_str)

    def bit_decrypt(self, url_str):
        """
            url_str --> secret_str
        """
        url_bytes = bytearray(url_str, "ISO-8859-1")
        url_len = len(url_bytes)
        block_num = int(url_len / 4)
        secret_bytes = []
        for i in range(block_num):
            b3_arr = self.four_to_three(
                url_bytes[i * 4], url_bytes[i * 4 + 1],
                url_bytes[i * 4 + 2], url_bytes[i * 4 + 3]
            )
            secret_bytes.extend(b3_arr)

        return str(bytearray(secret_bytes))

    def four_to_three(self, bb0, bb1, bb2, bb3):
        """
            4bytes -> 3bytes
        """
        bb0 = self.char_table.index(bb0)
        bb1 = self.char_table.index(bb1)
        bb2 = self.char_table.index(bb2)
        bb3 = self.char_table.index(bb3)
        table_len = len(self.char_table) - 1
        if bb3 == table_len:
            if bb2 == table_len:
                b0 = (bb0 << 2 & 0xfc) | (bb1 >> 4 & 0x3)
                return [b0]
            else:
                b0 = (bb0 << 2 & 0xfc) | (bb1 >> 4 & 0x3)
                b1 = (bb1 << 4 & 0xf0) | (bb2 >> 2 & 0xf)
                return [b0, b1]
        else:
            b0 = (bb0 << 2 & 0xfc) | (bb1 >> 4 & 0x3)
            b1 = (bb1 << 4 & 0xf0) | (bb2 >> 2 & 0xf)
            b2 = (bb2 << 6 & 0xc0) | (bb3 & 0x3f)
            return [b0, b1, b2]

    def aes_decrypt(self, secret_str):
        """
            secret_str -> params_str
        """
        self.iv = secret_str[0:16]
        # print("iv: {}".format(self.iv.encode("")))
        secret_data = secret_str[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        params_str = cipher.decrypt(secret_data)
        return params_str

    def get_param_str(self, url):
        # 1. get the s=url_str
        if url.find("?&") != -1:
            print("url: {}".format(url.split("?&")[0]))
            cipher_str = url.split("?&")[1][2:]
        else:
            cipher_str = url
        # print("len:{}, cipher str: {}".format(len(cipher_str),cipher_str))
        # 2. decode
        url_str = self.url_decrypt(cipher_str)
        # print("len:{}, decode str: {}".format(len(url_str), url_str))
        # 3. bit_decrypt
        secret_str = self.bit_decrypt(url_str)
        # print("len:{}, secret str: {}".format(len(secret_str), secret_str))
        # 4. aes_decrypt
        params_str = self.aes_decrypt(secret_str)
        # print("index:{}".format(-ord(params_str[-1])))
        # print("len:{}, params str: {}".format(len(params_str),params_str))
        params_str = un_pad(params_str)
        # print("len:{}, params str: {}".format(len(params_str), params_str))
        return urllib.unquote(params_str)


def register_user():
    reg = "(^1(33|53|77|8[019])[0-9]{8}$)|(^1700[0-9]{7}$)"
    reg1 = "(^1(3[0-2]|4[5]|5[56]|7[6]|8[56])[0-9]{8}$)|(^1709[0-9]{7}$)"
    reg2 = "(^1(3[4-9]|4[7]|5[0-27-9]|7[8]|8[2-478])[0-9]{8}$)|(^1705[0-9]{7}$)"
    yi_ma = YIMA("6381")
    yi_ma.login_yi_ma()
    # 1. get mobile
    time.sleep(3)
    mobile_num = yi_ma.get_mobile()
    mobile = Mobile(mobile_num)
    print("mobile: %s" % mobile_num)
    if mobile_num and \
            (re.match(reg, mobile_num) or re.match(reg1, mobile_num) or re.match(reg2, mobile_num)):
        ktt = KTT(mobile)
        ktt.gen_device_code()
        ktt.get_api_start()
        print("cookie: {}".format(ktt.cookie))

        # get sms captcha
        status = "-1113"
        while status == "-1113":
            img_captcha = None
            while img_captcha is None:
                img_ts, img_captcha = ktt.get_img_captcha()
                print("img_ts: %s, img_captcha: %s" % (img_ts, img_captcha))
                time.sleep(3)
            result = ktt.get_sms_captcha(img_ts, img_captcha)
            status = str(result["c"])
            print("status: %s" % status)
            if status == "-1113":
                time.sleep(60)

        if status == "-2043":
            print("exit mobile exists")
            sys.exit(0)
        if status == "0":
            time.sleep(10)
            sms_captcha = yi_ma.get_code()
            print("sms_captcha: %s" % sms_captcha)
            time.sleep(3)
            ktt.post_register(sms_captcha)
            time.sleep(3)
            ktt.get_user_info()
            # update user info
            time.sleep(3)
            ktt.post_update_user_info()
            time.sleep(3)
            ktt.get_user_info()
            # add master
            ktt.post_task_commit_invite("20833")
            # todo add a user to user_info
            # device_code, token, mac, mobile, os,
            # brand, coin, father, is_notice, coin_income, income
            # uid, balance, name

    yi_ma.release_all()

if "__main__" == __name__:
    print("Hello Main!")
    register_user()
    # check_encrypt()
    # test_decrypt_one()
    # test_mobile()
    # test_device_code()
    # test_start()
    # test_urllib()
