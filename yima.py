# coding: utf-8
import requests
import time


class YIMA:
    """
        login yi ma platform
    """
    def __init__(self, item_id='2674'):
        """
            args:
                item_id (2730 (zx), 2674(qtt), 6381(ktt))
        """
        self.url='http://api.51ym.me/UserInterface.aspx'
        self.token = ""
        self.item_id = item_id
        self.mobile = ""
        self.headers = {
            "Content-Type":"text/plain;charset:utf8;"
        }
        
    def login_yi_ma(self):
        """
            login
        """
        body = {
            'action': 'login',
            'username': 'gc12306',
            'password': 'gaochong1513'
        }
        r = requests.get(self.url, params=body, headers=self.headers)
        result = r.text.split('|')
        token = result[1]
        self.token = token

    def get_mobile(self):
        """
            get mobile for item_id = self.item_id
        """		
        
        body = {
            'action': 'getmobile',
            'token': self.token,
            'itemid': self.item_id
        }
        r = requests.get(self.url, params=body)
        result = r.text.split('|')
        if result[0] == 'success':
            mobile = result[1]
            self.mobile = mobile
            return mobile
        else:
            return None
            
    def release_all(self):
        """
            release all mobiles
        """
        body = {
            'action': 'releaseall',
            'token': self.token
        }
        r = requests.get(self.url, params=body)
        print(r.text)
    
    def get_message(self):
        """
            get message code
            return:
                message
        """
        print ("get message.")
        body={
            'action': 'getsms',
            'mobile': self.mobile,
            'itemid': self.item_id,
            'token': self.token
        }
        sms = "3001"
        while sms == '3001':
            r = requests.get(self.url, params=body)
            # print("encoding: %s" % r.apparent_encoding)
            sms = r.content.decode("utf-8").encode("utf-8")
            print ("message:%s" % sms)
            time.sleep(5)
        sms=sms.split('|')[1]
        return sms
        
    def get_code(self):
        """
        get the sms code
        :return: 
        """
        sms = self.get_message()
        # sms = sms.encode("utf-8")
        # sms = "【快头条】验证码5458，您正在注册成为快头条用户，感谢您的支持！"
        # print (sms)
        if self.item_id == "2730":
            begin = sms.find(':')+1
            end = sms.find(',')
            code = sms[begin:end]
            return code
        elif self.item_id == "2674":
            index = sms.find("。")
            return sms[index-4:index]
        elif self.item_id == "6381":
            index = sms.index("，")
            # print("index: %d" % index)
            return sms[index-4:index]

def main():
    sms = u"【快头条】验证码2149，您正在注册成为快头条用户，感谢您的支持！"
    # sms = sms.encode("utf-8")
    print(sms)

    # index = sms.find("，")
    # index = sms.index("，")
    # print("Hello. %d" % index)
    # ym = YIMA("6381")
    # code = ym.get_code()
    # print(code)
if "__main__" == __name__:
    main()
