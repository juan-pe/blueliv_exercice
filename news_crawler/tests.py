import os

import requests
import vcr
from django.conf import settings
from django.test import TestCase
from lxml import html

from news_crawler.models import RedditUser, Submision
from news_crawler.utils import *

CASSETES_DIR = os.path.join(settings.BASE_DIR, 'news_crawler/fixtures/vcr_cassettes/')


class PruebaConceptoTest(TestCase):
    
    def setUp(self):
        with vcr.use_cassette(CASSETES_DIR + 'reddit_python.yaml'):
            self.response = requests.get(settings.PYTHON_SUBREDDIT_URL, verify=False)

    # @vcr.use_cassette(self.CASSETES_DIR + 'reddit_python.yaml')
    def test_save_submision_db(self):
        # response = requests.get(settings.PYTHON_SUBREDDIT_URL, verify=False)
        self.assertEqual(self.response.status_code, 200)

        dom = html.fromstring(self.response.content)
        submissions = dom.cssselect('#siteTable > div.thing')

        process_submission(submissions[1])

        submission = Submision.objects.first()
        self.assertIsNotNone(submission)

    # @vcr.use_cassette(self.CASSETES_DIR + 'reddit_python.yaml')
    def test_get_or_create_user(self):
        dom = html.fromstring(self.response.content)
        submissions = dom.cssselect('#siteTable > div.thing')

        user = get_submision_submitter(submissions[1])
        redit_user = RedditUser.objects.first()
        self.assertIsNotNone(redit_user)
        self.assertEqual(user.name, redit_user.name)
