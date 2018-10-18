
import time
import datetime
import uuid
from PIL import Image
from io import BytesIO

from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User
from wechat.models import Activity
from wechat.models import Ticket

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings


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
        self.check_input('username', 'password')
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
        self.check_input('username', 'password')
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
            for act in activity_list:
                if act.status >= 0:
                    temp = {
                        'id': act.id,
                        'name': act.name,
                        'description': act.description,
                        'startTime': act.start_time,
                        "endTime": act.end_time,
                        'place': act.place,
                        'bookStart': act.book_start,
                        'bookEnd': act.book_end,
                        'currentTime': int(time.time()),  # 当前时间的秒级时间戳
                        'status': act.status,
                    }
                    result.append(temp)
            return result


class ActivityDelete(APIView):

    def post(self):
        """
        input:  self.input['id'] -------- 活动id
                删除此id对应的活动
                需要登录(没写,但我觉得应该要吧...不然直接打这个url进来不就渗透了吗...)
        """
        self.check_input('id')
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            activity = Activity.get_by_id(self.input['id'])
            activity.delete()
            return


class ActivityCreate(APIView):

    def post(self):
        """
        input:  self.input['name'] -------- 活动名称
                self.input['key'] -------- 活动代称
                self.input['place'] -------- 活动地点
                self.input['description'] -------- 活动描述
                self.input['picUrl'] -------- 活动配图url
                self.input['startTime'] -------- 活动开始时间
                self.input['endTime'] -------- 活动结束时间
                self.input['bookStart'] -------- 抢票开始时间
                self.input['bookEnd'] -------- 抢票结束时间
                self.input['totalTickets'] -------- 总票数
                self.input['status'] -------- 暂存或发布
                添加新活动
                需要登录
        """
        self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart',\
                         'bookEnd', 'totalTickets', 'status')
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            new_activity = Activity(name=self.input['name'], key=self.input['key'], description=self.input['description'], pic_url=self.input['picUrl'],\
                                   start_time=self.input['startTime'], end_time=self.input['endTime'], book_start=self.input['bookStart'],\
                                   book_end=self.input['bookEnd'], total_tickets=self.input['totalTickets'], status=self.input['status'])
            new_activity.save()
            return new_activity.id


class ImageUpload(APIView):

    def post(self):
        """
        input:  self.input['image'] -------- 图片文件
                上传图片并保存至服务器
                需要登录
        """
        self.check_input('image')
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            img = self.input['image']
            img = img[0]
            image_path = '%s\%s%s%s' % (settings.MEDIA_ROOT, str(int(round(time.time() * 1000))), str(uuid.uuid1()), img.name)
            file = img.file
            image = Image.open(file)
            image.save(image_path)
            return image_path


class ActivityDetail(APIView):

    def get(self):
        """
        input:  self.input['id'] -------- 活动id
                返回活动的详情数据
                需要登录
        """
        self.check_input('id')
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            activity = Activity.get_by_id(self.input['id'])

            return {
                'name': activity.name,
                'key': activity.key,
                'description': activity.description,
                'startTime': activity.start_time,
                'endTime': activity.end_time,
                'place': activity.place,
                'bookStart': activity.book_start,
                'bookEnd': activity.book_end,
                'totalTickets': activity.total_tickets,
                'picUrl': activity.pic_url,
                'bookedTickets': activity.total_tickets - activity.remain_tickets,
                'usedTickets': Ticket.count_used_tickets(activity.id),
                'currentTime': int(time.time()),  # 当前时间的秒级时间戳
                'status': activity.status,
            }

    def post(self):
        """
        input:  self.input['id'] -------- 活动id
                qself.input['name'] -------- 活动名称
                qself.input['place'] -------- 活动地点
                qself.input['description'] -------- 活动描述
                qself.input['picUrl'] -------- 活动配图url
                self.input['startTime'] -------- 活动开始时间
                self.input['endTime'] -------- 活动结束时间
                qself.input['bookStart'] -------- 抢票开始时间
                self.input['bookEnd'] -------- 抢票结束时间
                self.input['totalTickets'] -------- 总票数
                self.input['status'] -------- 暂存或发布
                修改活动详情
                需要登录
        """
        self.check_input('id', 'name', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart',\
                         'bookEnd', 'totalTickets', 'status')
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            activity = Activity.get_by_id(self.input['id'])
            activity.description = self.input['description']
            activity.pic_url = self.input['picUrl']
            if activity.status != activity.STATUS_PUBLISHED:    # 尚未发布的活动进入修改
                activity.name = self.input['name']
                activity.place = self.input['place']
                activity.book_start = self.input['bookStart']
            if int(time.time()) <= activity.end_time:           # 尚未结束的活动进入修改
                activity.start_time = self.input['startTime']
                activity.end_time = self.input['endTime']
            if int(time.time()) <= activity.start_time:         # 尚未开始的活动进入修改
                activity.book_end = self.input['bookEnd']       # ??????
            if int(time.time()) <= activity.book_start:         # 尚未开始抢票的活动进入修改
                activity.total_tickets = self.input['totalTickets']
            if activity.status == activity.STATUS_SAVED:
                activity.status = self.input['status']
            elif activity.status == activity.STATUS_PUBLISHED:
                activity.status = activity.STATUS_PUBLISHED
            else:
                raise LogicError("Can't edit deleted activity!")
            return

