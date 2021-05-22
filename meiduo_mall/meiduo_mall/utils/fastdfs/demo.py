from fdfs_client.client import Fdfs_client

if __name__ == '__main__':
    # 创建连接对象
    client = Fdfs_client('client.conf')
    # 上传文件
    ret = client.upload_by_filename('/Users/ws/Desktop/1.jpg')
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