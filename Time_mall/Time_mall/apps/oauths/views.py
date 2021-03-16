from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ

from Time_mall.utils.response_code import RETCODE


class QQLoginView(View):
    def get(self,request):
        '''获取Authorization Code
        https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=&redirect_uri=&state=
        :param request:
        :return:
        '''
        next = request.GET.get("next")
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url':login_url})
class QQcallBackView(View):
    def get(self,request):
        return http.HttpResponse("ok")