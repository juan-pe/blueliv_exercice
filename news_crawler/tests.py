import json
import os
from datetime import datetime
from inspect import getmembers, isfunction
from operator import itemgetter

import requests
import vcr
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from lxml import html

from news_crawler import api
from news_crawler.models import RedditUser, Submision
from news_crawler.utils import *

CASSETES_DIR = os.path.join(settings.BASE_DIR, 'news_crawler/fixtures/vcr_cassettes/')


class PruebaConceptoTest(TestCase):

    def setUp(self):
        with vcr.use_cassette(CASSETES_DIR + 'reddit_python.yaml'):
            self.response = requests.get(settings.PYTHON_SUBREDDIT_URL, verify=False)

        self.assertEqual(self.response.status_code, 200)
        dom = html.fromstring(self.response.content)
        self.submissions = dom.cssselect('#siteTable > div.thing')

    def test_save_submision_db(self):
        process_submission(self.submissions[1])
        sub_title = self.submissions[1].cssselect('a[class^="title"]')[0].text
        submission = Submision.objects.first()

        self.assertIsNotNone(submission, msg='No submissions founded')
        self.assertEqual(submission.title, sub_title, msg='Titles dont match')

    def test_get_or_create_user(self):
        user = get_submision_submitter(self.submissions[1])
        redit_user = RedditUser.objects.first()

        self.assertIsNotNone(redit_user, msg='No users founded')
        self.assertEqual(user.name, redit_user.name, msg='User names dont match')

    def test_get_submission_title(self):
        sub_title = self.submissions[1].cssselect('a[class^="title"]')[0].text
        title = get_submision_title(self.submissions[1])

        self.assertEqual(sub_title, title, msg='Titles dont match')

    def test_get_submission_url(self):
        sub_url = self.submissions[1].get('data-url')
        url = get_submision_url(self.submissions[1])

        self.assertEqual(sub_url, url, msg='Urls dont match')

    def test_get_creation_date(self):
        time_stamp = int(self.submissions[1].get('data-timestamp'))
        sub_creation_date = datetime.utcfromtimestamp(time_stamp/1000)
        creation_date = get_submision_creation_date(self.submissions[1])

        self.assertEqual(sub_creation_date, creation_date, msg='Dates dont match')

    def test_get_submission_punctuation(self):
        punctuation_elem = self.submissions[1].cssselect('[class="score unvoted"]')
        if punctuation_elem and punctuation_elem[0].text != u'•':
            sub_punctuation = int(punctuation_elem[0].text)
        else:
            sub_punctuation = 0
        punctuation = get_submision_punctuation(self.submissions[1])

        self.assertEqual(sub_punctuation, punctuation, msg="punctuations dont match")

    def test_get_submission_rank(self):
        sub_rank = self.submissions[1].get('data-rank')
        sub_rank = int(sub_rank) if sub_rank else 0
        rank = get_submision_rank(self.submissions[1])

        self.assertEqual(sub_rank, rank, msg="ranks dont match")

    def test_get_submission_comments(self):
        comments_elem = self.submissions[1].cssselect('li > a[class~="comments"]')
        if comments_elem and len(comments_elem[0].text.split(' ')) == 2:
            sub_comments = int(comments_elem[0].text.split(' ')[0])
        else:
            sub_comments = 0
        comments = get_submisions_comments(self.submissions[1])

        self.assertEqual(sub_comments, comments, msg='comments dont match')

    def test_get_comments_url(self):
        comments_elem = self.submissions[1].cssselect('li > a[class~="comments"]')
        sub_comment_url = comments_elem[0].get('href') if comments_elem  else ''
        comment_url = get_comments_url(self.submissions[1])

        self.assertEqual(sub_comment_url, comment_url, msg='comments url dont match')

    def test_get_submiter_url(self):
        submitter_url_elem = self.submissions[1].cssselect('p > a[class~="author"]')
        sub_submitter_url = submitter_url_elem[0].get('href') if submitter_url_elem else ''
        submitter_url = get_submitter_url(self.submissions[1])

        self.assertEqual(sub_submitter_url, submitter_url, msg='commiter url dont match')


class TestApi(TestCase):

    def setUp(self):

        with vcr.use_cassette(CASSETES_DIR + 'reddit_python.yaml'):
            self.response = requests.get(settings.PYTHON_SUBREDDIT_URL, verify=False)

        self.assertEqual(self.response.status_code, 200)
        dom = html.fromstring(self.response.content)
        self.submissions = dom.cssselect('#siteTable > div.thing')

        # Populate db with the submissions in the cassette
        for submission in self.submissions:
            process_submission(submission)

        self.client = Client()
        self.functions = [member_name for member_name, member_type in getmembers(api) if isfunction(member_type) and 'top' in member_name]


    def test_get_top10_articles_discussions_all_withoutget_parameter(self):

        for function in self.functions:
            response = self.client.get(reverse(function))
            self.assertEqual(response.status_code, 200)

            articles = json.loads(response.content.decode('utf-8'))
            self.assertEqual(len(articles), 10)

            for article in articles:
                if function == 'get_top10_articles':
                    self.assertIsNotNone(article['external_url'])
                    self.assertIsNone(article['discusion_url'])
                elif function == 'get_top10_discussions':
                    self.assertIsNone(article['external_url'])
                    self.assertIsNotNone(article['discusion_url'])
    def test_get_top10_articles_discussions_all_withoutget_parameter_default_order(self):
        for function in self.functions:
            response = self.client.get(reverse(function))
            articles = json.loads(response.content.decode('utf-8'))

            self.assertTrue(self._asc_order(articles))

    def test_get_top10_articles_discussions_all_point_parameter_and_order(self):
        for function in self.functions:
            response = self.client.get(reverse(function), {'order_by': 'points'})
            self.assertEqual(response.status_code, 200)

            articles = json.loads(response.content.decode('utf-8'))
            self.assertEqual(len(articles), 10)

            for article in articles:
                if function == 'get_top10_articles':
                    self.assertIsNotNone(article['external_url'])
                    self.assertIsNone(article['discusion_url'])
                elif function == 'get_top10_discussions':
                    self.assertIsNone(article['external_url'])
                    self.assertIsNotNone(article['discusion_url'])

            self.assertTrue(self._desc_order(articles))

    def test_get_top10_articles_discussions_all_comment_parameter_and_order(self):
        for function in self.functions:
            response = self.client.get(reverse(function), {'order_by': 'comments'})
            self.assertEqual(response.status_code, 200)

            articles = json.loads(response.content.decode('utf-8'))
            self.assertEqual(len(articles), 10)

            for article in articles:
                if function == 'get_top10_articles':
                    self.assertIsNotNone(article['external_url'])
                    self.assertIsNone(article['discusion_url'])
                elif function == 'get_top10_discussions':
                    self.assertIsNone(article['external_url'])
                    self.assertIsNotNone(article['discusion_url'])

            self.assertTrue(self._desc_order(articles))

    def test_get_top10_articles_discussions_all_incorrect_parameter(self):
        for function in self.functions:
            response = self.client.get(reverse(function), {'order_by': 'asds%$'})
            self.assertEqual(response.status_code, 400)

    def test_get_top10_articles_discussions_all_incorrect_method(self):
        for function in self.functions:
            response = self.client.post(reverse(function), {'order_by': 'asds%$'})
            self.assertEqual(response.status_code, 400)


    def _asc_order(self, list_of_dict):
        return all(first['rank'] <= first['rank'] for first, second in zip(list_of_dict, list_of_dict[1:]))

    def _desc_order(self, list_of_dict):
        return all(first['rank'] >= first['rank'] for first, second in zip(list_of_dict, list_of_dict[1:]))
