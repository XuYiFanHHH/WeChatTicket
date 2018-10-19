
import time, datetime
import uuid
from PIL import Image
from io import BytesIO

from codex.baseerror import *
from codex.baseview import APIView
from wechat.views import CustomWeChatView

from wechat.models import User
from wechat.models import Activity
from wechat.models import Ticket

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings


def datetime_to_timestamp(date_time):
    # 将datetime类型的时间转换为时间戳
    return time.mktime(time.strptime(date_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))


def UTCtime_to_timestamp(UTC_time):
    # 将UTC通用标准时转换为时间戳
    return time.mktime(time.strptime((datetime.datetime.strptime(UTC_time, "%Y-%m-%dT%H:%M:%S.%fZ") + \
                                               datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))


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

    def post(self):
        """
        input:  无
                获取登录状态,已登录返回0,否则返回非0
        """
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            logout(self.request)
        return


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
                        'startTime': time.mktime(time.strptime(act.start_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
                        "endTime": time.mktime(time.strptime(act.end_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
                        'place': act.place,
                        'bookStart': time.mktime(time.strptime(act.book_start.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
                        'bookEnd': time.mktime(time.strptime(act.book_end.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
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
            new_activity = Activity(name=self.input['name'], key=self.input['key'],place=self.input['place'], description=self.input['description'], pic_url=self.input['picUrl'],\
                                    start_time=self.input['startTime'], end_time=self.input['endTime'],\
                                    book_start=self.input['bookStart'], book_end=self.input['bookEnd'],\
                                    total_tickets=self.input['totalTickets'], status=self.input['status'], remain_tickets=self.input['totalTickets'])
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
            image_path = '%s/%s%s%s' % (settings.MEDIA_SAVE_ROOT, str(int(round(time.time() * 1000))), str(uuid.uuid1()), img.name)
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
                'startTime': time.mktime(time.strptime(activity.start_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
                'endTime': time.mktime(time.strptime(activity.end_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
                'place': activity.place,
                'bookStart': time.mktime(time.strptime(activity.book_start.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
                'bookEnd': time.mktime(time.strptime(activity.book_end.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
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
                self.input['name'] -------- 活动名称
                self.input['place'] -------- 活动地点
                self.input['description'] -------- 活动描述
                self.input['picUrl'] -------- 活动配图url
                self.input['startTime'] -------- 活动开始时间
                self.input['endTime'] -------- 活动结束时间
                self.input['bookStart'] -------- 抢票开始时间
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
            temp = self.input['startTime']

            activity = Activity.get_by_id(self.input['id'])

            if activity.name != self.input['name']:                         # 活动名称需要修改
                if activity.status == activity.STATUS_PUBLISHED:             # 活动已经发布
                    raise ValidateError("Can't change activity's name while the activity is published!")
                else:                                                        # 活动尚未发布
                    activity.name = self.input['name']

            if activity.place != self.input['place']:                        # 活动地点需要修改
                if activity.status == activity.STATUS_PUBLISHED:              # 活动已经发布
                    raise ValidateError("Can't change activity's place while the activity is published!")
                else:                                                         # 活动尚未发布
                    activity.place = self.input['place']

            activity.description = self.input['description']                 # 活动描述

            activity.pic_url = self.input['picUrl']                           # 活动配图url

            if datetime_to_timestamp(activity.start_time) != UTCtime_to_timestamp(self.input['startTime']):
                                                                                # 活动开始时间需要修改
                if int(time.time()) >= datetime_to_timestamp(activity.end_time):
                                                                               # 活动已经结束
                    raise ValidateError("Can't change activity's start time while the activity is end!")
                else:                                                          # 活动尚未结束
                    activity.start_time = UTCtime_to_timestamp(self.input['startTime'])

            if datetime_to_timestamp(activity.end_time) != UTCtime_to_timestamp(self.input['endTime']):
                                                                                # 活动结束时间需要修改
                if int(time.time()) >= datetime_to_timestamp(activity.end_time):
                                                                               # 活动已经结束
                    raise ValidateError("Can't change activity's end time while the activity is end!")
                else:                                                          # 活动尚未结束
                    activity.end_time = UTCtime_to_timestamp(self.input['endTime'])

            if datetime_to_timestamp(activity.book_start) != UTCtime_to_timestamp(self.input['bookStart']):
                                                                                # 抢票开始时间需要修改
                if activity.status == activity.STATUS_PUBLISHED:              # 活动已经发布
                    raise ValidateError("Can't change activity's book start time while the activity is published!")
                else:                                                         # 活动尚未发布
                    activity.book_start = UTCtime_to_timestamp(self.input['bookStart'])

            if datetime_to_timestamp(activity.book_end) != UTCtime_to_timestamp(self.input['bookEnd']):
                                                                                # 抢票结束时间需要修改
                if int(time.time()) >= datetime_to_timestamp(activity.start_time):
                                                                               # 活动已经开始
                    raise ValidateError("Can't change activity's book end time while the activity is end!")
                else:                                                          # 活动尚未开始
                    activity.book_end = UTCtime_to_timestamp(self.input['bookEnd'])

            if activity.total_tickets != int(self.input['totalTickets']):          # 总票数需要修改
                if int(time.time()) >= datetime_to_timestamp(activity.book_start):
                                                                               # 抢票已经开始
                    raise ValidateError("Can't change activity's total tickets count while booking is started!")
                else:                                                          # 抢票尚未开始
                    activity.total_tickets = int(self.input['totalTickets'])

            if activity.status != int(self.input['status']):                         # 活动状态需要修改
                if activity.status == activity.STATUS_SAVED:                        # 活动是暂存状态
                    activity.status = int(self.input['status'])                      # 允许更改状态
                else:
                    raise ValidateError("Can't change published activity to saved or change deleted activity's status!")
            return


class ActivityMenu(APIView):

    def get(self):
        """
        input:  空
                返回可加入菜单的活动对象数组
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
                        'menuIndex': 0
                    }
                    result.append(temp)
            for ii in range(5):
                index = ii + 1
                opposite_index = index * (-1)
                if index <= len(result):
                    result[opposite_index]['menuIndex'] = index
        return result

    def post(self):
        """
                input:  活动id数组
                        需要登录
        """
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            result = []
            activity_id_list = self.input
            for act_id in activity_id_list:
                act = Activity.get_by_id(act_id)
                result.append(act)
        CustomWeChatView.update_menu(result)
        return


class ActivityCheckin(APIView):

    def post(self):

        """
        input:  self.input['actId'] -------- 活动ID
                self.input['ticket'] -------- 电子票ID
                self.input['studentId'] -------- 学号
                检票
                需要登录
        """
        if not self.request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            self.check_input('actId')
            result = None
            if 'ticket' not in self.input:
                self.check_input('studentId')
                result = Ticket.get_by_activity_and_student_number(self.input['actId'], self.input['studentId'])
                if result:
                    result = result[0]
            elif 'studentId' not in self.input:
                self.check_input('ticket')
                result = Ticket.get_by_unique_id(self.input['ticket'])
            if result:
                result.status = Ticket.STATUS_USED
                return {
                    'ticket': result.unique_id,
                    'studentId': result.student_id,
                }
            else:
                return LogicError('Ticket not found')
