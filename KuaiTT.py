#-*- coding:utf-8 -*-

import urllib
from Crypto.Cipher import AES
from Crypto import Random
import random
import time
import requests

class StrUtil(object):
	'''
		Str Util
	'''
	@staticmethod
	def convert_n_bytes(n, b):
		bits = b*8
		return (n + 2**(bits-1)) % 2**bits - 2**(bits-1)
	
	@staticmethod
	def convert_4_bytes(n):
		return StrUtil.convert_n_bytes(n, 4)
		
	@staticmethod
	def get_hash_code(s):
		'''
			s -> hash code
		'''
		h = 0
		n = len(s)
		for i, c in enumerate(s):
			h = h + ord(c)*31**(n-1-i)
		return StrUtil.convert_4_bytes(h)
		
	@staticmethod
	def convert_8_bytes(num):
		'''
			extend the num by sign
		'''
		LEN = 16
		if num[0] == '-':
			pre = "f"*(LEN-len(num)+4)
			res = pre+num[3:-1]
		else:
			pre = "0"*(LEN-len(num)+3)
			res = pre+num[2:-1]
		return res
		
	@staticmethod
	def random_str(randomlength=20):
		res = ""
		chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
		length = len(chars) - 1
		
		for i in range(randomlength):
			res+=chars[random.randint(0, length)]
		return res

class KTT(object):
	'''
		ktt class
	'''
	def __init__(self, mobile):
		self.wxaid = "wx794e012a7127454a"
		self.param = {}
		self.mobile = mobile
		self.encrypt = Encrypt()
		mobile.get_mobile_info()
	
	def gen_device_code(self):
		'''
			generate device code
		'''
		device_hash = StrUtil.get_hash_code(self.mobile.imei)
		sim_hash = StrUtil.get_hash_code(StrUtil.random_str())
		android_hash = StrUtil.get_hash_code(self.mobile.android_id)
		
		hi64 = hex(android_hash)
		lo64 = hex((device_hash<<32) & 0xffffffff | sim_hash)
		#print("hi64: {}, lo64: {}".format(hi64, lo64))
		hi64 = StrUtil.convert_8_bytes(hi64)
		lo64 = StrUtil.convert_8_bytes(lo64)
		#print("hi64: {}, lo64: {}".format(hi64, lo64))
		self.device_code = hi64+lo64
	
	def get_current_time(self):
		'''
			get current time
		'''
		return str(int(time.time()))
		
	def get_api_start(self):
		'''
			start get cookie
		'''
		url = "http://api.applezhuan.com/api/c/start?&"
		params = {
			"android_id":self.mobile.android_id,
			"platform":"2",
			"av":"2",
			"time": self.get_current_time(),
			"ov":self.mobile.os,
			"lon":self.mobile.lon,
			"lat":self.mobile.lat,
			"device_name":"dpi",
			"device_code":self.device_code,
			"brand":self.mobile.brand,
			"mac":self.mobile.mac,
			"vn":"1.0.2",
			"network":self.mobile.network
		}
		params_str = self.encrypt.get_secret_param(params)
		url = url + "s=" + params_str
		headers = {
			"Accept-Language": "zh-CN,zh;q=0.8",
			"User-Agent": "Mozilla/5.0 (Linux; U; Android "+self.mobile.os+"; zh-cn; GT-N7100 Build/"+self.mobile.brand+") AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
			"Host": "api.applezhuan.com",
			"Connection": "Keep-Alive",
			"Accept-Encoding": "gzip",
			"Cookie": "token="
		}
		
		
		#url = "s=n0KnW61PXUYeu%2BfH6yjf9wq30TMtcfkhCLN70CU1W%2B7r1RB87l8BLJUUNHLYw4me%2B7nQscGSDibpYoP9UXBYnKmiSYRM4C3trbde5F55yzGzIQ2AMv0L1L4EOxGac4FhzAlzdqwEj%2FCNVTWa%2BVeFrno6BpreWrMV7RLUOMa05qB4wXx3AixB%2FTHODUsv5sZ%2FUYYDDSk9CZLBLK%2Bw%2FZa5NaCsTbNnPQLEiNEVMuZ9ANp35iXtQcr6izykfwQsQ3CT%2FnItaKJGIWI3PXNxk3J0zcBUPFXJ6i5jnfb8gWLjBeEGUv90T9rZWIfojcMEfBr7"
		res = requests.get(url, headers=headers)
		print(res.headers)
		print(res.text)
		
		
		
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)#s -> len(s)%BS==0
unpad = lambda s : s[0:-ord(s[-1])]		


class Mobile(object):
	'''
		mobile info :
			device_code (128bits)0x0000000035d7eb3f000000007f86fefe
			lat  40.41276437615495
			lon 116.67200895325377
			mac
			net_work
			android_id [HUAWEIFRD-AL00, KOT49H]
			brand [honor, samsung]
	'''
	
	brands=["honor", "samsung", "xiaomi"]
	android_ids={
		"honor":["HUAWEIFRD-AL00", "HUAWEIFRD-DL00", "HUAWEIKEW-TL00H", "HUAWEIKIW-UL00", "HUAWEIKIW-AL10", "HUAWEIKIW-AL20"],
		"samsung":["KOT49H", "G9300", "C5000"],
		"xiaomi":["MI4LTE-CT", "MI4LTE-CT","MI3", "MI5"]
	}
	TACs={
		"honor":['867922', '862915'],
		"samsung":['355065', '354066'],
		"xiaomi":['353068', '358046']
	}
	FACs=['00', '01', '02', '03', '04', '05']
	
	os_versions = ["4.4.2", "4.4.5", "5.0", "5.1", "6.0", "7.0"]
	
	def __init__(self, mobile=""):
		self.mobile = mobile
		self.lon = 116
		self.lat = 40
		self.network = "WIFI"
		
	def select_brand(self):
		'''
			select a brand
		'''
		brand_num = len(self.brands)
		self.brand = self.brands[random.randint(0, brand_num-1)]
		aids = self.android_ids[self.brand]
		aid_num = len(self.android_ids)
		self.android_id = aids[random.randint(0, aid_num-1)]
		
	
	def select_os(self):
		'''
			select os version
		'''
		os_num = len(self.os_versions)
		self.os = self.os_versions[random.randint(0, os_num-1)]
		
	
	def gen_imei(self):
		'''
			generate immee 
		'''
		ts = self.TACs[self.brand]
		TAC_LEN = len(ts)
		TAC = ts[random.randint(0, TAC_LEN-1)]
		FAC_LEN = len(self.FACs)
		FAC = self.FACs[random.randint(0, FAC_LEN-1)]
		SNR=random.randint(10000, 599999)
		num = TAC + FAC + str(SNR)
		digits = [int(x) for x in reversed(str(num))]
		check_sum = sum(digits[1::2]) + sum((dig//10 + dig%10) for dig in [2*el for el in digits[::2]])
		check_bit = (10-check_sum%10)%10
		self.imei= num + str(check_bit)
		
	def gen_lat_lon(self):
		'''
			generate lat lon
		'''
		delta = round(random.random()*random.randint(1,4), 4)
		sign = random.randint(1, 100)
		if sign%2 == 0:
			self.lat += delta
		else:
			self.lat -= delta
		
		delta = round(random.random()*random.randint(1,4), 4)
		sign = random.randint(1, 100)
		if sign%2 == 0:
			self.lon += delta
		else:
			self.lon -= delta
			
	def gen_mac(self):
		'''
			gen mac address
		'''
		add_list = []
		for i in range(1,7):
			rand_str = "".join(random.sample("0123456789ABCDEF", 2))
			add_list.append(rand_str)
		self.mac = ":".join(add_list)
		
	def get_mobile_info(self):
		'''
			get a mobile info
		'''
		#1. select brand
		self.select_brand()
		#2. select os
		self.select_os()
		#3. imei
		self.gen_imei()
		#4. lat lon
		self.gen_lat_lon()
		#5. mac
		self.gen_mac()
		
	
	def show(self):
		print("Mobile:")
		print("\timei: {}".format(self.imei))
		print("\tlat: {}".format(self.lat))
		print("\tlon: {}".format(self.lon))
		print("\tmac: {}".format(self.mac))
		print("\tosversion: {}".format(self.os))
		print("\tnetwork: {}".format(self.network))
		
		
	
class Encrypt(object):
	'''
		Encrypt
	'''
	char_table = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 43, 47, 61]
	def __init__(self, key="w1215e436fb3c730", iv=""):
		self.key = key
		#self.iv = Random.get_random_bytes(16)
		self.iv = iv
	
	def dic_to_str(self, params):
		'''
			params -> string
			args:
				params dict
			return:
				params_str str
		'''
		params_str = urllib.urlencode(params)
		#print("pstr: {}".format(params_str))
		return params_str
	
	def aes_encrypt(self, params_str):
		'''
			params_str -> aes_str
			args:
				params_str str
			return:
				aes_str
		'''
		params_str = pad(params_str)
		self.iv = Random.get_random_bytes(16)
		#self.iv = str(bytearray([256-97, 66, 256-89, 91, 256-83, 79, 93, 70, 30, 256-69, 256-25, 256-57, 256-21, 40, 256-33, 256-9]))
		cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
		cipher_str = cipher.encrypt(params_str)
		return self.iv+cipher_str
		
	def bit_encrypt(self, aes_str):
		'''
			aes_str -> bit_str
			args:
				aes_str str
			return:
				bit_str
		'''
		aes_str_bytes = bytearray(aes_str)
		len_bytes = len(aes_str_bytes)
		block_num, left_num = divmod(len_bytes, 3)
		aes_bytes = []
		for i in range(block_num):
			B4_arr = self.three_to_four(
				aes_str_bytes[i*3],
				aes_str_bytes[i*3+1],
				aes_str_bytes[i*3+2]
			)
			aes_bytes.extend(B4_arr)
		
		if left_num == 0:
			bit_str = str(bytearray(aes_bytes).decode("ISO-8859-1"))
		else:
			if left_num == 1:
				b0 = aes_str_bytes[-1]
				B0 = b0>>2 & 0x3f
				B1 = b0<<4 & 0x30
				B2 = -1
				B3 = -1
			else:
				b0 = aes_str_bytes[-2]
				b1 = aes_str_bytes[-1]
				B0 = b0>>2 & 0x3f
				B1 = (b0<<4 & 0x30) + (b1>>4 & 0xf)
				B2 = b1<<2 & 0x3c
				B3 = -1
			aes_bytes.extend(
				[self.char_table[B0],self.char_table[B1],
				self.char_table[B2],self.char_table[B3]]
			)
			bit_str = str(bytearray(aes_bytes).decode("ISO-8859-1"))
		return bit_str
		
	def three_to_four(self, b0, b1, b2):
		'''
			3bytes --> 4bytes
		'''
		B0 = b0>>2 & 0x3f
		B1 = (b0<<4 & 0x30) + (b1>>4 & 0xf)
		B2 = (b1<<2 & 0x3c) + (b2>>6 & 0x3)
		B3 = b2 & 0x3f
		return [
			self.char_table[B0],
			self.char_table[B1],
			self.char_table[B2],
			self.char_table[B3]
		]
		
	def get_secret_param(self, params):
		'''
			encrypt the params
			args:
				params dict
			return:
				secret_str str
		'''
		#1. dic to str
		param_str = self.dic_to_str(params)#DF%3ACE%3AF4%3A31%3ABF%3A42
		#param_str = "android_id=KOT49H&platform=2&time=1490191995&ov=4.4.2&lon=116.3876&device_name=dpi&device_code=ffffffff97dca561ffffffffd3fdff87&brand=samsung&mac=DF:CE:F4:31:BF:42&vn=1.0.2&av=2&network=WIFI&lat=39.9065"
		#param_str = "device_name=dpi&device_code=0000000034f9b724ffffffff2d43d17e&platform=2&android_id=KOT49H&time=1490191995&ov=4.4.5&lon=116.3876&brand=samsung&mac=BD%3AFA%3AE5%3A0B%3AF0%3A84&vn=1.0.2&av=2&network=WIFI&lat=39.9065"
		#param_str = "device_code=ffffffff7b844f0d0000000020430d87&brand=samsung&vn=1.0.2&mac=BD%3AFA%3AE5%3A0B%3AF0%3A84&lat=39.4056&android_id=KOT49H&network=WIFI&lon=117.9325&device_name=dpi&platform=2&time=1490806988&ov=6.0"
		print("len: {}, dic to str: {}".format(len(param_str), param_str))
		#param_str = urllib.quote(param_str)
		#2. aes 
		aes_str = self.aes_encrypt(param_str)
		print("len: {}, aes str: {}".format(len(aes_str), aes_str))
		#3. bit_encrypt
		bit_str = self.bit_encrypt(aes_str)
		#rep_str = bit_str.replace("\n", "")
		print("len: {}, bit str: {}".format(len(bit_str), bit_str))
		#print("len: {}, rep str: {}".format(len(rep_str), rep_str))
		return bit_str
		
class Decrypt(object):
	'''
		decrypt
	'''
	char_table = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 43, 47, 61]
	def __init__(self, key="w1215e436fb3c730", iv="123"):
		self.key = key
		self.iv = iv
	
	def url_decrypt(self, param_str):
		'''
			url -> param
		'''
		return urllib.unquote(param_str)
		
	def bit_decrypt(self, url_str):
		'''
			url_str --> secret_str
		'''
		url_bytes = bytearray(url_str, "ISO-8859-1")
		url_len = len(url_bytes)
		block_num = int(url_len / 4)
		secret_bytes = []
		for i in range(block_num):
			b3_arr = self.four_to_three(
				url_bytes[i*4], url_bytes[i*4+1],
				url_bytes[i*4+2], url_bytes[i*4+3]
			)
			secret_bytes.extend(b3_arr)
		
		return str(bytearray(secret_bytes))
		
	def four_to_three(self, B0, B1, B2, B3):
		'''
			4bytes -> 3bytes
		'''
		B0 = self.char_table.index(B0)
		B1 = self.char_table.index(B1)
		B2 = self.char_table.index(B2)
		B3 = self.char_table.index(B3)
		table_len = len(self.char_table)-1
		if B3 == table_len:
			if B2 == table_len:
				b0 = (B0<<2 & 0xfc) | (B1>>4 & 0x3)
				return [b0]
			else:
				b0 = (B0<<2 & 0xfc) | (B1>>4 & 0x3)
				b1 = (B1<<4 & 0xf0) | (B2>>2 & 0xf)
				return [b0, b1]
		else:
			b0 = (B0<<2 & 0xfc) | (B1>>4 & 0x3)
			b1 = (B1<<4 & 0xf0) | (B2>>2 & 0xf)
			b2 = (B2<<6 & 0xc0) | (B3 & 0x3f)
			return [b0, b1, b2]
			
	def aes_decrypt(self, secret_str):
		'''
			secret_str -> params_str
		'''
		self.iv = secret_str[0:16]
		#print("iv: {}".format(self.iv.encode("")))
		secret_data = secret_str[16:]
		cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
		params_str = cipher.decrypt(secret_data)
		return params_str
	
	def get_param_str(self, url):
		#1. get the s=url_str
		if url.find("?&") != -1:
			print("url: {}".format(url.split("?&")[0]))
			cipher_str = url.split("?&")[1][2:]
		else:
			cipher_str = url
		#print("len:{}, cipher str: {}".format(len(cipher_str),cipher_str))
		#2. decode
		url_str = self.url_decrypt(cipher_str)
		print("len:{}, decode str: {}".format(len(url_str),url_str))
		#3. bit_decrypt
		secret_str = self.bit_decrypt(url_str)
		print("len:{}, secret str: {}".format(len(secret_str),secret_str))
		#4. aes_decrypt
		params_str = self.aes_decrypt(secret_str)
		#print("index:{}".format(-ord(params_str[-1])))
		#print("len:{}, params str: {}".format(len(params_str),params_str))
		params_str = unpad(params_str)
		print("len:{}, params str: {}".format(len(params_str),params_str))
		return urllib.unquote(params_str)
		
def test_device_code():
	mobile = Mobile()
	ktt = KTT(mobile)
	ktt.gen_device_code()
	print("device_code: {}".format(ktt.device_code))
	
def test_start():
	mobile = Mobile()
	ktt = KTT(mobile)
	ktt.gen_device_code()
	ktt.get_api_start()

def test_mobile():
	mobile = Mobile()
	mobile.get_mobile_info()
	mobile.show()
		
def test_encrypt():
	params = {
		'name': 'g c ',
		"tel": "1248972395",
		"info": "infomation",
	}
	encrypt = Encrypt()
	secret_str = encrypt.get_secret_param(params)
	return secret_str
	
	
urls = {
	"aos_update_info": "http://api.applezhuan.com/api/c/aos_update_info?&s=07O%2FBYg6m3tt%2BnIk%2BRkuGzFnsiNrEFrL0RqJddjNaSM%3D",
	"start":"http://api.applezhuan.com/api/c/start?&s=n0KnW61PXUYeu%2BfH6yjf9wq30TMtcfkhCLN70CU1W%2B7r1RB87l8BLJUUNHLYw4me%2B7nQscGSDibpYoP9UXBYnKmiSYRM4C3trbde5F55yzGzIQ2AMv0L1L4EOxGac4FhzAlzdqwEj%2FCNVTWa%2BVeFrno6BpreWrMV7RLUOMa05qB4wXx3AixB%2FTHODUsv5sZ%2FUYYDDSk9CZLBLK%2Bw%2FZa5NaCsTbNnPQLEiNEVMuZ9ANp35iXtQcr6izykfwQsQ3CT%2FnItaKJGIWI3PXNxk3J0zcBUPFXJ6i5jnfb8gWLjBeEGUv90T9rZWIfojcMEfBr7",
	"get_default_channellist":"http://api.applezhuan.com/api/c/get_default_channellist?&s=WWXttPxs3pMaohAatKl9zdEP%2Fn%2B8UIJ%2FR%2FNphicwO4RyDRF3tSuFwWq%2BgGKZl4yIaS%2F5tPcLetYNkkJYLaVJltDkBFNcNcaZhlVREtUMKnkHv6akRj2%2FmBSIuggYJbV%2FbaDOdQtgv4H%2BAU%2BEPvAs2EvYZcsJz5MbIGrYAGB61VdfYbjUdFWRUpRdagHA0MUkc5yh3zTQWASCElp3ZyI0Se3GrefV1fP%2BUjJ0PQ9ZSjaD2SVPcKmtI4wNpFcs234BarQQiu8UpMMo%2F8vZDUpuWw8uMUsNHoZewl5cpAgfpjOZgPDJDjqRoYV8kzs%2FaApu",
	"getlist":"http://api.applezhuan.com/api/c/getlist?&s=lpSWZNJdbOENS8DXlNWgYuJvBGRQz9BB5TVI%2Bzmzz5J5Vo1WwmhjI35FZHTib%2FgCgZEimlDzRJD6gC0tv%2B3lI0zgl9nI6BiC2234h1OxH%2FION3Ah6r0m0ZqeMX9bcZ4RF1qahOF6inejBc8%2BAeKe%2FCOx6O8OMqowUTA2J7BpQP8fAQj6ZVYZcz95QyN3CSRmM36r1lVJ2OkJiWUl2%2BsVELweTErx%2BYhbGwe8%2BA1Jtt9mBdvnEdgnBACgFlBsmB5qTEkbaXXXJ0SfEF2VvkQJroHDi%2B32OS8zLW2QY7J8QqZkUigM1bdOzLCcuHE5WFLYy%2FYofYm2Ew90%2BAS6PczsomkQOo7%2BN63t%2FsLPv2qmYhY%3D",
	"get_guestinfo":"http://api.applezhuan.com/api/c/get_guestinfo?&s=vs2Z7HY1jV2rfFEsjEKB4mVyNcRKKq8jazww4hZP2uv%2F7YihlcLBalnNT1%2BVE7XSuujhYBv3gfbmOdRkG7TJme1wt25XMH5BRY9lFAP0zLN73FsHLjsBIXh%2FBDWEpbl3z6Tt4ixjtOD%2FC9tzSwW0oJ6FpNtMAlucpfknTzOs0XVfK81tRmLDsZbhz4gd7y4mZPUfbKvkStRsl8hVHxEgjPVfnEUwh9Rvvo5on031YB9nPtQ%2BmBtNkjFac1PzLH3pqLMrVvI8UVF8AAN8p9M0wtYQUFMR1WwIkG6ViQR9w2ZBVxoYvf5BfzbDM2Q9FrKD",
	"get_img_captcha":"http://api.applezhuan.com/api/c/get_img_captcha?&s=kKcEheRDc1flWMYBOtwoA0LjpfSmQcJ8by%2FDACZkUbuftmnPaGdzCiaCeBuXWejoJXDV2KUAlwjKX393wXj2A4v0GpTjoywdTqD6ieJBE4s1fHgktlNgyAZQynokj%2B26",
	"get_sms_captcha":"http://api.applezhuan.com/api/get_sms_captcha?&s=ogOUYwN7xhGkdqcFz4PbWDrptKkpTodbAxnU3MdagfNFL%2BJbQ3BwXqmMfbbrpDpoELszxDnf7xzB4m62qHwRi%2BwRtSXyULIu8kiiQ79yK09aEWLm4MMH06VbzxXMNy5qE%2FTGJATnKaMbx%2FS6kxyhuJNqZ5apCL%2B33uLOmRgXbNpgDWDNt0Sb7lt0dALWmBBl",
	"get_userinfo":"http://api.applezhuan.com/api/c/get_userinfo?&s=9xzktnhOagKIE53KGl3oNnJ%2B45Hbi7DdqJzVjvA5nHoK0ILPFJkrHkVtYJ%2BbXhPSrG7uoN4RDsWRze5epbtI1kqhAiTXLbHMerftN2jDPSk%2BrAeheYXKdk6sxtu4DF4JE3CiP4j7f23bGGqYQDDNsVzB0zaadY2ZQ7ChNDzVy3Hof1Bn9LO6B2XmALm3RsGVDDW2K%2FsnMmg4nLU%2FjiJ2YM8KyJfX4R2JlM7PVPC%2FdqMKLnSl5U9z3Y2mVJ7rHZsB5muIxa9avfBKzFxoKcto4uBnQO%2Bvzh1T%2BBK01sgmOiwD1pXiqeiN3sS6Q2XfMlJDOuHOS93T11XmNwc83ALYhZ7GIS94lQQzJHwwhrXa0krs7ehGP449hTirDnhycsDrsFqTAKuOyytCiUHmblQhTc76yfUFEBXGZarnKqD%2FrBwQcDFmExlf%2Bjx3CdMIKOLzYd3vsN%2B0laSWvyQ6PsUFSrHLEc3QTCQ74fsOLGbQKk6UOH6Ys2uvdrp2dCXCp7WFVrkHRbaLL%2FtDOOekpmu3tQ%3D%3D",
	"get_content":"http://api.applezhuan.com/api/c/get_content?&s=nUddm3eL5zGKFYFAyJvWk4o%2FPFkWhlb3o1KLGE6rO9VaIoCDwkaM8Kw8JvdNCIlhoRxpkfWFzccd%2B0I00PuEGutk4YsikiuINVeuiBfldrkktbBKIGV8SgVx8HE%2B%2B9X1Je6IMyKfuf5e5hkISJWMiZAt24HIc7kNXzsBZAfbT4UW1TCjZJpUCvB9MVZ1dWk8gHagI0nhv4Z1LRbaFZbiK8k%2BvT6wvRqt9omOIUgMmWJuaS5vbCmh7kNKWsRomx4L%2BnHB9j1CMqZpHUBn3Jk5YnbwoDE3Ds6FJBGqEPuRJIE%3D",
	"login_post":"http://api.applezhuan.com/api/c/login?&s=rXdjGQD8y9hszEPSFS4yiYDTiqc%2FfmOsGVxUDXRBA9hViyPaxV0IGgNZpx1KeJ7HCglRTIr5ocN0Z5sn0fAhuWl4GKNiJM%2FjaiVOH8qJnUHkPAHe6F8e4imcluEEbXtuyVo7D55gV4zBcHKW345wOjhiM3WMl6zW37YN39Gvw5CZNdSkjM8Uy%2F%2Fcy0Eh%2B%2BaQXsBXfqyhG53jn5QB6LLrWRjm2LtXPf8GE%2B3nTD23by3wzEsxEun6e89I2kwiWK9wBECphbaMusWRZkN%2FFF0ApcCW7BIm4y0BlRrHiiemqSIV4%2FbBoTVcoXD4RFIlav3SdJZCEtMyrvaQwKcIZTA7F8ldev0kkWhNePNsXQhcMcllcpljvJVa7HJFU1rZQCOZHfqqdB3q5UVXNkTOSnCjHYv2kfh2uk%2Bm%2F8msJ1xL5ow%3D",
	"register_post":"http://api.applezhuan.com/api/c/register?&s=OwBjPvLckT4biOj%2Br3j8KSXu67DrVYjG7%2BenFspMJKPIZgDwh10K2f%2BylDHgQxWxfasmNy9Oh5aW2FPq%2F5cekX%2FPFPa9%2FgQIrn6puv1%2FTyiRpHvlGfA8umOCyuB3IKv%2FAD1oEQhrDDm8pjLvCef2d8EW00z3E%2F4rYAFzPJS9ZWhDDhiorCLwKTc5deUgqEG91OUWzLJVdcEjxr7%2F5BuuPOX7kknzhl8hcOhts3gGQmQSRlSOOsRPhCTBqeVHIkVs%2FzmcOGiiHUJ9n44vBZOjj0YiefYYBG94e%2F6BoViwpC9AskDUnm%2F0dZZ3HPMyxvd%2BgqppcHBYZ%2Bi5VHt7%2Fq6od2NQQ4GRiOqYWb7OacXP4oXyLP2WFudeW3zqQmhCx%2FkDDZCd6JugKDPm%2FR9gRCoBig%3D%3D",
	"get_userinfo1":"http://api.applezhuan.com/api/c/get_userinfo?&s=nAUNfbXWkuYGTlZOyncFR584MgXiasHooBH8RVz1GJqmg8Imymg0l2srp%2FmlnAKexQoZ4bvbeUk7gXtO%2BA0hQu7HDzjfAglh5w1ARdGCUirpFuY%2BAKvdrlY%2BBEKltGJOzpeKsCIVUanLpzVvByXsArUQsywuJcu6ssQK6lwNEc3E1AXpmv%2Be80JDn%2BZz5lB4ICOfmmNFAbJnnkhFtuzMZ0Z65g2nEJ6oMiHulYow37SSNEyah8n%2Bxghv6sW2XMEi2YswsO9MtoW5nkC25tBNJlf2%2BuL2sPJLj12ytNfIMSDeY9K7Ao8MZtYNz33eYTY7Ino4MrFh92I%2BE3UysuyQThSeUsZlVUEmfIkWuuvv%2B50S7aoNld4HAVGTjESI1rdYUCOHD%2BM5b%2F5IZ2jODGQugo9lSOiYrDRQ%2BuQz8zM8DMJxpx2JJBZwbqRdIarIdQ00SFZqjHfdZ1pC9%2Fo9AYxmWA8lydGcxflomPEjDcGPj6%2Bk9dqMSRlGFZYn9VXmcbCtsg1DrssELSNx7ZNuMCEin1aW674FJiqJGi1%2BoY6dIpw%3D"
}


def test_decrypt():
	decrypt = Decrypt()
	for key, value in urls.items():
		print("key: {}".format(key))
		params_str = decrypt.get_param_str(value)
		print("params: {}".format(params_str))
		print("\n")
		
def test_decrypt_one():
	decrypt = Decrypt()
	key = "start"
	print("key: {}".format(key))
	value = urls[key]
	params_str = decrypt.get_param_str(value)
	print("params: {}".format(params_str))
	print("\n")
		


def check_encrypt():
	#secret_str = test_encrypt()
	secret_str = "http://api.applezhuan.com/api/c/start?&s=n0KnW61PXUYeu%2BfH6yjf9wq30TMtcfkhCLN70CU1W%2B7r1RB87l8BLJUUNHLYw4me%2B7nQscGSDibpYoP9UXBYnKmiSYRM4C3trbde5F55yzGzIQ2AMv0L1L4EOxGac4FhzAlzdqwEj%2FCNVTWa%2BVeFrno6BpreWrMV7RLUOMa05qB4wXx3AixB%2FTHODUsv5sZ%2FUYYDDSk9CZLBLK%2Bw%2FZa5NaCsTbNnPQLEiNEVMuZ9ANp35iXtQcr6izykfwQsQ3CT%2FnItaKJGIWI3PXNxk3J0zcBUPFXJ6i5jnfb8gWLjBeEGUv90T9rZWIfojcMEfBr7"
	decrypt = Decrypt()
	plainText = decrypt.get_param_str(secret_str)
	#print("len: {}, iv: {}".format(len(decrypt.iv), decrypt.iv))
	print(plainText)
	print("**"*20)
	
	encrypt = Encrypt(iv=decrypt.iv)
	encrypt.get_secret_param({})
	
def test_urllib():
	url_str = "n0KnW61PXUYeu%2BfH6yjf9wq30TMtcfkhCLN70CU1W%2B7r1RB87l8BLJUUNHLYw4me%2B7nQscGSDibpYoP9UXBYnKmiSYRM4C3trbde5F55yzGzIQ2AMv0L1L4EOxGac4FhzAlzdqwEj%2FCNVTWa%2BVeFrno6BpreWrMV7RLUOMa05qB4wXx3AixB%2FTHODUsv5sZ%2FUYYDDSk9CZLBLK%2Bw%2FZa5NaCsTbNnPQLEiNEVMuZ9ANp35iXtQcr6izykfwQsQ3CT%2FnItaKJGIWI3PXNxk3J0zcBUPFXJ6i5jnfb8gWLjBeEGUv90T9rZWIfojcMEfBr7"
	url_str = urllib.unquote(url_str)
	print(url_str)
if "__main__" == __name__:
	#check_encrypt()
	#test_decrypt_one()
	#test_mobile()
	#test_device_code()
	test_start()
	#test_urllib()
	