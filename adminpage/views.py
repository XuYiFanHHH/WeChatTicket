
import time
import datetime

from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User
from wechat.models import Activity
from wechat.models import Ticket

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


class Login(APIView):

    def get(self):
        """
        input:  无
                获取登录状态,已登录返回0,否则返回非0
        """
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        return

    def post(self):
        """
        input:  self.input['username'] -------- 管理员用户名
        input:  self.input['password'] -------- 管理员密码
        """
        user = authenticate(username=self.input['username'], password=self.input['password'])
        if user is not None:
            login(self.request, user)
            return
        else:
            raise ValidateError("Login failed!")

class Logout(APIView):

    def get(self):
        """
        input:  无
                获取登录状态,已登录返回0,否则返回非0
        """
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        return

    def post(self):
        """
        input:  self.input['username'] -------- 管理员用户名
        input:  self.input['password'] -------- 管理员密码
        """
        user = authenticate(username=self.input['username'], password=self.input['password'])
        if user is not None:
            login(self.request, user)
            return
        else:
            raise ValidateError("Login failed!")


class ActivityList(APIView):

    def get(self):
        """
        input:  空
                返回活动对象的数组(要求status>=0)
                需要登录
        """
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            result = []
            activity_list = Activity.get_all_activities()
            for a in activity_list:
                if a.status >= 0:
                    temp = {
                        'id': a.id,
                        'name': a.name,
                        'description': a.description,
                        'startTime': a.start_time,
                        "endTime": a.end_time,
                        'place': a.place,
                        'bookStart': a.book_start,
                        'bookEnd': a.book_end,
                        'currentTime': (int(time.time())),  # 当前时间的秒级时间戳
                        'status': a.status,
                    }
                    result.append(temp)
            return result


class ActivityDelete(APIView):

    def post(self):
        """
        input:  self.input['id'] -------- 活动id
                删除此id对应的活动
                需要登录(没写,但我觉得应该要吧...不然直接打这个url进来不就渗透了吗...
        """
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            activity = Activity.get_by_id(self.input['id'])
            return