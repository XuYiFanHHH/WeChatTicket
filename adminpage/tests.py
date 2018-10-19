# from django.contrib.auth.models import User
# from django.test import TestCase
# from wechat.models import Activity
# import json
# import datetime
# # Create your tests here.
#
#
# class AdminLoginTest(TestCase):
#     #初始化
#     def setUp(self):
#         User.objects.create_user(username="llp16", password="666")
#
#     #路由测试-get
#     def test_router_login_get(self):
#         response = self.client.get('/api/a/login')
#         self.assertEqual(response.status_code, 200)
#
#     #测试路由-post
#     def test_router_login_post(self):
#         response = self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
#         self.assertEqual(response.status_code, 200)
#
#     #测试已注册用户能否登陆
#     def test_register_login(self):
#         response = self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
#         self.assertEqual(json.loads(response.content.decode())['code'], 0)
#
#     #测试未注册用户能否登陆
#     def test_not_register_login(self):
#         response = self.client.post('/api/a/login', {'username':'txy16', 'password':'666'})
#         self.assertNotEqual(json.loads(response.content.decode())['code'], 0)
#
#     #测试未登录状态
#     def test_not_logged_admin(self):
#         response = self.client.get('/api/a/login')
#         self.assertNotEqual((json.loads(response.content.decode())['code']), 0)
#
#     #测试已登录状态
#     def test_logged_admin(self):
#         self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
#         response = self.client.get('/api/a/login')
#         self.assertEqual(json.loads(response.content.decode())['code'], 0)
#
# class AdminLogoutTest(TestCase):
#     #初始化
#     def setUp(self):
#         User.objects.create_user(username='llp16', password='666')
#
#     #路右测试-post
#     def test_router_logout_post(self):
#         response = self.client.post('/api/a/logout')
#         self.assertEqual(response.status_code, 200)
#
#     #已登录状态测试登出
#     def test_logged_logout(self):
#         self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
#         response = self.client.post('/api/a/logout')
#         self.assertEqual(json.loads(response.content.decode())['code'], 0)
#
#     def test_not_logged_logout(self):
#         response = self.client.post('/api/a/logout')
#         self.assertNotEqual(json.loads(response.content.decode())['code'], 0)
#
# class ActivityListTest(TestCase):
#     #初始化
#     def setUp(self):
#         User.objects.create_user(username='llp16', password='666')
#
#     #路由测试-get
#     def test_router_list_get(self):
#         response = self.client.get('/api/a/activity/list')
#         self.assertEqual(response.status_code, 200)
#
#     #测试未登录状态获得活动列表
#     def test_not_logged_list(self):
#         response = self.client.get('/api/a/activity/list')
#         self.assertNotEqual(json.loads(response.content.decode())['code'], 0)
#
#     #测试已登录状态获得活动列表
#     def test_logged_list(self):
#         self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
#         response = self.client.get('/api/a/activity/list')
#         self.assertEqual(json.loads(response.content.decode())['code'], 0)
#
#     #测试活动列表内活动状态是否大于等于0
#     def test_list_status(self):
#         self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
#         response = self.client.get('/api/a/activity/list')
#         content = json.loads(response.content.decode())['data']
#         flag = 0
#         for act in content:
#             if act.status < 0:
#                 flag = 1
#         self.assertEqual(flag, 0)
#
#     # #测试活动列表内的字段名是否正确
#     # def test_activity_key(self):
#     #     self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
#     #     response = self.client.get('/api/a/activity/list')
#     #     content = json.loads(response.content.decode())['data']
#     #     flag = 0
#
#
#
# class AcivityCreateTest(TestCase):
#     #初始化
#     def setUp(self):
#         User.objects.create_user(username='llp16', password='666')
#         self.new_activity = {
#             'name': '玩玩',
#             'key': '玩',
#             'place': 'THU',
#             'description': '桌游',
#             'picUrl': '',
#             'startTime':'2016-10-10 10:55',
#             'endTime':'2016-10-10 10:55',
#             'bookStart':'2016-10-10 10:55',
#             'bookEnd':'2016-10-10 10:55',
#             'totalTickets': 11,
#             'status': 1
#         }
#
#     #路由测试-post
#     def test_router_create_post(self):
#         response = self.client.post('/api/a/activity/create', self.new_activity)
#         self.assertEqual(response.status_code, 200)
#
#     #测试未登录状态创建活动
#     def test_not_logged_create(self):
#         response = self.client.post('/api/a/activity/create', self.new_activity)
#         self.assertNotEqual(json.loads(response.content.decode())['code'], 0)
#
#     #测试已登录状态创建活动
#     def test_logged_create(self):
#         self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
#         response = self.client.post('/api/a/activity/create', self.new_activity)
#         self.assertEqual(json.loads(response.content.decode())['code'], 0)
#         self.assertNotEqual(json.loads(response.content.decode())['data'], None)
#
# class TestDeleteActivity(TestCase):
#     #初始化
#     def setUp(self):
#         User.objects.create_user(username='llp16', password='666')
#         self.new_activity = {
#             'name': '玩玩',
#             'key': '玩',
#             'place': 'THU',
#             'description': '桌游',
#             'picUrl': '',
#             'startTime':'2016-10-10 10:55',
#             'endTime':'2016-10-10 10:55',
#             'bookStart':'2016-10-10 10:55',
#             'bookEnd':'2016-10-10 10:55',
#             'totalTickets': 11,
#             'status': 1
#         }
#         self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
#         response = self.client.post('/api/a/activity/create', self.new_activity)
#         self.id = json.loads(response.content.decode())['data']
#
#     #路由测试-post
#     def test_router_delete_post(self):
#         response = self.client.post('/api/a/activity/delete', {'id':'-1'})
#         self.assertEqual(response.status_code, 200)
#
#     #测试删除未注册活动
#     def test_delete_not_register_activity(self):
#         response = self.client.post('/api/a/activity/delete', {'id':'-1'})
#         self.assertNotEqual(json.loads(response.content.decode())['code'], 0)
#
#     #测试删除已注册活动
#     def test_delete_register_activity(self):
#         response = self.client.post('/api/a/activity/delete', {'id':self.id})
#         self.assertEqual(json.loads(response.content.decode())['code'], 0)
#
# class TestUploadTest(TestCase):
#     #初始化
#     def setUp(self):
#         User.objects.create_user(username='llp16', password='666')
#
#     #路由测试-post
#     def test_router_upload_post(self):
#         with open('./media/image.png', 'r') as fp:
#             response = self.client.post('/api/a/image/upload', {'image':fp})
#         self.assertEqual(response.status_code, 200)
#
#     #测试未登录上传
#     def test_not_logged_upload(self):
#         with open('./media/image.png', 'r') as fp:
#             response = self.client.post('/api/a/image/upload', {'image':fp})
#         self.assertNotEqual(json.loads(response.content.decode())['code'], 0)
#
#     #测试已登录上传
#     def test_logged_upload(self):
#         self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
#         with open('./media/image.png', 'r') as fp:
#             response = self.client.post('/api/a/image/upload', {'image':fp})
#         self.assertEqual(json.loads(response.content.decode())['code'], 0)
