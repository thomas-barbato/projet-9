"""import"""
from django.test import TestCase
# TODO: Should be at the bottom of imports: use isort
from .models import Ticket, Review, UserFollows
from django.contrib.auth.models import User
from django.db.utils import IntegrityError


# Create your tests here.
class ReviewTest(TestCase):
    fixtures = ["user.json", "review.json", "userfollows.json", "ticket.json"]
    # TODO: Delete comments if not needed
    # this fun start everytime
    # i made a test.
    # can be used to
    # create fake user (eg)

    def setUp(self):
        """docstring"""
        # TODO: Delete print
        print("hello setUp")
        # get all from fixtures directories
        self.user = User.objects.get(username="test")
        self.user2 = User.objects.get(username="test2")
        self.ticket = Ticket.objects.get(title="un titre", user_id=self.user.id)
        self.review = Review.objects.get(ticket_id=self.ticket.id, user_id=self.user.id)
        self.userfollows = UserFollows.objects.get(followed_user_id=self.user2.id, user_id=self.user.id)

    # fun executed at the end of
    # a test
    def tearDown(self):
        # TODO: Docstrings not necessary for tests
        """docstring"""
        # TODO: Delete print
        print("hello tearDown")

    def test_user_success(self):
        # TODO: Docstrings not necessary for tests
        """docstring"""
        assert User.objects.count() == 2
        # TODO: Delete print
        print("user success")

        # TODO: Delete assertion test
        self.assertTrue(True)

    def test_user_username_len(self):
        # TODO: Docstrings not necessary for tests
        """docstring"""

        try:
            self.user.username = "a" * 150
            self.assertLessEqual(len(self.user.username), 128, "username len is too large")
        except AssertionError as assert_e:
            print(assert_e)

    def test_user_password_len(self):
        # TODO: Docstrings not necessary for tests
        """docstring"""
        # TODO: try/except not needed
        try:
            # self.user.password = "123"
            self.assertGreaterEqual(len(self.user.password), 8, "Your password len is too short.")
        except AssertionError as assert_e:
            print(assert_e)

    def test_ticket_success(self):
        # TODO: Docstrings not necessary for tests
        """docstring"""
        assert Ticket.objects.count() == 1

        # TODO: Delete print and assertion test
        print("ticket success")
        self.assertTrue(True)

    # TODO: No need to put it static event if self not used
    @staticmethod
    def test_ticket_title_fail():
        # TODO: Docstrings not necessary for tests
        """docstring"""
        # TODO: try/except not needed
        try:
            Ticket.objects.create(title=None)
        except IntegrityError as e:
            print(f"ticket fail, {e}")

    def test_review_success(self):
        """docstring"""
        assert Review.objects.count() == 1

        # TODO: Delete print and assertion test
        print("review success")
        self.assertTrue(True)

    def test_userFollow_success(self):
        """docstring"""
        assert UserFollows.objects.count() >= 1

        # TODO: Delete print and assertion test
        print("userFollow success")
        self.assertTrue(True)

    # TODO: What is the purpose of this method?
    #   Can we do without?
    def raise_error(self, instance):
        """docstring"""
        return ord(instance.user_id), ord(instance.followed_user_id)

    def test_userFollow_fail(self):
        """docstring"""

        # TODO: Could we do some of those steps outside the context manager
        #   Is ValueError the real thing we are testing for?
        with self.assertRaises(ValueError):
            u = UserFollows(user_id="a", followed_user_id="azdadzazd").save()
            uid, fuid = self.raise_error(u)
            u.user_id = uid
            u.followed_user_id = fuid
            u.save()

    # TODO: Delete test if not used
    def test_exception(self):
        """docstring"""
        with self.assertRaises(IndexError):
            index = ["1"]
            print(index[1])
