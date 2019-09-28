import os
import time
from .utils import VERIFY, make_dirs
from .base import KaishuBase


class KaishuCategory(KaishuBase):
    """凯叔分类抓取"""

    def __init__(self, **kwargs):
        super(KaishuCategory, self).__init__(**kwargs)
        # 下载背景
        self.dl_bg = kwargs.get('dl_bg', True)
        # 根目录
        self.data_dir = kwargs.get('data_dir', 'data/凯叔故事')
        self.cate1 = kwargs.get('cate1')
        self.cate2 = kwargs.get('cate2')
        self.cate3 = kwargs.get('cate3')
        # self.cate3 = kwargs.get('cate3', ['凯叔·诗词来了 合集', ])

    def do_action(self):
        """
        执行操作
        :return:
        """
        items = self.get_category_data()

        for item in items:
            cate_data = {'id': item['id'], 'name': item['categoryName']}

            if self.cate1 is not None and item['categoryName'] not in self.cate1:
                continue

            self.get_children(cate_data, item['children'])

    def get_category_data(self):
        """
        获取分类数据
        :return:
        """
        url = 'https://api.kaishustory.com/category/new/list'
        resp = self.sess.get(url, verify=VERIFY).json()

        return resp['result']

    def get_children(self, p_data, items):
        """
        获取子节点
        :param p_data:
        :param items:
        :return:
        """
        for item in items:
            cate_data = {'id': item['id'], 'name': item['categoryName']}

            if self.cate2 is not None and item['categoryName'] not in self.cate2:
                continue

            data = self.get_playlists(item['id'])
            playlist = data['ablum']['list']
            self.get_all_products(p_data, cate_data, playlist)

    def get_playlists(self, category_id):
        """
        获取播放列表
        :param category_id:
        :return:
        """
        url = 'https://api.kaishustory.com/category/new/content/list'
        params = {
            'page_no': 1,
            'page_size': 9999,
            'feeType': '',
            'contentType': 'ablum',
            'categoryId': category_id,
            'tagType': 1,
        }
        resp = self.sess.get(url, params=params, verify=VERIFY).json()

        return resp['result']

    def get_all_products(self, p_data, c_data, playlist):
        """
        所有产品信息
        :param p_data:
        :param c_data:
        :param playlist:
        :return:
        """
        for item in playlist:
            try:
                if self.cate3 is not None and item['ablumname'] not in self.cate3:
                    continue

                g_data = {'id': item['ablumid'], 'name': item['ablumname'], }
                if item['feetype'] == '00':
                    # 免费
                    products = self.get_free_data(item['ablumid'])
                    if products is None:
                        continue

                    self.download_data('free', item['ablumid'], products, [p_data, c_data, g_data])
                else:
                    # 会员
                    products = self.select_method(item['product']['productid'], [p_data, c_data, g_data])
                    if products is None:
                        continue
            except Exception as e:
                print(e)

    def get_free_data(self, ablum_id):
        """
        获取免费数据
        :param ablum_id:
        :return:
        """
        url = 'https://api.kaishustory.com/ablumservice/findById'
        params = {
            'ablumid': ablum_id,
        }
        try:
            resp = self.sess.get(url, params=params, verify=VERIFY).json()

            return resp['result']['list']
        except Exception as e:
            print(e)

    def download_data(self, mode, product_id, data_list, tree_data):
        """
        下载数据
        :param mode:
        :param product_id:
        :param data_list:
        :param tree_data:
        :return:
        """
        file_dir = os.path.join(self.data_dir, *[data['name'] for data in tree_data])

        for index, data in enumerate(data_list, 1):
            if not data.get('storyname') or not data.get('voiceurl'):
                continue

            path = ' | '.join(['%d-%s' % (data['id'], data['name']) for data in tree_data])

            print('[%s] %d | %s | %d-%s | %d-%s | %d' % (
                time.strftime('%Y-%m-%d %H:%M:%S'), self.count, path, data['storyid'], data['storyname'], product_id,
                mode, index))

            story_name = data['storyname'].replace(
                '?', '？').replace(':', '：').replace('/', '：').replace('|', '：').replace('\t', ' ')
            story_name = '{:0>2}.{}'.format(index, story_name)

            if 'voice' in self.dl_types:
                self.download_voice(file_dir, story_name, data['voiceurl'])

            if 'html' in self.dl_types:
                content = self.get_article_content(data['storyid'], product_id, tree_data[-1]['id'])
                self.download_html(file_dir, story_name, content)

    def select_method(self, product_id, tree_data):
        """
        选择请求方法
        :param product_id:
        :param tree_data:
        :return:
        """
        pre_product = self.get_pre_product(product_id)
        product_list = pre_product['product']['childproductinfo'].get('list', [])

        products = self.get_product(product_id)
        if products.get('modulelistvalue'):
            self.get_module_list(product_id, products['modulelistvalue'], tree_data)

        elif len(product_list) > 0:
            for index, product in enumerate(product_list):
                if index > 0:
                    # 为了防止子目录内递归子目录
                    tree_data.pop(-1)
                tree_data.append({'id': product['productid'], 'name': product['productname']})
                self.select_method(product['productid'], tree_data)

        elif products.get('productlistvalue'):
            data_list = products['productlistvalue']['info']['list']
            self.download_data('product', product_id, data_list, tree_data)

        else:
            return None

        return products

    def get_pre_product(self, product_id):
        """
        准备产品前期数据
        :param product_id:
        :return:
        """
        url = 'https://api.kaishustory.com/product/detail'
        params = {
            'userid': self.user_id,
            'productid': product_id,
        }
        try:
            resp = self.sess.get(url, params=params, verify=VERIFY).json()

            return resp['result']
        except Exception as e:
            print(e)

    def get_product(self, product_id):
        """
        获取产品信息
        :param product_id:
        :return:
        """
        url = 'https://api.kaishustory.com/product/detail/storylist'
        params = {
            'userid': self.user_id,
            'page_no': 1,
            'page_size': 9999,
            'productid': product_id,
        }
        try:
            resp = self.sess.get(url, params=params, verify=VERIFY).json()

            return resp['result']
        except Exception as e:
            print(e)

    def get_module_list(self, product_id, product_list, tree_data):
        """
        获取模块下的信息
        :param product_id:
        :param product_list:
        :param tree_data:
        :return:
        """
        for index, pro_data in enumerate(product_list, 1):
            try:
                if index > 1:
                    tree_data.pop(-1)

                bg_url = pro_data['bgurl'] if pro_data['bgurlnew'] == '' else pro_data['bgurlnew']
                dirname = '%s(%s)' % (tree_data[-1]['name'], '{:0>2}'.format(index))
                file_dir = os.path.join(self.data_dir, *[data['name'] for data in tree_data], dirname)

                if 'bg' in self.dl_types:
                    self.download_bg(bg_url, file_dir)

                tree_data.append({'id': tree_data[-1]['id'], 'name': dirname})
                self.download_data('module', product_id, pro_data['list'], tree_data)
            except Exception as e:
                print(e)

    def get_voice_url(self, content_id):
        """
        获取音频地址
        :param content_id:
        :return:
        """
        url = 'https://api.kaishustory.com/hls/key/sts'
        params = {
            'userId': self.user_id,
            'contentId': content_id,
            'contentType': 'story',
            'downloadType': 1,
        }
        resp = self.sess.get(url, params=params, verify=VERIFY).json()

        return resp['result']

    def download_bg(self, bg_url, file_dir):
        """
        下载背景图
        :param bg_url:
        :param file_dir:
        :return:
        """
        if not bg_url or self.dl_bg is False:
            return

        try:
            self.count += 1
            resp = self.sess.get(url=bg_url)
            suffix = os.path.splitext(bg_url)[-1]
            filename = '00.%s%s' % (os.path.basename(file_dir), suffix)
            filepath = os.path.join(file_dir, filename)

            make_dirs(file_dir)

            if self.is_fake is False:
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
            else:
                with open(filepath, 'w') as f:
                    f.write('')
        except Exception as e:
            print(e)
