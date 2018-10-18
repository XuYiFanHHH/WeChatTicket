# -*- coding: utf-8 -*-
from django.test import TestCase
from wechat.models import User
from wechat.models import Activity
import json
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

    # 测试将当前用户成功绑定至制定学号
    def test_bind_student_id_success(self):
        response = self.client.post('/api/u/user/bind', {'openid': '123456789', 'student_id': '2016010649',
                                                         'password': '12516'})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    # 测试将当前用户失败绑定至制定学号
    def test_bind_student_id_fail(self):
        response = self.client.post('/api/u/user/bind', {'openid': '123456789', 'student_id': '2016649',
                                                         'password': ''})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)


# 活动详情测试
class ActivityInfoTest(TestCase):
    # 初始化
    def setUp(self):
        Activity.objects.create(
            name='玩一玩',
            key='玩',
            description='玩桌游',
            startTime='1499825149',
            endTime='2499825149',
            place='THU',
            bookStart='1899825149',
            bookEnd='2099825149',
            totalTickets=11,
            picUrl='www.baidu.com',
            remainTickets=10,
            currentTime="1899825149",
        )
        this.id = Activity.objects.get(name="玩一玩").id

    # 路由测试-get
    def test_router_get(self):
        response = self.client.get('/api/u/activity/detail', {'id': this.id})
        self.assertEqual(response.status_code, 200)

    # 测试获取已发布状态活动的详情
    def test_activity_info_success(self):
        response = self.client.get('/api/u/activity/detail', {'id': this.id})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    # 测试获取非已发布状态活动的详情
    def test_activity_info_fail(self):
        response = self.client.get('/api/u/activity/detail', {'id': this.id + 1})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

