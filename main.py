import datetime
import logging
import sys
import time

import requests

import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

column = False


def get_videos(keyword):
    # Page number to start
    page_num = 25
    page_size = 25
    stop = False

    while not stop and page_num <= page_size:
        logger.info('http://api.bilibili.com/x/web-interface/search/type?search_type=%s&keyword=%s&page=%s', 'video',
                    keyword, page_num)
        response = requests.get('http://api.bilibili.com/x/web-interface/search/type',
                                {'search_type': 'video', 'keyword': keyword, 'page': page_num}).json()

        # Update page size
        page_size = response['data']['numPages']
        if page_num == 1:
            logger.info('Page size: %s', page_size)

        # Response data
        videos = response['data']['result']

        # for video in result:
        #     # Filter by public date
        #     if video['pubdate'] > oldest_date:
        #         videos.append(video)
        #     else:
        #         stop = True

        details = get_video_details(videos, page_num)

        # Dump to json file by timestamp
        with open('json/%s%s.json' % (keyword, page_num), "w", encoding='utf-8') as outfile:
            json.dump(details, outfile, ensure_ascii=False)

        with open('following.json', 'w', encoding='utf-8') as f:
            json.dump(following, f, ensure_ascii=False)

        logger.info('Page: %s success!', page_num)
        page_num += 1
        time.sleep(0.5)


# def get_danmaku(aid):
#     logger.info('http://api.bilibili.com/x/web-interface/view?aid=%s' % aid)
#     cid = requests.get('http://api.bilibili.com/x/web-interface/view', {'aid': aid}).json()['data']['cid']
#
#     logger.info('https://comment.bilibili.com/%s.xml' % cid)
#     res = requests.get('https://comment.bilibili.com/%s.xml' % cid).content.decode('utf-8')
#
#     time.sleep(0.5)
#
#     root = ElementTree.fromstring(res)
#     return [d.text for d in root.findall('d')]

following = {}


def get_video_details(videos, page_num):
    details = []

    for video in videos:
        logger.info('http://api.bilibili.com/archive_stat/stat?aid=%s', video['aid'])
        stat = requests.get('http://api.bilibili.com/archive_stat/stat', {'aid': video['aid']}).json()['data']

        if video['mid'] not in following:
            logger.info('%s[%s] not in the cache, http://api.bilibili.com/x/relation/stat?vmid=%s', video['author'],
                        video['mid'], video['mid'])
            user_stat = requests.get('http://api.bilibili.com/x/relation/stat', {'vmid': video['mid']}).json()
            following[video['mid']] = user_stat['data']['following']
        else:
            logger.info('%s[%s] in the cache, skip to fetch', video['author'], video['mid'])

        time.sleep(1)

        details.append({
            'URL': 'https://www.bilibili.com/video/av%s' % video['aid'],
            'Title': video['title'].replace('<em class=\"keyword\">', '').replace('</em>', ''),
            'Upload date': datetime.datetime.fromtimestamp(video['pubdate']).strftime('%m/%d/%Y'),
            'Play': stat['view'],
            'Uploader': video['author'],
            'Fans': following[video['mid']],
            'Description': video['description'],
            'Tag': video['tag'],
            'Danmaku': stat['danmaku'],
            'Like': stat['like'],
            'Coin': stat['coin'],
            'Favorite': stat['favorite'],
            'Forward': stat['share'],
            'Reply': stat['reply'],
            'Page Num': page_num
            # 'Comments': get_danmaku(video['aid'])
        })

    return details


if __name__ == '__main__':
    logger.info('Read following.json')
    with open('following.json', 'r', encoding='utf-8') as f:
        following = json.load(f)

    keywords = [
        '鬼畜+人力VOCALOID+罗翔',
        '鬼畜+人力VOCALOID+特朗普',
        '鬼畜+人力VOCALOID+马云',
        '鬼畜+人力VOCALOID+马化腾',
        '鬼畜+人力VOCALOID+亮剑',
        '鬼畜+人力VOCALOID+诸葛亮'
    ]
    for keyword in keywords:
        get_videos(keyword)
