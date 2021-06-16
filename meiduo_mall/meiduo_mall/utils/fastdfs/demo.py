from fdfs_client.client import Fdfs_client, get_tracker_conf

from django.conf import settings

if __name__ == '__main__':
    import os
    if not os.getenv('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'
    # 创建连接对象
    tracker_path = get_tracker_conf(settings.FDFS_CLIENT_PATH)
    client = Fdfs_client(tracker_path)
    # 上传文件
    ret = client.upload_by_filename('/home/ws/Desktop/1.jpg')
    # 响应值
    print(ret)


'''
ret = '{
    'Group name': 'group1', 
    'Remote file_id': 'group1/M00/00/02/wKj6gmCoVkqAFTfyAAAPMxOaz8U730.jpg', 
    'Status': 'Upload successed.', 
    'Local file name': '/Users/ws/Desktop/1.jpg', 
    'Uploaded size': '3.00KB', 
    'Storage IP': '192.168.250.130'
}'
'''