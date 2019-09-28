import os

VERIFY = True


def make_dirs(file_dir):
    """
    创建目录
    :param file_dir:
    :return:
    """
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)


def delete_gap_dir(gap_dir, del_hide=True):
    """
    移除空目录
    :param gap_dir:
    :param del_hide:
    :return:
    """
    if os.path.isdir(gap_dir):
        for d in os.listdir(gap_dir):
            delete_gap_dir(os.path.join(gap_dir, d))

        file_list = os.listdir(gap_dir)
        if len(file_list) == 0:
            os.rmdir(gap_dir)
            print('移除空目录: %s' % gap_dir)
        elif del_hide is True and len(file_list) == 1 and file_list[0].startswith('.'):
            os.rmdir(gap_dir)
            print('移除空目录: %s' % gap_dir)
