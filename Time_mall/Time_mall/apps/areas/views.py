import logging

from django import http
from django.shortcuts import render
from django.views import View
from django.core.cache import cache

from areas.models import Areas

logger = logging.getLogger('django')

class AreasView(View):
    def get(self,request):
        '''
        省市区
        :param request:
        :return:
        '''
        #重构省市区结构
        areas_id = request.GET.get('areas_id')
        if not areas_id:
            # #将省份进行缓存到redis 0号库
            # province_list = cache.get("province_list")
            # #不存在就加入缓存中
            # if not province_list:
            try:#省为一级，没有父级id
                #获取省份  parent_id为null
                provinces = Areas.objects.filter(parent_id__isnull=True).values('id', 'name')
                province_list = []
                #序列化，保存到列表内
                for province in provinces:
                    province_list.append(province)
                return http.JsonResponse({"code": "0", "errmsg": "ok", "province_list": province_list})
            except Exception as e:
                logger.error(e)
                return http.HttpResponseForbidden("获取省份数据失败")
            # cache.set("province_list", province_list, 10)
                # 返回前端
        # print("province_list=",province_list)
        # return http.JsonResponse({"code": "0", "errmsg": "ok", "province_list": province_list})
        else:
            # sub_city_list = cache.get("sub_city_list")
            # if not sub_city_list:
            try:#根据响应第几级id获取下级管辖区
                #获取当前选中的地区对象
                province_obj = Areas.objects.get(id=areas_id)
                #通过related_name查找所有的下级地区
                sub_cities = province_obj.subs.all().values("id","name")
                sub_city_list = []
                for sub_city in sub_cities:
                    sub_city_list.append(sub_city)
                return http.JsonResponse({"code": "0", "errmsg": "ok", "sub_city_list": sub_city_list})
            except Exception as e:
                logger.error(e)
                return http.HttpResponseForbidden("获取省份下级地区数据失败")
            # cache.set("sub_city_list", sub_city_list, 10)
            # print("sub_city_list=", sub_city_list)
            # return http.JsonResponse({"code": "0", "errmsg": "ok", "sub_city_list": sub_city_list})