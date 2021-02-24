from fdfs_client.client import Fdfs_client
client = Fdfs_client('./client.conf')
ret = client.upload_by_filename('./1.png')
print(ret)