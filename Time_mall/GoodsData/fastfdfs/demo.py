# from fdfs_client.client import Fdfs_client
# client = Fdfs_client('./client.conf')
# ret = client.upload_by_filename('./1.png')
# print(ret)

#
# data = []
# for i in range(30):
#     data.append(i)
#
# dd = []
# for j in range(0,32,4):
#     d = [k for k in data[j:j+4]]
#     dd.append(d)
# print(dd)
d = dict()
d["d"] = 1
d["g"] = 2
d["a"] = 3
print(list(d.keys())[0])