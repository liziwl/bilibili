import codecs
import random
import threading
from functools import namedtuple
from concurrent import futures
import time as ti
import csv
import requests
from lxml import etree
import re

# TODO 速度还是快了，会被封ip

basic_header = ["aid", "view", "danmaku", "reply", "favorite", "coin", "share"]
detail_header = ["aid", "title", "category", "date", "duration", "upid"]
Video = namedtuple('Video', basic_header)
Video_detail = namedtuple('Video_detail', detail_header)
headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/56.0.2924.87 Safari/537.36'
}
total = 1
detail_total = 1
result = []
detail_result = []
lock = threading.Lock()

def basic_info(url):
    """
    抓取视频编号，播放量，弹幕数，评论数，收藏数，硬币数，分享数
    :param url: 网址
    :return:
    """
    global total
    ti.sleep(0.5)  # 延迟，避免太快 ip 被封
    req = requests.get(url, headers=headers, timeout=6).json()
    try:
        data = req['data']
        video = Video(
            data['aid'],  # 视频编号
            data['view'],  # 播放量
            data['danmaku'],  # 弹幕数
            data['reply'],  # 评论数
            data['favorite'],  # 收藏数
            data['coin'],  # 硬币数
            data['share']  # 分享数
        )
        with lock:
            result.append(video)
            print(total)
            total += 1
    except:
        pass


def detailed_info(url):
    """
    抓取视频标题，上传时间，视频类型，视频标签，时长
    :param url: 网址
    :return:
    """
    global detail_total
    ti.sleep(0.5)
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
                ti.sleep(0.5)
                video_info = requests.get(info_url)
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


def generate_url(to_num, size):
    ra = random.sample(range(1, to_num), size)
    out = []
    out_detail = []
    for i in ra:
        url = "http://api.bilibili.com/archive_stat/stat?aid={}".format(i)
        detail_url = "http://bilibili.com/video/av{}".format(i)
        out.append(url)
        out_detail.append(detail_url)
    return out, out_detail


if __name__ == "__main__":
    urls, detail_url = generate_url(17000000, 3000)
    with futures.ThreadPoolExecutor(32) as executor:
        executor.map(basic_info, urls)
        executor.map(detailed_info, detail_url)
    print(result)
    save("basic_info", basic_header, result)
    print(detail_result)
    save("detail_info", detail_header, detail_result)
