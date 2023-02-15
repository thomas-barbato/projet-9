"""import"""
from django.test import TestCase
from .models import Ticket, Review, UserFollows
from django.contrib.auth.models import User
from django.db.utils import IntegrityError


class ReviewTest(TestCase):
    fixtures = ["user.json", "review.json", "userfollows.json", "ticket.json"]

    def setUp(self):
        print("hello setUp")
        # get all from fixtures directories
        self.user = User.objects.get(username="test")
        self.user2 = User.objects.get(username="test2")
        self.ticket = Ticket.objects.get(title="un titre", user_id=self.user.id)
        self.review = Review.objects.get(ticket_id=self.ticket.id, user_id=self.user.id)
        self.userfollows = UserFollows.objects.get(
            followed_user_id=self.user2.id, user_id=self.user.id
        )

    def tearDown(self):
        print("hello tearDown")

    def test_user_success(self):
        assert User.objects.count() == 2
        print("user success")
        self.assertTrue(True)

    def test_user_username_len(self):
        try:
            self.user.username = "a" * 150
            self.assertLessEqual(
                len(self.user.username), 128, "username len is too large"
            )
        except AssertionError as assert_e:
            print(assert_e)

    def test_user_password_len(self):
        try:
            self.assertGreaterEqual(
                len(self.user.password), 8, "Your password len is too short."
            )
        except AssertionError as assert_e:
            print(assert_e)

    def test_ticket_success(self):
        assert Ticket.objects.count() == 1
        print("ticket success")
        self.assertTrue(True)

    @staticmethod
    def test_ticket_title_fail():
        try:
            Ticket.objects.create(title=None)
        except IntegrityError as e:
            print(f"ticket fail, {e}")

    def test_review_success(self):
        assert Review.objects.count() == 1
        print("review success")
        self.assertTrue(True)

    def test_userFollow_success(self):
        assert UserFollows.objects.count() >= 1
        print("userFollow success")
        self.assertTrue(True)

    def raise_error(self, instance):
        return ord(instance.user_id), ord(instance.followed_user_id)

    def test_userFollow_fail(self):
        with self.assertRaises(ValueError):
            u = UserFollows(user_id="a", followed_user_id="azdadzazd").save()
            uid, fuid = self.raise_error(u)
            u.user_id = uid
            u.followed_user_id = fuid
            u.save()

    def test_exception(self):
        with self.assertRaises(IndexError):
            index = ["1"]
            print(index[1])
