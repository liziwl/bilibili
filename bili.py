import random
import threading
from functools import namedtuple
from concurrent import futures
import time as ti
import csv
import requests
from lxml import etree
import re

# 不要轻易改小sleep数值，否则会被封IP。
# 有些视频需要登陆才能查看，所以在basic_info里播放量会为"--"。

basic_header = ["aid", "view", "danmaku", "reply", "favorite", "coin", "share", "tag_attention"]
detail_header = ["aid", "title", "category", "date", "duration", "upid"]
up_header = ["mid", "name", "fans", "video"]

Video = namedtuple('Video', basic_header)
Video_detail = namedtuple('Video_detail', detail_header)
Up_detail = namedtuple('up_detail', up_header)

headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/56.0.2924.87 Safari/537.36'
}
total = 1
detail_total = 1
up_total = 1

result = []
detail_result = []
up_result = []

lock = threading.Lock()


def basic_info(url):
    """
    抓取视频编号，播放量，弹幕数，评论数，收藏数，硬币数，分享数
    :param url: 网址
    """
    global total
    ti.sleep(1)  # 延迟，避免太快 ip 被封
    req = requests.get(url, headers=headers, timeout=6).json()
    ti.sleep(1)  # 延迟，避免太快 ip 被封
    av = url.replace("http://api.bilibili.com/archive_stat/stat?aid=", "")
    tag_url = "https://api.bilibili.com/x/tag/archive/tags?aid=" + str(av)
    tag_req = requests.get(tag_url, headers=headers, timeout=6).json()
    try:
        data = req['data']
        total_tag_atten = 0
        tag_data = tag_req['data']
        for i in range(0, len(tag_data)):
            total_tag_atten += tag_data[i]['count']['atten']

        video = Video(
            data['aid'],  # 视频编号
            data['view'],  # 播放量
            data['danmaku'],  # 弹幕数
            data['reply'],  # 评论数
            data['favorite'],  # 收藏数
            data['coin'],  # 硬币数
            data['share'],  # 分享数
            total_tag_atten  # 标签总关注数
        )

        with lock:
            result.append(video)
            print(total)
            total += 1
    except:
        pass


def up_info(url):
    """
    抓取up名称，粉丝数，投稿数
    :param url: 网址
    """
    global up_total
    ti.sleep(1)  # 延迟，避免太快 ip 被封
    req = requests.get(url, headers=headers, timeout=6).json()
    try:
        data = req['data']
        card = data['card']
        mid = card['mid']
        name = card['name']
        fans = card['fans']
        url_de = "https://api.bilibili.com/x/space/navnum?mid=" + str(mid)
        ti.sleep(1)  # 延迟，避免太快 ip 被封
        req_de = requests.get(url_de, headers=headers, timeout=6).json()
        data = req_de['data']
        video = data['video']

        tmp = Up_detail(mid, name, fans, video)
        with lock:
            up_result.append(tmp)
            print(up_total)
            up_total += 1
    except:
        pass


def detailed_info(url):
    """
    抓取视频标题，上传时间，视频类型，视频标签，时长
    :param url: 网址
    """
    global detail_total
    ti.sleep(1)
    html = requests.get(url, headers=headers, timeout=6)
    selector = etree.HTML(html.text)
    content = selector.xpath("//html")
    for each in content:
        title = each.xpath('//div[@class="v-title"]/h1/@title')
        if title:  # 如果有这个视频，即非404
            title = title[0]
            av = url.replace("http://bilibili.com/video/av", "")
            tminfo1_log = each.xpath('//div[@class="tminfo"]/a/text()')
            tminfo2_log = each.xpath('//div[@class="tminfo"]/span[1]/a/text()')
            tminfo3_log = each.xpath('//div[@class="tminfo"]/span[2]/a/text()')
            if tminfo1_log:
                tminfo1 = tminfo1_log[0]
            else:
                tminfo1 = ""
            if tminfo2_log:
                tminfo2 = tminfo2_log[0]
            else:
                tminfo2 = ""
            if tminfo3_log:
                tminfo3 = tminfo3_log[0]
            else:
                tminfo3 = ""
            tminfo = tminfo1 + '-' + tminfo2 + '-' + tminfo3
            time_log = each.xpath('//div[@class="tminfo"]/time/i/text()')
            mid_log = each.xpath('//div[@class="b-btn f hide"]/@mid')
            if time_log:
                time = time_log[0]
            else:
                time = ""
            if mid_log:
                mid = mid_log[0]
            else:
                mid = ""
            cid_html_1 = each.xpath('//div[@class="scontent"]/iframe/@src')
            cid_html_2 = each.xpath('//div[@class="scontent"]/script/text()')
            if cid_html_1 or cid_html_2:
                if cid_html_1:
                    cid_html = cid_html_1[0]
                else:
                    cid_html = cid_html_2[0]

                cids = re.findall(r'cid=.+&aid', cid_html)
                cid = cids[0].replace("cid=", "").replace("&aid", "")
                info_url = "http://interface.bilibili.com/player?id=cid:" + str(cid) + "&aid=" + av
                ti.sleep(1)
                video_info = requests.get(info_url, headers=headers, timeout=6)
                video_selector = etree.HTML(video_info.text)
                for video_each in video_selector:
                    duration_log = video_each.xpath('//duration/text()')
                    if duration_log:
                        duration = duration_log[0]
                    else:
                        duration = ""
    print(av, title, tminfo, time, duration, mid)
    tmp = Video_detail(av, title, tminfo, time, duration, mid)

    with lock:
        detail_result.append(tmp)
        print(detail_total)
        detail_total += 1


def save(file_name, header, result):
    """
    将数据保存至本地
    :param header: 请求头
    :param result: 结果
    """
    file = file_name + ".csv"
    with open(file, "w", encoding="utf_8_sig", newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(result)


def generate_url(from_num, to_num, size):
    ra = random.sample(range(from_num, to_num), size)
    out = []
    out_detail = []
    for i in ra:
        url = "http://api.bilibili.com/archive_stat/stat?aid={}".format(i)
        detail_url = "http://bilibili.com/video/av{}".format(i)
        out.append(url)
        out_detail.append(detail_url)
    return out, out_detail


def get_mid(file):
    mid = []
    with open(file, encoding="utf_8_sig") as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for row in f_csv:
            mid.append(row[5])
            # print(row[5])
    return mid


def generate_mid_url(mids):
    out = []
    for i in mids:
        url = "https://api.bilibili.com/cardrich?mid={}".format(i)
        out.append(url)
    return out


if __name__ == "__main__":
    pass
    # ------------------------------------------------
    # 第一次运行这一部分，随机采样数据，生成2个csv文件。
    # ------------------------------------------------

    # urls, detail_url = generate_url(14035440, 14950778, 4000)
    # with futures.ThreadPoolExecutor(32) as executor:
    #     executor.map(basic_info, urls)
    # print(result)
    # save("basic_info", basic_header, result)
    #
    # with futures.ThreadPoolExecutor(32) as executor:
    #     executor.map(detailed_info, detail_url)
    # print(detail_result)
    # save("detail_info", detail_header, detail_result)

    # -----------------------------------------------------
    # 第二次运行这一部分，根据上面采样出的视频找up的数据
    # ------------------------------------------------

    # mid = get_mid("detail_info.csv")
    # mid_url = generate_mid_url(mid)
    #
    # with futures.ThreadPoolExecutor(32) as executor:
    #     executor.map(up_info, mid_url)
    # print(up_result)
    # save("up_info", up_header, up_result)
