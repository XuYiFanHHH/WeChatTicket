import time
import datetime
import re
import json

from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User
from wechat.models import Activity
from wechat.models import Ticket


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        # raise NotImplementedError('You should implement UserBind.validate_user method')
        if not re.match(r'^\d{10}$', self.input['student_id']):
            raise ValidateError('Invalid student number!')
        if len(self.input['password']) == 0:
            raise ValidateError('Invalid password!')
        return

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class ActivityDetail(APIView):

    def get(self):
        """
        input:  self.input['id'] -------- 活动id
        """
        self.check_input('id')
        activity = Activity.get_by_id(self.input['id'])
        if activity.status != 1:
            raise LogicError("The activity isn't normally published!")
        else:
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
                'remainTickets': activity.remain_tickets,
                'currentTime': (int(time.time())),   # 当前时间的秒级时间戳
            }


class TicketDetail(APIView):

    def get(self):
        """
        input:  self.input['openid'] -------- 微信用户OpenID
                self.input['ticket'] -------- 电子票unique_id
        """
        self.check_input('openid', 'ticket')
        ticket = Ticket.get_by_unique_id(self.input['ticket'])
        activity = Activity.get_by_id(ticket.activity_id)
        return {
            'activityName': activity.name,
            'place': activity.place,
            'activityKey': activity.key,
            'uniqueId': ticket.unique_id,
            'startTime': time.mktime(time.strptime(activity.start_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
            'endTime': time.mktime(time.strptime(activity.end_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),
            'currentTime': int(time.time()),  # 当前时间的秒级时间戳
            'status': ticket.status,
        }