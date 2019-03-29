#!/usr/bin/env python
"""Provides de download_videos function.

download_videos holds a directory path and a file path with the list of URLs and save all videos of the
"""

import os
import argparse
import urllib3.request

__author__ = "jssprz"
__version__ = "0.0.1"
__maintainer__ = "jssprz"
__email__ = "jperezmartin90@gmail.com"
__status__ = "Development"


def download_and_process_video(save_dir_path, video_name, video_url):
    full_path = os.path.join(save_dir_path, video_name)

    if os.path.exists(full_path):
        return 1

    http = urllib3.PoolManager()
    r = http.request('GET', video_url, preload_content=False)

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


def download_videos(save_dir_path, list_file_path):
    with open(list_file_path) as f:
        lines = f.readlines()
        video_data = [{"video_id": data[0], "url": data[1], "video_path": "video%s.avi" % data[0]} for data in
                      (x.split() for x in lines)]
    print('videos to download: {}'.format(len(video_data)))

    downloads_count = 0
    errors_count = 0
    for row in video_data:
        result = download_and_process_video(save_dir_path, row['video_id'] + '.avi', row['url'])
        if result == 0:
            downloads_count += 1
        elif result == 2:
            errors_count += 1
            print('ERROR downloading for {}'.format(row['video_id']))

    print('Downloaded videos: {}\nTOTAL ERRORS: {}'.format(downloads_count, errors_count))


if __name__ == 'main':
    parser = argparse.ArgumentParser(description='Download the videos from a urls.')
    parser.add_argument('-save_dir_path', '--save', type=str, default='videos',
                        help='the path of the folder to save the downloaded videos (default is videos).')
    parser.add_argument('-list_file_path', '--file', type=str, default='videos_urls.txt',
                        help='the path of the file with the list of urls to downloaded (default is videos_urls.txt).')

    args = parser.parse_args()

    download_videos(args.save_dir_path, args.list_file_path)
