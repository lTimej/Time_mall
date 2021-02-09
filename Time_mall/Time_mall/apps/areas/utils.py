import logging

from areas.models import AreasModel

from django import http

logger = logging.getLogger('django')

# def refactor_areas():
#     try:
#         provinces = AreasModel.objects.filter(parent_id__isnull=True).values('id','name')
#         dic = {}
#         province_list = []
#         for province in provinces:
#             province_list.append(province)
#         dic['province_list'] = province_list
#         return dic
#     except Exception as e:
#         logger.error(e)
#         return http.HttpResponseForbidden("获取省份数据失败")
#     # dic['code'] = '0'
#     # dic['errmsg'] = 'ok'
