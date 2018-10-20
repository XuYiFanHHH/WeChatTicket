# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
import time, datetime
import uuid
from PIL import Image
from io import BytesIO
import re

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
from django.db import transaction

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
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind']) or len(self.user.student_id) == 0

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty']) and len(self.user.student_id) != 0

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class BookListHandler(WeChatHandler):

    def check(self):
        return (self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])) and len(self.user.student_id) != 0

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


class TicketBookHandler(WeChatHandler):

    def check(self):
        return (self.is_text_command('抢票') or (self.is_msg_type('event') and re.match(r'^BOOKING_ACTIVITY_', self.input['EventKey']))) and len(self.user.student_id) != 0

    def handle(self):
        with transaction.atomic():
            if self.is_msg_type('text'):
                # 通过抢票命令进入
                search = self.input['Content'].split()
                if len(search) == 1:
                    return self.reply_text('找不到此活动Orz')
                else:
                    search = search[1]
                # 在name字段匹配
                if search is not None:
                    activity_1 = Activity.get_all_activities()
                    if activity_1:
                        activity_1 = activity_1.filter(name=search)
                    if activity_1 and len(activity_1) > 0:
                        activity_1 = activity_1[0]
                    else:
                        activity_1 = None

                # 在key字段匹配
                if search is not None:
                    activity_2 = Activity.get_all_activities()
                    if activity_2:
                        activity_2 = activity_2.filter(name=search)
                    if activity_2 and len(activity_2) > 0:
                        activity_2 = activity_2[0]
                    else:
                        activity_2 = None

                if activity_1:
                    activity = activity_1
                elif activity_2:
                    activity = activity_2
                else:
                    return self.reply_text('找不到此活动Orz')

            elif self.is_msg_type('event'):
                activity_id = int(self.input['EventKey'].replace(self.view.event_keys['book_header'], ''))
                try:
                    activity = Activity.get_by_id(activity_id)
                except LogicError:
                    return self.reply_text('找不到此活动Orz')
                if not activity:
                    return self.reply_text('找不到此活动Orz')

            # 此时activity必定存在
            my_ticket = Ticket.get_by_activity_and_student_number(activity.id, self.user.student_id)
            temp = []
            for tic in my_ticket:
                temp.append(tic)
            my_ticket = temp
            while len(my_ticket) > 0 and my_ticket[0].status != Ticket.STATUS_VALID:
                my_ticket.pop(0)
            if len(my_ticket) == 0:
                if activity.remain_tickets > 0:
                    activity.remain_tickets = activity.remain_tickets - 1
                    activity.save()
                    unique = '%s%s' % (str(int(round(time.time() * 1000))), str(uuid.uuid1()))
                    ticket = Ticket(student_id=self.user.student_id, unique_id=unique, status=Ticket.STATUS_VALID,
                                    activity=activity)
                    ticket.save()
                    return self.reply_single_news({
                        'Title': '[' + activity.name + '] 抢票成功！',
                        'Description': '活动名称：' + activity.name + '\n活动代称：' + activity.key + '\n请于活动开始时前往现场使用，您可以通过 [查票] 菜单查询电子票、或发送 [取票/退票 活动名称或代称] 查询或退票(・◇・)',
                        'Url': self.url_ticket_detail(ticket.unique_id),
                    })
                else:
                    return self.reply_text('此活动的电子票已经全部发出，没有抢到QwQ')
            else:
                my_ticket = my_ticket[0]
                return self.reply_single_news({
                    'Title': '[' + activity.name + '] 电子票',
                    'Description': '活动名称：' + activity.name + '\n活动代称：' + activity.key,
                    'Url': self.url_ticket_detail(my_ticket.unique_id),
                })


class TicketDetailHandler(WeChatHandler):

    def check(self):
        return (self.is_text_command('取票') or self.is_event_click(self.view.event_keys['get_ticket'])) and len(self.user.student_id) != 0

    def handle(self):
        if self.is_msg_type('text'):
            # 通过取票命令进入
            search = self.input['Content'].split()
            if len(search) == 1:
                return self.reply_text('找不到此活动Orz')
            else:
                search = search[1]
            # 在name字段匹配
            if search is not None:
                activity_1 = Activity.get_all_activities()
                if activity_1:
                    activity_1 = activity_1.filter(name=search)
                if activity_1 and len(activity_1) > 0:
                    activity_1 = activity_1[0]
                else:
                    activity_1 = None

            # 在key字段匹配
            if search is not None:
                activity_2 = Activity.get_all_activities()
                if activity_2:
                    activity_2 = activity_2.filter(name=search)
                if activity_2 and len(activity_2) > 0:
                    activity_2 = activity_2[0]
                else:
                    activity_2 = None

            if activity_1:
                activity = activity_1
            elif activity_2:
                activity = activity_2
            else:
                return self.reply_text('找不到此活动Orz')
            # 此时activity必定存在
            my_ticket = Ticket.get_by_activity_and_student_number(activity.id, self.user.student_id)
            if len(my_ticket) == 0:
                return self.reply_text('您还没有此活动的票！Ծ‸Ծ')
            valid_ticket = None
            for tic in my_ticket:
                if tic.status == Ticket.STATUS_VALID:
                    valid_ticket = tic
            if not valid_ticket:
                return self.reply_text('您还没有此活动的合法票！Ծ‸Ծ')
            return self.reply_single_news({
                'Title': '[' + activity.name + '] 电子票',
                'Description': '活动名称：' + activity.name+'\n活动代称：' + activity.key,
                'Url': self.url_ticket_detail(valid_ticket.unique_id),
            })

        elif self.is_msg_type('event'):
            # 通过取票按钮进入
            ticket_list = Ticket.get_user_tickets(self.user.student_id)
            ticket_list = ticket_list.order_by('-activity__start_time')
            if len(ticket_list) == 0:
                return self.reply_text('您尚未持有任何票0.0')
            if len(ticket_list) > 8:
                ticket_list = ticket_list[:7]
            result = []
            for tic in ticket_list:
                act = tic.activity
                result.append({'Title': '[' + act.name + '] 电子票', 'Url': self.url_ticket_detail(tic.unique_id)})
            return self.reply_news(result)
        return


class TicketReturnHandler(WeChatHandler):

    def check(self):
        return (self.is_text_command('退票')) and len(self.user.student_id) != 0

    def handle(self):
        content = self.input['Content'].split()
        if len(content) == 1:
            return self.reply_text('退票失败，找不到需要退票的活动_(:з」∠)_')
        else:
            content = content[1]
        if not content:
            return self.reply_text('退票失败，找不到需要退票的活动_(:з」∠)_')
        if content is not None:
            # 在name字段匹配
            activity_1 = Activity.get_all_activities()
            if activity_1:
                activity_1 = activity_1.filter(name=content)
            if activity_1 and len(activity_1) > 0:
                activity_1 = activity_1[0]
            else:
                activity_1 = None

            # 在key字段匹配
            activity_2 = Activity.get_all_activities()
            if activity_2:
                activity_2 = activity_2.filter(name=content)
            if activity_2 and len(activity_2) > 0:
                activity_2 = activity_2[0]
            else:
                activity_2 = None

            if activity_1:
                activity = activity_1
            elif activity_2:
                activity = activity_2
            else:
                return self.reply_text('退票失败，找不到需要退票的活动_(:з」∠)_')

            my_ticket = Ticket.get_by_activity_and_student_number(activity.id, self.user.student_id)
            valid_ticket=None
            for tic in my_ticket:
                if tic.status == Ticket.STATUS_VALID:
                    valid_ticket = tic
            if not valid_ticket:
                return self.reply_text('退票失败，您没有此次活动的合法电子票！|･ω･｀)')
            if not my_ticket:
                return self.reply_text('退票失败，您没有此次活动的电子票！|･ω･｀)')
            else:
                valid_ticket.status = Ticket.STATUS_CANCELLED
                valid_ticket.save()
                activity.remain_tickets = activity.remain_tickets + 1
                activity.save()
                return self.reply_text('活动 [' + activity.name + '] 退票成功！')
