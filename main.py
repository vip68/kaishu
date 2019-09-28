#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
博客：
    http://v88v.cnblogs.com

简介：
    KS数据爬取

"""

import sys
import time

if __name__ == '__main__':
    start_time = time.time()

    if len(sys.argv) < 2:
        print('请指定要操作的类型，c：分类，k：小知识，d：下载')
        sys.exit()

    if sys.argv[1].lower() == 'c':
        from scripts import KaishuCategory

        category_obj = KaishuCategory(
            data_dir='data/凯叔故事', is_fake=True, dl_voice=True, dl_html=True, dl_bg=True, dl_types=[
                'html', 'voice', 'bg', ])
        category_obj.do_action()

    elif sys.argv[1].lower() == 'k':
        from scripts import KaishuKnowledge

        know_obj = KaishuKnowledge(
            data_dir='data/凯叔小知识', is_fake=False, dl_voice=True, dl_html=True, dl_types=['html', 'voice', ], days=6)
        know_obj.do_action()

    elif sys.argv[1].lower() == 'd':
        print('此功能已停用')
        # from scripts import KaishuDownloader
        #
        # downloader = KaishuDownloader()
        # downloader.download_voices('info-20190925215058.json')
        # print('下载文件总数：%d' % downloader.count)
        # delete_gap_dir('凯叔故事')

    else:
        print('请指定要操作的类型，c：分类，k：小知识，d：下载')
        sys.exit()

    duration = time.time() - start_time
    m, s = divmod(duration, 60)

    print('==================================================')
    print('### 运行完毕，用时：%02d 分 %02d 秒 ###' % (m, s))
