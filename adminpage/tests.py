from django.contrib.auth.models import User
from wechat.models import User as wechat_user
from django.test import TestCase
from wechat.models import Activity, Ticket
from datetime import datetime, timezone
import json
import datetime
# Create your tests here.


class AdminLoginTest(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_user(username="llp16", password="666")

    #路由测试-get
    def test_router_login_get(self):
        response = self.client.get('/api/a/login')
        self.assertEqual(response.status_code, 200)

    #测试路由-post
    def test_router_login_post(self):
        response = self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        self.assertEqual(response.status_code, 200)

    #测试已注册用户能否登陆
    def test_register_login(self):
        response = self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    #测试未注册用户能否登陆
    def test_not_register_login(self):
        response = self.client.post('/api/a/login', {'username':'txy16', 'password':'666'})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试未登录状态
    def test_not_logged_admin(self):
        response = self.client.get('/api/a/login')
        self.assertNotEqual((json.loads(response.content.decode())['code']), 0)

    #测试已登录状态
    def test_logged_admin(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.get('/api/a/login')
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

class AdminLogoutTest(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_user(username='llp16', password='666')

    #路由测试-post
    def test_router_logout_post(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.post('/api/a/logout',{"test":""})
        self.assertEqual(response.status_code, 200)

    #已登录状态测试登出
    def test_logged_logout(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.post('/api/a/logout', {'test':""})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    def test_not_logged_logout(self):
        response = self.client.post('/api/a/logout', {"test":""})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

class ActivityListTest(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_user(username='llp16', password='666')

    #路由测试-get
    def test_router_list_get(self):
        response = self.client.get('/api/a/activity/list')
        self.assertEqual(response.status_code, 200)

    #测试未登录状态获得活动列表
    def test_not_logged_list(self):
        response = self.client.get('/api/a/activity/list')
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试已登录状态获得活动列表
    def test_logged_list(self):
        self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
        response = self.client.get('/api/a/activity/list')
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    #测试活动列表内活动状态是否大于等于0
    def test_list_status(self):
        self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
        response = self.client.get('/api/a/activity/list')
        content = json.loads(response.content.decode())['data']
        flag = 0
        for act in content:
            if act.status < 0:
                flag = 1
        self.assertEqual(flag, 0)

    # #测试活动列表内的字段名是否正确
    # def test_activity_key(self):
    #     self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
    #     response = self.client.get('/api/a/activity/list')
    #     content = json.loads(response.content.decode())['data']
    #     flag = 0


class AcivityCreateTest(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_user(username='llp16', password='666')
        self.new_activity = {
            'name': 'HappyDay',
            'key': 'play',
            'place': 'THU',
            'description': 'game',
            'picUrl': '',
            'startTime': '2016-10-10 10:55',
            'endTime': '2016-10-10 10:55',
            'bookStart': '2016-10-10 10:55',
            'bookEnd': '2016-10-10 10:55',
            'totalTickets': 11,
            'status': 1
        }

    #路由测试-post
    def test_router_create_post(self):
        response = self.client.post('/api/a/activity/create', self.new_activity)
        self.assertEqual(response.status_code, 200)

    #测试未登录状态创建活动
    def test_not_logged_create(self):
        response = self.client.post('/api/a/activity/create', self.new_activity)
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试已登录状态创建活动
    def test_logged_create(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.post('/api/a/activity/create', self.new_activity)
        print("lalal"+str(response.content))
        self.assertEqual(json.loads(response.content.decode())['code'], 0)
        print('lala'+str(response.content))
        self.assertNotEqual(json.loads(response.content.decode())['data'], None)

class TestDeleteActivity(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_user(username='llp16', password='666')
        self.new_activity = {
            'name': 'HappyDay',
            'key': 'play',
            'place': 'THU',
            'description': 'game',
            'picUrl': '',
            'startTime': '2016-10-10 10:55',
            'endTime': '2016-10-10 10:55',
            'bookStart': '2016-10-10 10:55',
            'bookEnd': '2016-10-10 10:55',
            'totalTickets': 11,
            'status': 1
        }
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.post('/api/a/activity/create', self.new_activity)
        self.id = json.loads(response.content.decode())['data']

    #路由测试-post
    def test_router_delete_post(self):
        response = self.client.post('/api/a/activity/delete', {'id':'-1'})
        self.assertEqual(response.status_code, 200)

    #测试删除未注册活动
    def test_delete_not_register_activity(self):
        response = self.client.post('/api/a/activity/delete', {'id':'-1'})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试删除已注册活动
    def test_delete_register_activity(self):
        response = self.client.post('/api/a/activity/delete', {'id':self.id})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

class TestUploadTest(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_user(username='llp16', password='666')

    #路由测试-post
    def test_router_upload_post(self):
        with open('./static/u/activity_imgs/image.jpg', 'rb') as file:
            response = self.client.post('/api/a/image/upload', {'image':file})
            self.assertEqual(response.status_code, 200)

    #测试利用返回url上传
    # def test_reload_pic(self):
    #     with open('./static/u/activity_imgs/image.jpg', 'rb') as file:
    #         self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
    #         response = self.client.post('/api/a/image/upload', {'image':file})
    #         self.assertEqual(json.loads(response.content.decode())['code'], 0)
    #         response = self.client.get(response.json()['data'])
    #         self.assertEqual(response.status_code, 200)

    #测试未登录上传
    def test_not_logged_upload(self):
        with open('./static/u/activity_imgs/image.jpg', 'rb') as file:
            response = self.client.post('/api/a/image/upload', {'image': file})
            self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试已登录上传
    def test_logged_upload(self):
        with open('./static/u/activity_imgs/image.jpg', 'rb') as file:
            self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
            response = self.client.post('/api/a/image/upload', {'image':file})
            self.assertEqual(json.loads(response.content.decode())['code'], 0)

class TestActivityDetail(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_user(username='llp16', password='666')
        self.new_activity = {
            'name': 'HappyDay',
            'key': 'play',
            'place': 'THU',
            'description': 'game',
            'picUrl': '',
            'startTime': '2016-10-10 10:55',
            'endTime': '2019-10-10 10:55',
            'bookStart': '2016-10-10 10:55',
            'bookEnd': '2016-10-10 10:55',
            'totalTickets': 11,
            'status': 0
        }
        self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
        response = self.client.post('/api/a/activity/create', self.new_activity)
        self.id = json.loads(response.content.decode())['data']
        self.client.post('/api/a/logout', {'test': ''})
        # self.modify_activity = {"id": self.id, "name": "22", "place": "22", "description": "22", "picUrl": "",
        #              "totalTickets": "100", "status": 1, "startTime": datetime.datetime.now().isoformat(),
        #              "endTime": datetime.datetime.now().isoformat(), "bookStart": datetime.datetime.now().isoformat(),
        #              "bookEnd": datetime.datetime.now().isoformat()
        #
        # }

    #测试路由-get
    def test_router_detail_get(self):
        response = self.client.get('/api/a/activity/detail', {'id':self.id})
        self.assertEqual(response.status_code, 200)

    #测试路由-post
    def test_router_detail_post(self):
        response = self.client.get('/api/a/activity/detail', {'id': 0})
        self.assertEqual(response.status_code, 200)

    #测试未登录获取详情数据
    def test_not_logged_detail(self):
        response = self.client.get('/api/a/activity/detail', {'id':self.id})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试已登录获取详情数据
    def test_logged_detail(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.get('/api/a/activity/detail', {'id':self.id})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)
        self.assertEqual(json.loads(response.content.decode())['data']['key'], 'play')

    #测试获取不存在活动详情
    def test_wrong_activity_detail(self):
        self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
        response = self.client.get('/api/a/activity/detail', {'id': -1})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    def test_modify_detail(self):
        self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
        modify = {"id": 6, "name": "22", "place": "22", "description": "22", "picUrl": "",
                     "totalTickets": "100", "status": 1, "startTime": datetime.datetime.now().isoformat(),
                     "endTime": datetime.datetime.now().isoformat(), "bookStart": datetime.datetime.now().isoformat(),
                     "bookEnd": datetime.datetime.now().isoformat()}

        response = self.client.post('/api/a/activity/detail', modify)
        self.assertEqual(response.json()['code'], 2)

    #测试修改活动详情
    # def test_modify_detail(self):
    #     self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
    #     response = self.client.post('/api/a/activity/detail', self.modify_activity)
    #     print("xixixi"+str(response.content))
    #     self.assertEqual(json.loads(response.content.decode())['code'], 0)
    #     response = self.client.get('/api/a/activity/detail', {'id':self.id})
    #     self.assertEqual(json.loads(response.content.decode())['data']['key'], 'sleep')

class TestActivityMenu(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_user(username='llp16', password='666')
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        for i in range(6):
            act = Activity.objects.create(name='test' + str(i), key='test' + str(i), description='myTest',
                                               start_time='2018-12-02T08:00:00.000Z',
                                               end_time='2018-12-02T10:00:00.000Z', place='github',
                                               book_start='2018-11-02T08:00:00.000Z',
                                               book_end='2018-11-02T10:00:00.000Z',
                                               total_tickets=100, pic_url='xxx', remain_tickets=100, status=1)
            if i > 3:
                act.status = 0
        self.client.post('/api/a/logout', {'test':''})
        self.id_array = [activity.id for activity in Activity.objects.all()]
    #测试路由-get
    def test_router_menu_get(self):
        response = self.client.get('/api/a/activity/menu')
        self.assertEqual(response.status_code, 200)

    #测试路由-post
    def test_router_menu_post(self):
        response = self.client.post('/api/a/activity/menu', {'id':'0'})
        self.assertEqual(response.status_code, 200)

    #测试非法参数
    def test_wrong_array(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.post('/api/a/activity/menu', {'id':'0'})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试空数组参数
    # def test_blank_array(self):
    #     self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
    #     response = self.client.post('/api/a/activity/menu', [], content_type='application/json')
    #     self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试未登录获取菜单
    def test_not_logged_menu(self):
        response = self.client.get('/api/a/activity/menu')
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试已登录获取菜单
    def test_logged_menu(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.get('/api/a/activity/menu')
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    #测试未登录修改菜单
    def test_not_logged_modify(self):
        response = self.client.post('/api/a/activity/menu', self.id_array[:3], content_type='application/json')
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)

    #测试已登录修改菜单
    def test_logged_modify(self):
        self.client.post('/api/a/login', {'username': 'llp16', 'password': '666'})
        response = self.client.post('/api/a/activity/menu', self.id_array, content_type='application/json')
        print('test_logged_modify: ', str(response.content))
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

class TestActivityCheckin(TestCase):
    #初始化
    def setUp(self):
        self.open_id = 'asdssssdsdsasdsda'
        self.student_id = '2016013251'
        self.unique_id = 'ttyyttdfdfsssdf'
        self.activity = Activity.objects.create(name='test', key='test', description='myTest',
                                               start_time='2018-12-22T08:00:00.000Z',
                                               end_time='2018-12-22T10:00:00.000Z', place='THU',
                                               book_start='2018-11-22T08:00:00.000Z',
                                               book_end='2018-11-22T10:00:00.000Z',
                                               total_tickets=100, pic_url='xxx', remain_tickets=100, status=0)
        User.objects.create_user(username='llp16', password='666')
        wechat_user.objects.create(open_id=self.open_id, student_id=self.student_id)
        Ticket.objects.create(student_id=self.student_id, unique_id=self.unique_id,
                              activity=Activity.objects.get(id=self.activity.id),
                              status=1)
        self.ticket = Ticket.objects.get(student_id=self.student_id)

    #路由测试-post
    def test_router_Chekin_post(self):
        response = self.client.post('/api/a/activity/checkin', {'actid':'1', 'ticket':'', 'studentid':'2016013333'})
        self.assertEqual(response.status_code, 200)

    #测试check非法票
    def test_wrong_ticker(self):
        response = self.client.post('/api/a/activity/checkin', {'actid': self.activity.id, 'ticket': ''})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)


    #测试成功检票
    def test_success_checkin(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.post('/api/a/activity/checkin', {'actId':self.activity.id, 'ticket':self.unique_id})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)
        self.assertEqual(json.loads(response.content.decode())['data']['studentId'], self.student_id)

    #测试已用过票checkin
    def test_used_ticket_checkin(self):
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        self.client.post('/api/a/activity/checkin', {'actId': self.activity.id, 'ticket': self.unique_id})
        response = self.client.post('/api/a/activity/checkin', {'actId': self.activity.id, 'ticket': self.unique_id})
        self.assertEqual(Ticket.objects.get(student_id=self.student_id).status, Ticket.STATUS_USED)

    #测试已取消票checkin
    def test_cancelled_ticket_checkin(self):
        unique = 'abcyttdfdfsssdf'
        Ticket.objects.create(student_id=self.student_id, unique_id=unique,
                              activity=Activity.objects.get(id=self.activity.id),
                              status=Ticket.STATUS_CANCELLED)
        self.client.post('/api/a/login', {'username':'llp16', 'password':'666'})
        response = self.client.post('/api/a/activity/checkin', {'actId': self.activity.id, 'ticket': unique})
        self.assertNotEqual(json.loads(response.content.decode())['code'], 0)






