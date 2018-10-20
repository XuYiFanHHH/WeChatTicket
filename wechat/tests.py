from django.test import TestCase
from wechat.views import *
from wechat.handlers import *
from wechat.models import *
import datetime

# Create your tests here.


# 简单的Handler测试
class SimpleHandlerTest(TestCase):

    # 帮助测试
    def test_help_or_subscribe_handler_check(self):
        handler = HelpOrSubscribeHandler(view=CustomWeChatView, msg={}, user={})
        handler.input = {
            "MsgType": "text",
            "Content": "帮助"
        }
        self.assertTrue(handler.check())

        handler.input = {
            "MsgType": "text",
            "Content": "help"
        }
        self.assertTrue(handler.check())

        handler.input = {
            "MsgType": "event",
            "Event": "CLICK",
            "EventKey": 'SERVICE_HELP',
        }
        self.assertTrue(handler.check())

        handler.input = {
            "MsgType": "event",
            "Event": "scan"
        }
        self.assertTrue(handler.check())

        handler.input = {
            "MsgType": "event",
            "Event": "subscribe"
        }
        self.assertTrue(handler.check())

    # 绑定测试
    def test_bind_account_handler_check(self):
        handler = BindAccountHandler(view=CustomWeChatView, msg={}, user={})
        handler.input = {
            "MsgType": "text",
            "Content": "绑定"
        }
        self.assertTrue(handler.check())

        handler.input = {
            "MsgType": "event",
            "Event": "CLICK",
            "EventKey": 'SERVICE_BIND',
        }
        self.assertTrue(handler.check())

    # 解绑测试
    def test_unbind_or_unsubscribe_handler_check(self):
        handler = UnbindOrUnsubscribeHandler(view=CustomWeChatView, msg={}, user={})
        handler.input = {
            "MsgType": "text",
            "Content": "解绑"
        }
        self.assertTrue(handler.check())

        handler.input = {
            "MsgType": "event",
            "Event": "unsubscribe"
        }
        self.assertTrue(handler.check())

    # 绑定用户抢啥测试
    def test_book_list_handler_success_check(self):
        user_ = User.objects.create(open_id="123", student_id="2016010649")
        handler = BookListHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "抢啥"
        }
        self.assertTrue(handler.check())

        handler.input = {
            "MsgType": "event",
            "Event": "CLICK",
            "EventKey": 'SERVICE_BOOK_WHAT',
        }
        self.assertTrue(handler.check())

    # 未绑定用户抢啥测试
    def test_book_list_handler_fail_check(self):
        user_ = User.objects.create(open_id="123", student_id="")
        handler = BookListHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "抢啥"
        }
        self.assertFalse(handler.check())

        handler.input = {
            "MsgType": "event",
            "Event": "CLICK",
            "EventKey": 'SERVICE_BOOK_WHAT',
        }
        self.assertFalse(handler.check())


# 抢票测试
class TicketBookHandlerTest(TestCase):
    # 初始化
    def setUp(self):
        User.objects.create(open_id="1", student_id="")
        User.objects.create(open_id="2", student_id="2016010649")
        self.saved_activity = Activity.objects.create(
            name='saved',
            key='saved',
            description='桌游',
            start_time=datetime.datetime.fromtimestamp(1539844241),
            end_time=datetime.datetime.fromtimestamp(1539844945),
            place='THU ',
            book_start=datetime.datetime.fromtimestamp(1539844345),
            book_end=datetime.datetime.fromtimestamp(1539844545),
            total_tickets=11,
            pic_url='www.baidu.com',
            remain_tickets=11,
            status=Activity.STATUS_SAVED,
        )
        self.published_activity = Activity.objects.create(
            name='published',
            key='published',
            description='桌游',
            start_time=datetime.datetime.fromtimestamp(1539844241),
            end_time=datetime.datetime.fromtimestamp(1539844945),
            place='THU ',
            book_start=datetime.datetime.fromtimestamp(1539844345),
            book_end=datetime.datetime.fromtimestamp(1539844545),
            total_tickets=11,
            pic_url='www.baidu.com',
            remain_tickets=10,
            status=Activity.STATUS_PUBLISHED,
        )
        self.no_ticket_activity = Activity.objects.create(
            name='noticket',
            key='noticket',
            description='桌游',
            start_time=datetime.datetime.fromtimestamp(1539844241),
            end_time=datetime.datetime.fromtimestamp(1539844945),
            place='THU ',
            book_start=datetime.datetime.fromtimestamp(1539844345),
            book_end=datetime.datetime.fromtimestamp(1539844545),
            total_tickets=11,
            pic_url='www.baidu.com',
            remain_tickets=0,
            status=Activity.STATUS_PUBLISHED,
        )

    # 未绑定用户check测试
    def test_not_bind_book_check(self):
        user_ = User.objects.get(open_id='1')
        handler = TicketBookHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "抢票 saved",
        }
        self.assertFalse(handler.check())

    # 绑定用户check测试
    def test_bind_book_check(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketBookHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "抢票 saved",
        }
        self.assertTrue(handler.check())

    # 绑定用户抢票时无此活动handler测试
    def test_no_activity_book_handle(self):
        user_ = User.objects.get(open_id='2')
        Activity.objects.all().delete()
        handler = TicketBookHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "抢票 saved",
        }
        self.assertEqual(handler.status(), TicketBookHandler.STATUS_NO_ACTIVITY)

    # 绑定用户抢票时票已空handler测试
    def test_no_activity_book_handle(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketBookHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "抢票 noticket",
        }
        self.assertEqual(handler.status(), TicketBookHandler.STATUS_NO_TICKET)

    # 绑定用户抢票时已拥有票
    def test_has_ticket_book_handle(self):
        user_ = User.objects.get(open_id='2')
        Ticket.objects.create(student_id=user_.student_id,
                              unique_id="test",
                              activity=self.published_activity,
                              status=Ticket.STATUS_VALID)
        handler = TicketBookHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "抢票 published",
        }
        self.assertEqual(handler.status(), TicketBookHandler.STATUS_HAS_GOT)

    # 綁定用戶成功买票
    def test_get_ticket_book_handle(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketBookHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "抢票 published",
        }
        self.assertEqual(handler.status(), TicketBookHandler.STATUS_VALID)


# 查票测试
class TicketDetailHandleTest(TestCase):
    # 初始化
    def setUp(self):
        User.objects.create(open_id="1", student_id="")
        User.objects.create(open_id="2", student_id="2016010649")
        self.published_activity = Activity.objects.create(
            name='published',
            key='published',
            description='桌游',
            start_time=datetime.datetime.fromtimestamp(1539844241),
            end_time=datetime.datetime.fromtimestamp(1539844945),
            place='THU ',
            book_start=datetime.datetime.fromtimestamp(1539844345),
            book_end=datetime.datetime.fromtimestamp(1539844545),
            total_tickets=11,
            pic_url='www.baidu.com',
            remain_tickets=10,
            status=Activity.STATUS_PUBLISHED,
        )

    # 未绑定用户check测试
    def test_not_bind_detail_check(self):
        user_ = User.objects.get(open_id='1')
        handler = TicketDetailHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "取票 saved",
        }
        self.assertFalse(handler.check())

    # 绑定用户check测试
    def test_bind_detail_check(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketDetailHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "取票 saved",
        }
        self.assertTrue(handler.check())


# 退票测试
class TicketReturnHandleTest(TestCase):
    # 初始化
    def setUp(self):
        User.objects.create(open_id="1", student_id="")
        User.objects.create(open_id="2", student_id="2016010649")
        self.published_activity = Activity.objects.create(
            name='published',
            key='published',
            description='桌游',
            start_time=datetime.datetime.fromtimestamp(1539844241),
            end_time=datetime.datetime.fromtimestamp(1539844945),
            place='THU ',
            book_start=datetime.datetime.fromtimestamp(1539844345),
            book_end=datetime.datetime.fromtimestamp(1539844545),
            total_tickets=11,
            pic_url='www.baidu.com',
            remain_tickets=10,
            status=Activity.STATUS_PUBLISHED,
        )

    # 未绑定用户check测试
    def test_not_bind_return_check(self):
        user_ = User.objects.get(open_id='1')
        handler = TicketReturnHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "退票 published",
        }
        self.assertFalse(handler.check())

    # 绑定用户check测试
    def test_bind_return_check(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketReturnHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "退票 published",
        }
        self.assertTrue(handler.check())

    # 绑定用户退票时未输入活动名handler测试
    def test_no_activity_name_return_handle(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketReturnHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "退票",
        }
        self.assertEqual(handler.status(), TicketReturnHandler.STATUS_NOT_FIND)

    # 绑定用户退票时输入不存在的活动名handler测试
    def test_no_activity_return_handle(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketReturnHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "退票 sdafas",
        }
        self.assertEqual(handler.status(), TicketReturnHandler.STATUS_NO_ACTIVITY)

    # 绑定用户退票时输入其从未拥有过票的活动名handler测试
    def test_no_ticket_return_handle(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketReturnHandler(view=CustomWeChatView, msg={}, user=user_)
        handler.input = {
            "MsgType": "text",
            "Content": "退票 published",
        }
        self.assertEqual(handler.status(), TicketReturnHandler.STATUS_NO_TICKET)

    # 绑定用户退票时输入其已经退票的活动名handler测试
    def test_has_cancel_ticket_return_handle(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketReturnHandler(view=CustomWeChatView, msg={}, user=user_)
        Ticket.objects.create(student_id=user_.student_id,
                              unique_id="test",
                              activity=self.published_activity,
                              status=Ticket.STATUS_CANCELLED)
        handler.input = {
            "MsgType": "text",
            "Content": "退票 published",
        }
        self.assertEqual(handler.status(), TicketReturnHandler.STATUS_NOT_LEGAL)

    # 绑定用户退票时输入其已经使用的活动名handler测试
    def test_has_been_used_return_handle(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketReturnHandler(view=CustomWeChatView, msg={}, user=user_)
        Ticket.objects.create(student_id=user_.student_id,
                              unique_id="test",
                              activity=self.published_activity,
                              status=Ticket.STATUS_USED)
        handler.input = {
            "MsgType": "text",
            "Content": "退票 published",
        }
        self.assertEqual(handler.status(), TicketReturnHandler.STATUS_NOT_LEGAL)

    # 绑定用户成功退票handler测试
    def test_success_return_handle(self):
        user_ = User.objects.get(open_id='2')
        handler = TicketReturnHandler(view=CustomWeChatView, msg={}, user=user_)
        Ticket.objects.create(student_id=user_.student_id,
                              unique_id="test",
                              activity=self.published_activity,
                              status=Ticket.STATUS_VALID)
        handler.input = {
            "MsgType": "text",
            "Content": "退票 published",
        }
        self.assertEqual(handler.status(), TicketReturnHandler.STATUS_VALID)



