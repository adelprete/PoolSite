from django.test import TestCase

class TestingTheTest(TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(),'FBO')
