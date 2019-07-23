#!/usr/bin/env python
"""Provides the download_videos function.
download_videos holds a directory path and a file path with the list of URLs and save all videos of the
"""

import os
import argparse
import logging
import urllib3.request

__author__ = "jssprz"
__version__ = "0.0.1"
__maintainer__ = "jssprz"
__email__ = "jperezmartin90@gmail.com"
__status__ = "Development"


def download_and_process_video(save_dir_path, video_name, video_url, user, password):
    full_path = os.path.join(save_dir_path, video_name)

    if os.path.exists(full_path):
        return 1

    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth='{}:{}'.format(user, password))
    r = http.request('GET', video_url, headers=headers, preload_content=False)

    if r.status >= 300:
        return 2

    with open(full_path, 'wb') as out:
        while True:
            data = r.read()
            if not data:
                break
            out.write(data)

    r.release_conn()

    return 0


def download_videos(save_dir_path, list_file_path, user, password):
    with open(list_file_path) as f:
        lines = f.readlines()
        video_data = [{"video_id": data[0], "url": data[1], "video_format": "{}".format(data[1].split('.')[-1])} for data in
                      (x.split() for x in lines)]
    logging.info('videos to download: {}'.format(len(video_data)))

    downloads_count = 0
    errors_count = 0
    for row in video_data:
        result = download_and_process_video(save_dir_path,
                                            '{}.{}'.format(row['video_id'], row['video_format']),
                                            row['url'], user, password)
        if result == 0:
            downloads_count += 1
        elif result == 2:
            errors_count += 1
            logging.error('ERROR downloading for {}'.format(row['video_id']))

    logging.info('Downloaded videos: {}\nTOTAL ERRORS: {}'.format(downloads_count, errors_count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download the videos from a urls.')
    parser.add_argument('-save', '--save_dir_path', type=str, default='videos',
                        help='the path of the folder to save the downloaded videos (default is videos).')
    parser.add_argument('-file', '--list_file_path', type=str, default='videos_urls.txt',
                        help='the path of the file with the list of urls to downloaded (default is videos_urls.txt).')
    parser.add_argument('-u', '--user', type=str, help='the trecvid userid (required for Flickr videos).')
    parser.add_argument('-p', '--password', type=str, help='the trecvid password (required for Flickr videos).')

    args = parser.parse_args()

    logging.basicConfig(filename='./log/download',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    logging.info('path to save videos: {}'.format(args.save_dir_path))
    logging.info('file with the list of URLs: {}'.format(args.list_file_path))

    download_videos(args.save_dir_path, args.list_file_path, args.user, args.password)
