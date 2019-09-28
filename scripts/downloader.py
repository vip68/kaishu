import os
import json
from .utils import make_dirs
from .base import KaishuBase


class KaishuDownloader(KaishuBase):
    """凯叔下载器"""

    def __init__(self, **kwargs):
        super(KaishuDownloader, self).__init__(**kwargs)
        # 根目录
        self.data_dir = kwargs.get('data_dir', 'data/凯叔故事')

    def download_voices(self, json_path):
        """
        下载音频资源
        :param json_path:
        :return:
        """
        with open(json_path, 'r') as f:
            data_list = json.load(f)

        for data in data_list:
            # if data['category'] == '凯叔推荐':
            for items in data['child']:
                # if items['category'] == '社交力':
                for item in items['child']:
                    # if item['product_name'] == '凯叔365夜':
                    file_dir = os.path.join(self.data_dir, data['category'], items['category'], item['product_name'])
                    product = item['module']
                    if len(product) > 0:
                        self.download_module(product, file_dir)

                    product = item['product']
                    if len(product) > 0:
                        self.download_outer(product, file_dir)

    def download_module(self, product, file_dir):
        """
        下载模块内容
        :param product:
        :param file_dir:
        :return:
        """
        for index, data in enumerate(product, 1):
            target_dir = os.path.join(file_dir, '%s(%s)' % (os.path.basename(file_dir), '{:0>2}'.format(index)))
            make_dirs(target_dir)
            if self.is_fake is False:
                self.download_bg(data['bgurl'], target_dir)
            self.download_product(data['child'], target_dir)

    def download_bg(self, bg_url, file_dir):
        """
        下载背景图
        :param bg_url:
        :param file_dir:
        :return:
        """
        if not bg_url:
            return

        try:
            resp = self.sess.get(url=bg_url)
            suffix = os.path.splitext(bg_url)[-1]
            filename = '00.%s%s' % (os.path.basename(file_dir), suffix)
            filepath = os.path.join(file_dir, filename)
            print(filepath)

            with open(filepath, 'wb') as f:
                f.write(resp.content)
        except Exception as e:
            print(e)

    def download_outer(self, product, file_dir):
        """
        外部下载
        :param product:
        :param file_dir:
        :return:
        """
        if product[0].get('product_name'):
            for item in product:
                cur_dir = os.path.join(file_dir, item['product_name'])
                make_dirs(cur_dir)
                product = item['module']
                if len(product) > 0:
                    self.download_module(product, cur_dir)

                product = item['product']
                if len(product) > 0:
                    self.download_product(product, cur_dir)
        else:
            make_dirs(file_dir)
            self.download_product(product, file_dir)

    def download_product(self, product, file_dir):
        """
        下载
        :param product:
        :param file_dir:
        :return:
        """
        for file_data in product:
            try:
                voice_url = file_data['voice_url']
                suffix = os.path.splitext(voice_url)
                filename = os.path.join(file_dir, '%s%s' % (file_data['story_name'], suffix[-1]))
                print(filename)

                if self.is_fake is False:
                    resp = self.sess.get(voice_url)
                    with open(filename, 'wb') as f:
                        f.write(resp.content)
                else:
                    with open(filename, 'w') as f:
                        f.write('')

                if self.dl_html is True and file_data.get('article'):
                    filename = os.path.join(file_dir, '%s.html' % file_data['story_name'])
                    html = '<!DOCTYPE html><html lang="zh-cn"></html><body>%s</body></html>' % file_data['article']
                    with open(filename, 'w') as f:
                        f.write(html)

                self.count += 1

            except Exception as e:
                print(e)
