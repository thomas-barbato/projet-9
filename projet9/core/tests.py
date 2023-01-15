from django.test import TestCase
from .models import *
from django.contrib.auth.models import User
import datetime

# Create your tests here.
class ReviewTest(TestCase):
    # this fun start everytime
    # i made a test.
    # can be used to
    # create fake user (eg)
    def setUp(self):
        print("hello setUp")
        User.objects.create(
            username="test",
            password="passwordtest123*",
            email="email@email.com",
        )
        u = User.objects.get(username="test")

        Ticket.objects.create(
            title="un titre",
            description="une description",
            time_created=datetime.datetime.now(),
            user_id = 1,
        )
        t = Ticket.objects.get(title="un titre")

        Review.objects.create(
            ticket_id=t.id,
            rating=4,
            user_id=u.id,
            headline="Un titre",
            body="un corps de text",
            time_created=datetime.datetime.now()
        )
        UserFollows.objects.create(
            followed_user_id=u.id,
            user_id=u.id
        )
    # fun executed at the end of
    # a test

    def tearDown(self):
        print("hello tearDown")

    def test_user_success(self):
        assert User.objects.count() == 1
        print("user success")
        self.assertTrue(True)

    def test_user_fail(self):
        try:
            u = User(name='1234')
        except Exception as e:
            print(f"user fail, {e}")

    def test_ticket_success(self):
        print("ticket success")
        assert Ticket.objects.count() == 1
        self.assertTrue(True)

    def test_ticket_fail(self):
        try:
            Ticket.objects.create(title=None)
        except Exception as e:
            print(f"ticket fail, {e}")

    def test_review_success(self):
        print("review success")
        assert Review.objects.count() == 1
        self.assertTrue(True)

    def test_review_fail(self):
        try:
            Review(
                rating="",
                headline="Test headline",
                body="Empty body"
            ).save()
        except Exception as e:
            print(f"review fail, {e}")

    def test_userFollow_success(self):
        print("userFollow success")
        assert UserFollows.objects.count() == 1
        self.assertTrue(True)

    def test_userFollow_fail(self):
        try:
            UserFollows(
                user_id = "a",
                followed_user_id = "azdadzazd"
            ).save()
        except Exception as e:
            print(f"userFollow fail, {e}")