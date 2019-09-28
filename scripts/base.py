import os
import requests
from .utils import VERIFY, make_dirs


class KaishuBase(object):
    """凯叔基类"""

    def __init__(self, **kwargs):
        # 模拟下载
        self.is_fake = kwargs.get('is_fake', False)
        # 下载文稿
        self.dl_html = kwargs.get('dl_html', True)
        # 下载音频
        self.dl_voice = kwargs.get('dl_voice', True)
        # 下载类型 ['html', 'voice', 'bg', ]
        self.dl_types = kwargs.get('dl_types', ['html', 'voice', 'bg', ])
        # 文件总数
        self.count = 1
        self.sess = requests.session()
        self.user_id = 103504910
        self.headers = {
            "content-type": "application/json; charset=UTF-8",
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5OTIwOTkwMDEiLCJpbCI6dHJ1ZSwiaXNzIjoia2Fpc2h1c3"
                     "RvcnkiLCJleHAiOjE1NzE5OTcyNDcsInVkIjoxMDM1MDQ5MTB9.ZPiRVo96fqSn4krvG9mYWjxsE214H_m394JrnH5webQ",
            "deviceid": "E60338EF0DE19F1A2E9A00E7F8FC4D49",
            "appversion": "6.1.2",
            "accept-encoding": "identity",
            "apiver": "2.4",
            "userid": str(self.user_id),
            "appid": "992099001",
            "channelid": "xiaomi",
            "clientform": "android",
            "usersource": "kaishu",
            "platform": "kaishu",
            "user-agent": "okhttp/3.12.1",
        }

    def download_voice(self, file_dir, filename, voice_url):
        """
        下载音频
        :param file_dir:
        :param filename:
        :param voice_url:
        :return:
        """
        if not voice_url or self.dl_voice is False:
            return

        make_dirs(file_dir)

        try:
            self.count += 1
            suffix = os.path.splitext(voice_url)
            filepath = os.path.join(file_dir, '%s%s' % (filename, suffix[-1]))

            if self.is_fake is False:
                resp = self.sess.get(voice_url)
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
            else:
                with open(filepath, 'w') as f:
                    f.write('')
        except Exception as e:
            print(e)

    def download_html(self, file_dir, filename, content):
        """
        下载页面
        :param file_dir:
        :param filename:
        :param content:
        :return:
        """
        if not content or self.dl_html is False:
            return

        self.count += 1
        make_dirs(file_dir)
        filepath = os.path.join(file_dir, '%s.html' % filename)

        if self.is_fake is False:
            html = '<!DOCTYPE html><html lang="zh-cn"></html><body>%s</body></html>' % content
            with open(filepath, 'w') as f:
                f.write(html)
        else:
            with open(filepath, 'w') as f:
                f.write('')

    def get_article_content(self, story_id, product_id, ablum_id):
        """
        获取文稿内容
        :param story_id:
        :param product_id:
        :param ablum_id:
        :return:
        """
        try:
            pre_data = self.get_pre_article(story_id, product_id, ablum_id)
            if pre_data['article']:
                article_data = self.get_article_data(pre_data['article']['articleid'])
                content = article_data['article']['content']
            else:
                content = ''
        except Exception as e:
            # print(e)
            content = ''

        return content

    def get_pre_article(self, story_id, product_id, ablum_id):
        """
        获取文稿信息
        :param story_id:
        :param product_id:
        :param ablum_id:
        :return:
        """
        resp = None
        url = 'https://api.kaishustory.com/storyservice/story/findbyid'
        params = {
            'id': story_id,
            'userid': self.user_id,
            'productid': product_id,
            'ablumid': ablum_id,
        }
        try:
            resp = self.sess.get(url, headers=self.headers, params=params, verify=VERIFY).json()

            return resp['result']
        except Exception as e:
            if resp.get('errmsg', ''):
                print(resp['errmsg'])
            else:
                print(e)

    def get_article_data(self, article_id):
        """
        获取文稿数据
        :param article_id:
        :return:
        """
        url = 'https://api.kaishustory.com/storyservice/article'
        params = {
            'articleid': article_id,
        }
        try:
            resp = self.sess.get(url, headers=self.headers, params=params, verify=VERIFY).json()

            return resp['result']
        except Exception as e:
            print(e)
