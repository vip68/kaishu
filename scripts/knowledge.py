import os
import time
import math
from .utils import VERIFY
from .base import KaishuBase


class KaishuKnowledge(KaishuBase):
    """凯叔小知识"""

    def __init__(self, **kwargs):
        super(KaishuKnowledge, self).__init__(**kwargs)
        # 根目录
        self.data_dir = kwargs.get('data_dir', 'data/凯叔小知识')
        # 模拟下载
        self.is_fake = kwargs.get('is_fake', False)
        # 下载文稿
        self.dl_html = kwargs.get('dl_html', False)
        # 下载音频
        self.dl_voice = kwargs.get('dl_voice', False)
        # 天数 0 为无限制，> 0 为指定天数
        self.days = kwargs.get('days', 0)
        # 每页条数，目前为固定值，请勿修改
        self.page_size = 10

    def do_action(self):
        """
        执行操作
        :return:
        """
        # 先请求一次，获取页码信息
        base_info = self.get_page_info(1)
        days = math.ceil(base_info['total_count']) if self.days == 0 else self.days
        self.get_all_data(days)

    def get_page_info(self, page_no):
        """
        获取指定页面信息
        :param page_no:
        :return:
        """
        url = 'https://api.kaishustory.com/column/content'
        params = {
            'userid': self.user_id,
            'columnid': 1,
            'page_no': page_no,
            'page_size': self.page_size,
            'order': 1,
        }
        try:
            resp = self.sess.get(url, headers=self.headers, params=params, verify=VERIFY).json()

            return resp['result']
        except Exception as e:
            print(e)

    def get_all_data(self, days):
        """
        获取所有数据
        :param days:
        :return:
        """
        page = math.ceil(days / self.page_size) + 1

        for i in range(1, page):
            data_list = self.get_page_info(i)
            if not data_list.get('list'):
                continue

            if page - i == 1 and days % self.page_size > 0:
                days_list = data_list['list'][:days % self.page_size]
            else:
                days_list = data_list['list']

            data_dict = self.get_everyday_data(days_list)
            for data in data_dict:
                file_dir = os.path.join(self.data_dir, data['sale_time'])
                self.download_data(file_dir, data)

    def get_everyday_data(self, data_list):
        """
        获取每日数据
        :param data_list:
        :return:
        """
        for day in data_list:
            data_dict = {
                'sale_time': day['saletime'],
                'child': []
            }
            for dt in day['list']:
                content = self.get_article_content(dt['story']['storyid'], '', '')
                data_dict['child'].append({
                    'story_name': dt['story']['storyname'],
                    'voice_url': dt['story']['voiceurl'],
                    'article': content,
                })

            yield data_dict

    def download_data(self, file_dir, data):
        """
        下载数据
        :param file_dir:
        :param data:
        :return:
        """
        for child_data in data['child']:
            print('[%s] %d | %s | %s' % (
                time.strftime('%Y-%m-%d %H:%M:%S'), self.count, data['sale_time'], child_data['story_name']))
            story_name = child_data['story_name'].replace(
                '?', '？').replace(':', '：').replace('/', '：').replace('|', '：').replace('\t', ' ')

            for dl_type in self.dl_types:
                if dl_type == 'html':
                    self.download_html(file_dir, story_name, child_data['article'])
                elif dl_type == 'voice':
                    self.download_voice(file_dir, story_name, child_data['voice_url'])
