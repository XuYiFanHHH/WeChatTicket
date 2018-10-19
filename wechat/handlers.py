# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
import time, datetime, timedelta
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

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class BookListHandler(WeChatHandler):

    def check(self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        all_activities = Activity.get_all_activities().order_by('book_start')
        all_activities_list = []
        for act in all_activities:
            all_activities_list.append(act)
        while len(all_activities_list) > 8:
            all_activities_list = all_activities_list[1:]
            if len(all_activities_list) > 8:
                all_activities_list.pop()
        result = []
        for act in all_activities_list:
            result.append({'Title': act.name, 'Url': self.url_activity_detail(act.id)})
        return self.reply_news(result)

class BookTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('抢票') or self.is_event_click(self.view.event_keys['book_header'])

    def handle(self):
        if self.is_msg_type('text'):
            # 通过抢票命令进入
            search = (self.input['Content'].split() or [None, None])[1]
            # 在name字段匹配
            if search is not None:
                flag = True
                try:
                    activity_1 = Activity.get_all_activities()
                except LogicError:
                    flag = False
                if flag:
                    activity_1 = activity_1.filter(name=search)
            # 在key字段匹配
            if search is not None:
                activity_2 = Activity.get_all_activities()
                activity_2 = activity_2.filter(key=search)
