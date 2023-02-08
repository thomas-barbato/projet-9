"""import"""
from django.test import TestCase
from .models import Ticket, Review, UserFollows
from django.contrib.auth.models import User
from django.db.utils import IntegrityError


# Create your tests here.
class ReviewTest(TestCase):
    fixtures = ["user.json", "review.json", "userfollows.json", "ticket.json"]
    # this fun start everytime
    # i made a test.
    # can be used to
    # create fake user (eg)

    def setUp(self):
        """docstring"""
        print("hello setUp")
        # get all from fixtures directories
        self.user = User.objects.get(username="test")
        self.user2 = User.objects.get(username="test2")
        self.ticket = Ticket.objects.get(title="un titre", user_id=self.user.id)
        self.review = Review.objects.get(
            ticket_id=self.ticket.id, user_id=self.user.id
        )
        self.userfollows = UserFollows.objects.get(
            followed_user_id=self.user2.id, user_id=self.user.id
        )

    # fun executed at the end of
    # a test
    def tearDown(self):
        """docstring"""
        print("hello tearDown")

    def test_user_success(self):
        """docstring"""
        assert User.objects.count() == 2
        print("user success")
        self.assertTrue(True)

    def test_user_username_len(self):
        """docstring"""
        try:
            self.user.username = "a" * 150
            self.assertLessEqual(
                len(self.user.username), 128, "username len is too large"
            )
        except AssertionError as assert_e:
            print(assert_e)

    def test_user_password_len(self):
        """docstring"""
        try:
            # self.user.password = "123"
            self.assertGreaterEqual(
                len(self.user.password), 8, "Your password len is too short."
            )
        except AssertionError as assert_e:
            print(assert_e)

    def test_ticket_success(self):
        """docstring"""
        assert Ticket.objects.count() == 1
        print("ticket success")
        self.assertTrue(True)

    @staticmethod
    def test_ticket_title_fail():
        """docstring"""
        try:
            Ticket.objects.create(title=None)
        except IntegrityError as e:
            print(f"ticket fail, {e}")

    def test_review_success(self):
        """docstring"""
        assert Review.objects.count() == 1
        print("review success")
        self.assertTrue(True)

    def test_userFollow_success(self):
        """docstring"""
        assert UserFollows.objects.count() >= 1
        print("userFollow success")
        self.assertTrue(True)

    # test with assertRaise
    def raise_error(self, instance):
        """docstring"""
        return ord(instance.user_id), ord(instance.followed_user_id)

    def test_userFollow_fail(self):
        """docstring"""
        with self.assertRaises(ValueError):
            u = UserFollows(user_id="a", followed_user_id="azdadzazd").save()
            uid, fuid = self.raise_error(u)
            u.user_id = uid
            u.followed_user_id = fuid
            u.save()

    def test_exception(self):
        """docstring"""
        with self.assertRaises(IndexError):
            index = ["1"]
            print(index[1])
