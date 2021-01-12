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


def get_videos(oldest_date):
    # Page number to start
    page_num = 22
    page_size = 22
    stop = False

    while not stop and page_num <= page_size:

        logger.info('https://api.bilibili.com/x/web-interface/newlist?rid=%s&pn=%s&ps=%s', 126, page_num, 50)
        response = requests.get('https://api.bilibili.com/x/web-interface/newlist',
                                {'rid': '126', 'pn': page_num, 'ps': 50}).json()

        videos = []

        # Update page size
        page_size = response['data']['page']['count'] / response['data']['page']['size']

        # Response data
        result = response['data']['archives']

        for video in result:
            videos.append(video)

            # Filter by public date
            # if video['pubdate'] > oldest_date:
            #     videos.append(video)
            # else:
            #     stop = True

        details = get_video_details(videos)

        # Dump to json file by timestamp
        with open('json/%s.json' % datetime.datetime.now().timestamp(), "w", encoding='utf-8') as outfile:
            json.dump(details, outfile, ensure_ascii=False)

        logger.info('Page: %s success!', page_num)
        page_num += 1
        time.sleep(0.5)


def get_video_details(videos):
    details = []

    for video in videos:
        stat = video['stat']
        owner = video['owner']

        logger.info('http://api.bilibili.com/x/relation/stat?vmid=%s', owner['mid'])
        user_stat = requests.get('http://api.bilibili.com/x/relation/stat', {'vmid': owner['mid']}).json()

        logger.info('http://api.bilibili.com/x/tag/archive/tags?aid=%s', video['aid'])
        tags = requests.get('http://api.bilibili.com/x/tag/archive/tags', {'aid': video['aid']}).json()

        time.sleep(1)

        details.append({
            'URL': 'https://www.bilibili.com/video/av%s' % video['aid'],
            'Title': video['title'],
            'Upload date': datetime.datetime.fromtimestamp(video['pubdate']).strftime('%m/%d/%Y'),
            'Play': stat['view'],
            'Uploader': owner['name'],
            'Fans': user_stat['data']['following'],
            'Description': video['desc'],
            'Tag': ','.join([item['tag_name'] for item in tags['data']]),
            'Danmaku': stat['danmaku'],
            'Like': stat['like'],
            'Coin': stat['coin'],
            'Favorite': stat['favorite'],
            'Forward': stat['share'],
            'Reply': stat['reply']
        })

    return details


if __name__ == '__main__':
    get_videos(datetime.datetime(2019, 1, 1).timestamp())
