from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from . import response_code

class MyLoginRequiredMixin(LoginRequiredMixin):
    """
    自定义用户未登录，返回未登录状态
    """
    def handle_no_permission(self):
        return http.JsonResponse({"code":response_code.RETCODE.SESSIONERR,"errmsg":"用户未登录"})



