# -*- coding: utf-8 -*-
from django.test import TestCase
from wechat.models import User, Activity, Ticket
import json
import datetime
# Create your tests here.


# 学号绑定测试
class StudentIdBindTest(TestCase):
    # 初始化
    def setUp(self):
        User.objects.create(open_id="123456789", student_id="2016010649")

    # 路由测试-get
    def test_router_get(self):
        response = self.client.get('/api/u/user/bind', {'openid': '123456789'})
        self.assertEqual(response.status_code, 200)

    # 路由测试-post
    def test_router_post(self):
        response = self.client.post('/api/u/user/bind', {'openid': '123456789', 'student_id': '2016010649',
                                                         'password': '12516'})
        self.assertEqual(response.status_code, 200)

    # 测试获取当前已绑定学号的用户绑定状态
    def test_binded_student(self):
        response = self.client.get('/api/u/user/bind', {'openid': '123456789'})
        self.assertEqual(json.loads(response.content.decode())['data'], '2016010649')

    # 测试获取当前未绑定学号的用户绑定状态
    def test_not_binded_student(self):
        response = self.client.get('/api/u/user/bind', {'openid': '8794616'})
        self.assertEqual(json.loads(response.content.decode())['data'], None)

    # 测试将当前用户成功绑定至指定学号
    def test_bind_student_id_success(self):
        response = self.client.post('/api/u/user/bind', {'openid': '123456789', 'student_id': '2016010649',
                                                         'password': '12516'})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    # 测试将当前用户失败绑定至指定学号
    def test_bind_student_id_fail(self):
        response = self.client.post('/api/u/user/bind', {'openid': '123456789', 'student_id': '2016649',
                                                         'password': ''})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)


# 活动详情测试
class ActivityInfoTest(TestCase):
    # 初始化
    def setUp(self):
        new_activity = Activity(
            name='玩玩',
            key='玩  ',
            description='桌游',
            start_time=datetime.datetime.fromtimestamp(1539844241),
            end_time=datetime.datetime.fromtimestamp(1539844945),
            place='THU ',
            book_start=datetime.datetime.fromtimestamp(1539844345),
            book_end=datetime.datetime.fromtimestamp(1539844545),
            total_tickets=11,
            pic_url='www.baidu.com',
            remain_tickets=10,
            status=1,
        )
        new_activity.save()
        self.id_success = new_activity.id
        new_activity = Activity(
            name='玩一玩',
            key='玩',
            description='玩桌游',
            start_time=datetime.datetime.fromtimestamp(1539844245),
            end_time=datetime.datetime.fromtimestamp(1539844945),
            place='THU',
            book_start=datetime.datetime.fromtimestamp(1539844345),
            book_end=datetime.datetime.fromtimestamp(1539844545),
            total_tickets=11,
            pic_url='www.baidu.com',
            remain_tickets=10,
            status=0,
        )
        new_activity.save()
        self.id_fail = new_activity.id


    # 路由测试-get
    def test_router_get(self):
        response = self.client.get('/api/u/activity/detail', {'id': self.id_success})
        self.assertEqual(response.status_code, 200)

    # 测试获取已发布状态活动的详情
    def test_activity_info_success(self):
        response = self.client.get('/api/u/activity/detail', {'id': self.id_success})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)
        self.assertEqual(json.loads(response.content.decode())['data']['name'], '玩玩')
        self.assertEqual(json.loads(response.content.decode())['data']['remainTickets'], 10)

    # 测试获取非已发布状态活动的详情
    def test_activity_info_fail(self):
        response = self.client.get('/api/u/activity/detail', {'id': self.id_fail})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)


# 电子票详情测试
class TicketInfoTest(TestCase):
    # 初始化
    def setUp(self):
        User.objects.create(open_id="123456789", student_id="2016010649")
        new_activity = Activity(
            name='玩玩',
            key='玩  ',
            description='桌游',
            start_time=datetime.datetime.fromtimestamp(1539844241),
            end_time=datetime.datetime.fromtimestamp(1539844945),
            place='THU ',
            book_start=datetime.datetime.fromtimestamp(1539844345),
            book_end=datetime.datetime.fromtimestamp(1539844545),
            total_tickets=11,
            pic_url='www.baidu.com',
            remain_tickets=10,
            status=1,
        )
        new_activity.save()
        new_ticket = Ticket(
            student_id='2016010649',
            unique_id='789456123',
            activity=new_activity,
            status=1,
        )
        new_ticket.save()

    # 路由测试-get
    def test_router_get(self):
        response = self.client.get('/api/u/ticket/detail', {'openid': '123456789', 'ticket': '789456123'})
        self.assertEqual(response.status_code, 200)

    # openid和uniqueid都正确的成功测试
    def test_get_ticket_info_success(self):
        response = self.client.get('/api/u/ticket/detail', {'openid': '123456789', 'ticket': '789456123'})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)
        self.assertEqual(json.loads(response.content.decode())['data']['uniqueId'], '789456123')


    # 错误测试
    def test_get_ticket_info_fail(self):
        response = self.client.get('/api/u/ticket/detail', {'openid': '123456789', 'ticket': '05252'})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)
