import sys

from KuaiTT import Mobile, KTT, StrUtil, Encrypt, Decrypt
from yima import YIMA
import urllib
import pytesseract
from PIL import Image, ImageDraw
import time

def test_device_code():
    mobile = Mobile()
    ktt = KTT(mobile)
    ktt.gen_device_code()
    print("device_code: {}".format(ktt.device_code))


def test_start():

    yi_ma = YIMA("6381")
    yi_ma.login_yi_ma()
    # 1. get mobile
    time.sleep(3)
    mobile_num = yi_ma.get_mobile()
    mobile = Mobile(mobile_num)
    print("mobile: %s" % mobile_num)
    if mobile:
        ktt = KTT(mobile)
        ktt.gen_device_code()
        ktt.get_api_start()
        print("cookie: {}".format(ktt.cookie))
    # get channel list
    # channel_list = ktt.get_api_default_channel_list()
    # print(channel_list)
    # get guest info
    # ktt.get_guest_info()

    # for i in range(6, 20):
    #     time.sleep(3)
    #     decode_png = ktt.get_img_captcha()
    #     path = "imgs/%d.png"% i
    #     print(path)
    #     with open(path, "wb") as f:
    #         f.write(decode_png)

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
            time.sleep(5)
            sms_captcha = yi_ma.get_code()
            print("sms_captcha: %s" % sms_captcha)
            time.sleep(3)
            ktt.post_register(sms_captcha)
            time.sleep(3)
            ktt.get_user_info()
            return mobile_num
    yi_ma.release_all()



    # 0 normal
    # -2043 mobile exists
    # -1113 pic code error

    # print("sms result: %s" % result)


def test_orc():
    for i in range(0, 20):
        image = Image.open("imgs/%d.png"% i)
        draw = ImageDraw.Draw(image)
        white_color = (255, 255, 255)
        for x in range(0, image.size[0]):
            for y in range(0, image.size[1]):
                color = image.getpixel((x, y))
                if color[2] == 0:
                    draw.point((x, y), white_color)
        image.save("tifs/%d%d.tif"%(i,i))
        code = pytesseract.image_to_string(image, lang="ktt")
        print("%d code: %s"% (i,code))


def test_show_default_channel_list():
    c_list = [{u'id': 1, u'name': u'\u63a8\u8350'}, {u'id': 3, u'name': u'\u5a31\u4e50'}, {u'id': 5, u'name': u'\u641e\u7b11'}, {u'id': 6, u'name': u'\u7f8e\u5973'}, {u'id': 7, u'name': u'\u60c5\u611f'}, {u'id': 8, u'name': u'\u4f53\u80b2'}, {u'id': 9, u'name': u'\u8d22\u7ecf'}, {u'id': 10, u'name': u'\u6c7d\u8f66'}, {u'id': 11, u'name': u'\u7f8e\u98df'}, {u'id': 12, u'name': u'\u79d1\u6280'}, {u'id': 13, u'name': u'\u65f6\u5c1a'}, {u'id': 14, u'name': u'\u5065\u5eb7'}, {u'id': 15, u'name': u'\u623f\u4ea7'}, {u'id': 16, u'name': u'\u661f\u5ea7'}, {u'id': 17, u'name': u'\u80b2\u513f'}]
    print("*"*50)
    # print("id : {}, name: {}".format(c_list[0]["id"],c_list[0]["name"]))
    for channel in c_list:
        id = channel["id"]
        name = channel["name"]
        print("id : %d, name: %s" % (id, name))
    print("*"*50)


def test_show_guest_info():
    """
    birth coin uid name mobile father headimg income balance  
    :return: 
    """
    guest_info = {u'coin': 0, u'h5_url': {u'notice_url': u'http://m.applezhuan.com/notice.html', u'income_url': u'http://m.applezhuan.com/detail.html', u'feedback_url': u'http://m.applezhuan.com/feedback.html', u'exchange_url': u'http://m.applezhuan.com/exchange.html', u'privacy_url': u'http://m.applezhuan.com/privacy.html', u'about_url': u'http://m.applezhuan.com/about.html'}, u'mobile': u'', u'menu': [{u'title': u'\u65b0\u624b\u6307\u5f15', u'url': u'http://m.applezhuan.com/task_new.html', u'tip': u'', u'show_type': 1, u'desc': u'\u5b8c\u6210\u65b0\u624b\u95ee\u5377\uff0c\u53ef\u5f9710\u91d1\u5e01\u5956\u52b1', u'type': 1, u'id': 1, u'icon': u'http://m.applezhuan.com/images/icon_xingshouzhinan.png'}, {u'title': u'\u5ba2\u670d\u4e2d\u5fc3', u'url': u'http://m.applezhuan.com/customer.html', u'tip': u'', u'show_type': 1, u'desc': u'\u89e3\u51b3\u70e6\u607c\uff0c\u5168\u8eab\u5fc3\u73a9\u5e94\u7528', u'type': 1, u'id': 7, u'icon': u'http://m.applezhuan.com/images/icon_kefuzhongxing.png'}], u'father': u'0', u'headimg': u'', u'birth': u'', u'income': 0, u'uid': 0, u'balance': 0, u'banner': [], u'name': u''}
    guest_info.pop("h5_url")
    guest_info.pop("banner")
    guest_info.pop("menu")
    for key, val in guest_info.items():
        print("key: %s value: %s"% (key, val))

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




def test_decrypt():
    decrypt = Decrypt()
    for key, value in urls.items():
        print("key: {}".format(key))
        params_str = decrypt.get_param_str(value)
        print("params: {}".format(params_str))
        print("\n")


def test_decrypt_one(key):
    decrypt = Decrypt()
    # key = "start"
    print("key: {}".format(key))
    value = urls[key]
    params_str = decrypt.get_param_str(value)
    print("params: {}".format(params_str))
    print("\n")


def check_encrypt():
    # secret_str = test_encrypt()
    secret_str = "http://api.applezhuan.com/api/c/start?&s=n0KnW61PXUYeu%2BfH6yjf9wq30TMtcfkhCLN70CU1W" \
                 "%2B7r1RB87l8BLJUUNHLYw4me" \
                 "%2B7nQscGSDibpYoP9UXBYnKmiSYRM4C3trbde5F55yzGzIQ2AMv0L1L4EOxGac4FhzAlzdqwEj%2FCNVTWa" \
                 "%2BVeFrno6BpreWrMV7RLUOMa05qB4wXx3AixB%2FTHODUsv5sZ%2FUYYDDSk9CZLBLK%2Bw" \
                 "%2FZa5NaCsTbNnPQLEiNEVMuZ9ANp35iXtQcr6izykfwQsQ3CT" \
                 "%2FnItaKJGIWI3PXNxk3J0zcBUPFXJ6i5jnfb8gWLjBeEGUv90T9rZWIfojcMEfBr7 "
    decrypt = Decrypt()
    plain_text = decrypt.get_param_str(secret_str)
    # print("len: {}, iv: {}".format(len(decrypt.iv), decrypt.iv))
    print(plain_text)
    print("**" * 20)

    encrypt = Encrypt(iv=decrypt.iv)
    encrypt.get_secret_param({})


def test_urllib():
    url_str = "n0KnW61PXUYeu%2BfH6yjf9wq30TMtcfkhCLN70CU1W%2B7r1RB87l8BLJUUNHLYw4me" \
              "%2B7nQscGSDibpYoP9UXBYnKmiSYRM4C3trbde5F55yzGzIQ2AMv0L1L4EOxGac4FhzAlzdqwEj%2FCNVTWa" \
              "%2BVeFrno6BpreWrMV7RLUOMa05qB4wXx3AixB%2FTHODUsv5sZ%2FUYYDDSk9CZLBLK%2Bw" \
              "%2FZa5NaCsTbNnPQLEiNEVMuZ9ANp35iXtQcr6izykfwQsQ3CT" \
              "%2FnItaKJGIWI3PXNxk3J0zcBUPFXJ6i5jnfb8gWLjBeEGUv90T9rZWIfojcMEfBr7 "
    url_str = urllib.unquote(url_str)
    print(url_str)

urls = {
    "getlist2": "http://api.applezhuan.com/api/c/getlist?&s=T%2BMxP9B%2B58ZCpjoEd4ix4ZKaluQn1F2Vpvex%2BVohxJBIjop7GQeE9cW2LUoz%2FZguHT23ObPb2ig8tnYHBrblQppKl%2BiN%2FS0rJAzVbfX7qFYg2op%2Fv51OdFWPybHCok949XSwxgJN8eCjSH9RIcQ2NVaEkAEeu8MlNlgU0ztqoMsOCs1r2a9dVq8jcWwoENFnU3UQgjhVD0R2yjoMGc84j%2FK0gDZwPe5ND8EgMqb97SdMlpWq3Bkx4WF2qw%2FhOaVUz8pdFOtdxgMiqfbxwc%2FWamjUTvpqigwDzlZeEwITPi41Vl2TLHPmvAVMIYqg9tsFo2bfmQUHWkBvKs0x1vdIvIxqbPp0uA7rgtPjL3rzSHg%3D",
    "update_user": "http://api.applezhuan.com/api/c/update_user_info?&s=FTDTHHO4wIdoUWgVDI3uy3qspq4XrHXwkitUItPuNniSYfKhsorJnIw6VsVh56f7er9Zji0TjgeSao411kaT9NKCqWNw9Q5hHvyng58wAYg%3D",
    "aos_update_info": "http://api.applezhuan.com/api/c/aos_update_info?&s=07O%2FBYg6m3tt%2BnIk"
                       "%2BRkuGzFnsiNrEFrL0RqJddjNaSM%3D",
    "start": "http://api.applezhuan.com/api/c/start?&s=n0KnW61PXUYeu%2BfH6yjf9wq30TMtcfkhCLN70CU1W"
             "%2B7r1RB87l8BLJUUNHLYw4me%2B7nQscGSDibpYoP9UXBYnKmiSYRM4C3trbde5F55yzGzIQ2AMv0L1L4EOxGac4FhzAlzdqwEj"
             "%2FCNVTWa%2BVeFrno6BpreWrMV7RLUOMa05qB4wXx3AixB%2FTHODUsv5sZ%2FUYYDDSk9CZLBLK%2Bw"
             "%2FZa5NaCsTbNnPQLEiNEVMuZ9ANp35iXtQcr6izykfwQsQ3CT"
             "%2FnItaKJGIWI3PXNxk3J0zcBUPFXJ6i5jnfb8gWLjBeEGUv90T9rZWIfojcMEfBr7",
    "get_default_channel_list": "http://api.applezhuan.com/api/c/get_default_channellist?&s=WWXttPxs3pMaohAatKl9zdEP"
                               "%2Fn%2B8UIJ%2FR%2FNphicwO4RyDRF3tSuFwWq%2BgGKZl4yIaS"
                               "%2F5tPcLetYNkkJYLaVJltDkBFNcNcaZhlVREtUMKnkHv6akRj2%2FmBSIuggYJbV%2FbaDOdQtgv4H%2BAU"
                               "%2BEPvAs2EvYZcsJz5MbIGrYAGB61VdfYbjUdFWRUpRdagHA0MUkc5yh3zTQWASCElp3ZyI0Se3GrefV1fP"
                               "%2BUjJ0PQ9ZSjaD2SVPcKmtI4wNpFcs234BarQQiu8UpMMo"
                               "%2F8vZDUpuWw8uMUsNHoZewl5cpAgfpjOZgPDJDjqRoYV8kzs%2FaApu",
    "getlist": "http://api.applezhuan.com/api/c/getlist?&s=lpSWZNJdbOENS8DXlNWgYuJvBGRQz9BB5TVI"
               "%2Bzmzz5J5Vo1WwmhjI35FZHTib%2FgCgZEimlDzRJD6gC0tv%2B3lI0zgl9nI6BiC2234h1OxH"
               "%2FION3Ah6r0m0ZqeMX9bcZ4RF1qahOF6inejBc8%2BAeKe"
               "%2FCOx6O8OMqowUTA2J7BpQP8fAQj6ZVYZcz95QyN3CSRmM36r1lVJ2OkJiWUl2%2BsVELweTErx%2BYhbGwe8"
               "%2BA1Jtt9mBdvnEdgnBACgFlBsmB5qTEkbaXXXJ0SfEF2VvkQJroHDi%2B32OS8zLW2QY7J8QqZkUigM1bdOzLCcuHE5WFLYy"
               "%2FYofYm2Ew90%2BAS6PczsomkQOo7%2BN63t%2FsLPv2qmYhY%3D",
    "get_guest_info": "http://api.applezhuan.com/api/c/get_guestinfo?&s=vs2Z7HY1jV2rfFEsjEKB4mVyNcRKKq8jazww4hZP2uv"
                     "%2F7YihlcLBalnNT1%2BVE7XSuujhYBv3gfbmOdRkG7TJme1wt25XMH5BRY9lFAP0zLN73FsHLjsBIXh"
                     "%2FBDWEpbl3z6Tt4ixjtOD%2FC9tzSwW0oJ6FpNtMAlucpfknTzOs0XVfK81tRmLDsZbhz4gd7y4mZPUfbKvkStRsl8hVHxEgjPVfnEUwh9Rvvo5on031YB9nPtQ%2BmBtNkjFac1PzLH3pqLMrVvI8UVF8AAN8p9M0wtYQUFMR1WwIkG6ViQR9w2ZBVxoYvf5BfzbDM2Q9FrKD",
    "get_img_captcha": "http://api.applezhuan.com/api/c/get_img_captcha?&s=kKcEheRDc1flWMYBOtwoA0LjpfSmQcJ8by"
                       "%2FDACZkUbuftmnPaGdzCiaCeBuXWejoJXDV2KUAlwjKX393wXj2A4v0GpTjoywdTqD6ieJBE4s1fHgktlNgyAZQynokj"
                       "%2B26",
    "get_sms_captcha": "http://api.applezhuan.com/api/get_sms_captcha?&s"
                       "=ogOUYwN7xhGkdqcFz4PbWDrptKkpTodbAxnU3MdagfNFL%2BJbQ3BwXqmMfbbrpDpoELszxDnf7xzB4m62qHwRi"
                       "%2BwRtSXyULIu8kiiQ79yK09aEWLm4MMH06VbzxXMNy5qE%2FTGJATnKaMbx%2FS6kxyhuJNqZ5apCL"
                       "%2B33uLOmRgXbNpgDWDNt0Sb7lt0dALWmBBl",
    "get_user_info": "http://api.applezhuan.com/api/c/get_userinfo?&s=9xzktnhOagKIE53KGl3oNnJ"
                    "%2B45Hbi7DdqJzVjvA5nHoK0ILPFJkrHkVtYJ%2BbXhPSrG7uoN4RDsWRze5epbtI1kqhAiTXLbHMerftN2jDPSk"
                    "%2BrAeheYXKdk6sxtu4DF4JE3CiP4j7f23bGGqYQDDNsVzB0zaadY2ZQ7ChNDzVy3Hof1Bn9LO6B2XmALm3RsGVDDW2K"
                    "%2FsnMmg4nLU%2FjiJ2YM8KyJfX4R2JlM7PVPC%2FdqMKLnSl5U9z3Y2mVJ7rHZsB5muIxa9avfBKzFxoKcto4uBnQO"
                    "%2Bvzh1T%2BBK01sgmOiwD1pXiqeiN3sS6Q2XfMlJDOuHOS93T11XmNwc83ALYhZ7GIS94lQQzJHwwhrXa0krs7ehGP449hTirDnhycsDrsFqTAKuOyytCiUHmblQhTc76yfUFEBXGZarnKqD%2FrBwQcDFmExlf%2Bjx3CdMIKOLzYd3vsN%2B0laSWvyQ6PsUFSrHLEc3QTCQ74fsOLGbQKk6UOH6Ys2uvdrp2dCXCp7WFVrkHRbaLL%2FtDOOekpmu3tQ%3D%3D",
    "get_content": "http://api.applezhuan.com/api/c/get_content?&s=nUddm3eL5zGKFYFAyJvWk4o"
                   "%2FPFkWhlb3o1KLGE6rO9VaIoCDwkaM8Kw8JvdNCIlhoRxpkfWFzccd"
                   "%2B0I00PuEGutk4YsikiuINVeuiBfldrkktbBKIGV8SgVx8HE%2B"
                   "%2B9X1Je6IMyKfuf5e5hkISJWMiZAt24HIc7kNXzsBZAfbT4UW1TCjZJpUCvB9MVZ1dWk8gHagI0nhv4Z1LRbaFZbiK8k"
                   "%2BvT6wvRqt9omOIUgMmWJuaS5vbCmh7kNKWsRomx4L%2BnHB9j1CMqZpHUBn3Jk5YnbwoDE3Ds6FJBGqEPuRJIE%3D",
    "login_post": "http://api.applezhuan.com/api/c/login?&s=rXdjGQD8y9hszEPSFS4yiYDTiqc"
                  "%2FfmOsGVxUDXRBA9hViyPaxV0IGgNZpx1KeJ7HCglRTIr5ocN0Z5sn0fAhuWl4GKNiJM"
                  "%2FjaiVOH8qJnUHkPAHe6F8e4imcluEEbXtuyVo7D55gV4zBcHKW345wOjhiM3WMl6zW37YN39Gvw5CZNdSkjM8Uy%2F"
                  "%2Fcy0Eh%2B%2BaQXsBXfqyhG53jn5QB6LLrWRjm2LtXPf8GE%2B3nTD23by3wzEsxEun6e89I2kwiWK9wBECphbaMusWRZkN"
                  "%2FFF0ApcCW7BIm4y0BlRrHiiemqSIV4"
                  "%2FbBoTVcoXD4RFIlav3SdJZCEtMyrvaQwKcIZTA7F8ldev0kkWhNePNsXQhcMcllcpljvJVa7HJFU1rZQCOZHfqqdB3q5UVXNkTOSnCjHYv2kfh2uk%2Bm%2F8msJ1xL5ow%3D",

    "login_post1": "http://api.applezhuan.com/api/c/login?&s=BP%2FJ3EgrIBweBzOP6scfli7kQWt8Qg1zaPrnuGIdn"
                   "%2B8gyaBFoojT9dg8fM8C9rZ%2F1Z3sqUNCZoKW1VnMZVxeaiSsvnXXY6mS8rzs%2FFkvMBXWjbdwbX"
                   "%2F1m9tLhWbrBD2PfIwmqm7FoX%2F51f5y9i8VpyPOUxjO2pMWY"
                   "%2FUwqjXdrsPnFQp2bn87RoCxo0n5Ls1GNL2pfxG250GYpwdm2v%2Fhh3p%2B9G8l%2Ft0gDr"
                   "%2FYMMfLetjZeoSwDV2EXti5VpVpecT708Ym2zVFVHpqYiY1xPSl7VWL78fJLQtU6LZtABP4550BIY"
                   "%2FlTZUthrpecC3e9PNo9W0URaMpdB3avpFusu"
                   "%2BBaMyM2MmxJvGQ3FJOyu42K47L2xsczSBcdXx4NkKYPzTfSpMGxWdKMHOTLiHhoj4%2Bdg%2FtOIoZMWJHfDdNkDxomPc"
                   "%3D",
    "register_post": "http://api.applezhuan.com/api/c/register?&s=OwBjPvLckT4biOj%2Br3j8KSXu67DrVYjG7"
                     "%2BenFspMJKPIZgDwh10K2f%2BylDHgQxWxfasmNy9Oh5aW2FPq%2F5cekX%2FPFPa9%2FgQIrn6puv1"
                     "%2FTyiRpHvlGfA8umOCyuB3IKv%2FAD1oEQhrDDm8pjLvCef2d8EW00z3E"
                     "%2F4rYAFzPJS9ZWhDDhiorCLwKTc5deUgqEG91OUWzLJVdcEjxr7"
                     "%2F5BuuPOX7kknzhl8hcOhts3gGQmQSRlSOOsRPhCTBqeVHIkVs%2FzmcOGiiHUJ9n44vBZOjj0YiefYYBG94e"
                     "%2F6BoViwpC9AskDUnm%2F0dZZ3HPMyxvd%2BgqppcHBYZ%2Bi5VHt7"
                     "%2Fq6od2NQQ4GRiOqYWb7OacXP4oXyLP2WFudeW3zqQmhCx%2FkDDZCd6JugKDPm%2FR9gRCoBig%3D%3D",
    "get_user_info1": "http://api.applezhuan.com/api/c/get_userinfo?&s"
                     "=nAUNfbXWkuYGTlZOyncFR584MgXiasHooBH8RVz1GJqmg8Imymg0l2srp%2FmlnAKexQoZ4bvbeUk7gXtO"
                     "%2BA0hQu7HDzjfAglh5w1ARdGCUirpFuY%2BAKvdrlY"
                     "%2BBEKltGJOzpeKsCIVUanLpzVvByXsArUQsywuJcu6ssQK6lwNEc3E1AXpmv%2Be80JDn"
                     "%2BZz5lB4ICOfmmNFAbJnnkhFtuzMZ0Z65g2nEJ6oMiHulYow37SSNEyah8n"
                     "%2Bxghv6sW2XMEi2YswsO9MtoW5nkC25tBNJlf2%2BuL2sPJLj12ytNfIMSDeY9K7Ao8MZtYNz33eYTY7Ino4MrFh92I"
                     "%2BE3UysuyQThSeUsZlVUEmfIkWuuvv%2B50S7aoNld4HAVGTjESI1rdYUCOHD%2BM5b%2F5IZ2jODGQugo9lSOiYrDRQ"
                     "%2BuQz8zM8DMJxpx2JJBZwbqRdIarIdQ00SFZqjHfdZ1pC9%2Fo9AYxmWA8lydGcxflomPEjDcGPj6"
                     "%2Bk9dqMSRlGFZYn9VXmcbCtsg1DrssELSNx7ZNuMCEin1aW674FJiqJGi1%2BoY6dIpw%3D "
}


def test_run(mobile_num="17184084074"):
    # mobile_num =
    mobile = Mobile(mobile_num)
    ktt = KTT(mobile)
    # 0. get cookie
    ktt.gen_device_code()
    ktt.get_api_start()
    # 1. login
    time.sleep(3)
    ktt.post_login()
    # 2. get_user_info
    time.sleep(3)
    ktt.get_user_info()
    print(ktt.user_info)
    # 3. get_task_center
    print("task_status:")
    time.sleep(3)
    task_center_status = ktt.post_task_center_status()
    print("task_center_status")
    print(task_center_status)
    if task_center_status["new_task_status"] == 0:
        time.sleep(3)
        task_status = ktt.get_task_status()
        print(task_status["status"])
        if task_status["status"][0] == 0:
            time.sleep(3)
            new_task_result = ktt.post_task_commit_new()
            print("new_task_result:")
            print(new_task_result)

    if task_center_status["invite_task_status"] == 0:
        time.sleep(3)
        ktt.post_task_commit_invite("20833")
    # 4. sign
    print("task sign")
    time.sleep(3)
    is_sign = ktt.get_sign_status()
    if is_sign == 0:
        time.sleep(3)
        ktt.get_sign()
    else:
        print("has signed")
    # 5. packet
    print("packet")
    time.sleep(3)
    count_down = ktt.get_timing_packet()
    print("count_down: %d" % count_down)
    if count_down == 0:
        time.sleep(3)
        ktt.post_packet()
    # 6. get list

    time.sleep(3)
    art_list = ktt.get_list()
    while art_list["total"] == 0:
        time.sleep(3)
        art_list = ktt.get_list()
    print("art total: %d" % art_list["total"])
    print("art len: %d" % art_list["num"])
    print(art_list["list"][0])
    print(art_list["list"][0]["id"])
    art_id = art_list["list"][0]["id"]
    # 7. get content
    print("get content")
    time.sleep(3)
    res_data = ktt.get_content(art_id)
    print(res_data)
    time.sleep(1)
    res_data = ktt.get_content_by_id(art_id)
    print(res_data)

    # 8. get reward
    print("get reward")
    time.sleep(3)
    res_data = ktt.get_article_reward(art_id)
    print(res_data)
    print("hello")

def test_update_user():
    token = "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ5MzU0MTE4NCwiaWF0IjoxNDkwOTQ5MTg0fQ.eyJpYXQiOjE0OTA5NDkxODQsInVpZCI6MjY0NjN9.RYKPgvX_3MDEBKqifLpG3bo7kLoTwy0G1DlceigfwtA"
    # session = ""
    # lon=0.0&time=1490976061&vn=1.0.2&mac=24:00:ba:75:3d:91&cid=1&content_type=1,3,4,5&av=2&
    # network=WIFI&platform=2&brand=HONOR&device_code=0000000076f574c7fffffffff6e65fd7&
    # ov=5.1.1&device_name=huawei&page=1&lat=0.0&android_id=HONORKIW-TL00H
    mobile = Mobile("13288250180")
    mobile.mac = "24:00:ba:75:3d:91"
    mobile.brand = "HONOR"
    mobile.ov = "5.1.1"
    mobile.android_id = "HONORKIW-TL00H"
    mobile.device_name = "huawei"
    ktt = KTT(mobile)
    ktt.device_code = "0000000076f574c7fffffffff6e65fd7"
    ktt.get_api_start()
    ktt.token = token
    ktt.cookie += token

    ktt.post_update_user_info()


def main():
    # mobile_num = test_start()
    # test_show_default_channel_list()
    # test_decrypt_one("getlist2")
    # test_decrypt_one("update_user")
    # print("mobile_num: %s" % mobile_num)
    # time.sleep(20)
    # if mobile_num:
    test_run()
    # test_show_guest_info()
    # test_orc()
    # test_update_user()

if "__main__" == __name__:
    main()