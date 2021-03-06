from django.db import models

from codex.baseerror import *


class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, db_index=True)

    @classmethod
    def get_by_openid(cls, openid):
        try:
            return cls.objects.get(open_id=openid)
        except cls.DoesNotExist:
            raise LogicError('User not found')


class Activity(models.Model):
    name = models.CharField(max_length=128)
    key = models.CharField(max_length=64, db_index=True)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    place = models.CharField(max_length=256)
    book_start = models.DateTimeField(db_index=True)
    book_end = models.DateTimeField(db_index=True)
    total_tickets = models.IntegerField()
    status = models.IntegerField()
    pic_url = models.CharField(max_length=256)
    remain_tickets = models.IntegerField()

    STATUS_DELETED = -1
    STATUS_SAVED = 0
    STATUS_PUBLISHED = 1

    @classmethod
    def get_by_id(cls, search_id):
        try:
            return cls.objects.get(id=int(search_id))
        except cls.DoesNotExist:
            raise LogicError('Activity not found')

    @classmethod
    def get_all_activities(cls):

        """
        返回所有活动
        """
        try:
            return cls.objects.all()
        except cls.DoesNotExist:
            raise LogicError('Activity not found')


class Ticket(models.Model):
    student_id = models.CharField(max_length=32, db_index=True)
    unique_id = models.CharField(max_length=64, db_index=True, unique=True)
    activity = models.ForeignKey(Activity)
    status = models.IntegerField()

    @classmethod
    def get_by_unique_id(cls, search_unique_id):
        try:
            return cls.objects.get(unique_id=search_unique_id)
        except cls.DoesNotExist:
            raise LogicError('Ticket not found')

    @classmethod
    def get_by_activity_and_student_number(cls, act_id, stu_id):
        try:
            return cls.objects.filter(activity=Activity.get_by_id(act_id)).filter(student_id=stu_id)
        except cls.DoesNotExist:
            raise LogicError('Ticket not found')

    @classmethod
    def count_used_tickets(cls, search_activity_id):
        return len(cls.objects.filter(activity_id=search_activity_id).filter(status=Ticket.STATUS_USED))

    @classmethod
    def get_user_tickets(cls, student_id):
        """
        返回此用户的所有票
        """
        try:
            return cls.objects.all().filter(student_id=student_id)
        except cls.DoesNotExist:
            raise LogicError('Activity not found')

    STATUS_CANCELLED = 0
    STATUS_VALID = 1
    STATUS_USED = 2
