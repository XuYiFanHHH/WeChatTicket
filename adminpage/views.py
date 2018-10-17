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
