from django.conf import settings
from django.core.files.storage import Storage

class FastDFSStorage(Storage):
    """自定义文件存储类"""
    def __init__(self, fdfs_base_url=None):
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """
        打开文件时会被调用, 文档要求必须重写,
        :param name: 文件路径
        :param mode: 文件打开方式
        :return:
        """
        pass

    def _save(self, name, content):
        """
        保存文件时会被调用, 文档要求必须重写, 实现文件上传到FastDFS服务器
        :param name: 文件路径
        :param content: 文件二进制内容
        :return:
        """
        pass

    def url(self, name):
        """
        返回文件的全路径
        :param name: 文件相对路径
        :return: 文件的全路径(http://192.168.3.67:8888/group1/M00/00/01/CtM3BVrLmc-AJdVSAAEI5Wm7zaw8639396)
        """
        return self.fdfs_base_url + name