import json
import os
from datetime import datetime
from inspect import getmembers, isfunction
from operator import itemgetter

import requests
import vcr
from dateutil import parser
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from lxml import html

from news_crawler import api
from news_crawler.models import Comment, RedditUser, Submision
from news_crawler.tasks import (get_and_process_comments_page,
                                get_and_process_user_page)
from news_crawler.utils import *

CASSETES_DIR = os.path.join(settings.BASE_DIR, 'news_crawler/fixtures/vcr_cassettes/')


class SubmissionsUtilsTest(TestCase):

    def setUp(self):
        headers = {'user-agent': settings.AGENT}
        with vcr.use_cassette(CASSETES_DIR + 'reddit_python_submissions.yaml'):
            self.response = requests.get(settings.PYTHON_SUBREDDIT_URL,
                                         headers=headers,
                                         verify=False)

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

        self.assertEqual(sub_comment_url, comment_url, msg='comments url doesnt match')

    def test_get_submiter_url(self):
        submitter_url_elem = self.submissions[1].cssselect('p > a[class~="author"]')
        sub_submitter_url = submitter_url_elem[0].get('href') if submitter_url_elem else ''
        submitter_url = get_submitter_url(self.submissions[1])

        self.assertEqual(sub_submitter_url, submitter_url, msg='commiter url doesnt match')


class KarmaUtilsTest(TestCase):

    def setUp(self):
        headers = {'user-agent': settings.AGENT}
        url = 'https://www.reddit.com/user/iapitus'
        with vcr.use_cassette(CASSETES_DIR + 'reddit_python_user.yaml'):
            self.response = requests.get(url,
                                         headers=headers,
                                         verify=False)

        self.assertEqual(self.response.status_code, 200)
        self.dom = html.fromstring(self.response.content)

    def test_get_user_comment_karma(self):
        user_commment_karma_elem = self.dom.cssselect('div > span[class="karma comment-karma"]')
        self.assertIsNotNone(user_commment_karma_elem)

        dom_user_commment_karma = int(user_commment_karma_elem[0].text.replace(',', ''))
        user_commment_karma = get_user_comment_karma(self.dom)

        self.assertEqual(dom_user_commment_karma, user_commment_karma, msg='user coments karma doesnt match')

    def test_get_user_karma(self):
        user_karma_elem = self.dom.cssselect('div > span[class="karma"]')
        self.assertIsNotNone(user_karma_elem)

        dom_user_karma = int(user_karma_elem[0].text.replace(',', ''))
        user_karma = get_user_karma(self.dom)

        self.assertEqual(dom_user_karma, user_karma, msg='user coments karma doesnt match')


class CommentsUtilsTest(TestCase):

    def setUp(self):
        headers = {'user-agent': settings.AGENT}
        url = 'https://www.reddit.com/r/Python/comments/55y1v7/python_shells/'
        with vcr.use_cassette(CASSETES_DIR + 'reddit_python_comments.yaml'):
            self.response = requests.get(url,
                                         headers=headers,
                                         verify=False)

        self.assertEqual(self.response.status_code, 200)
        dom = html.fromstring(self.response.content)
        self.comments = dom.cssselect('div[class~="comment"] > div[class="entry unvoted"]')

    def test_get_comment_author(self):
        comment = self.comments[1]
        author_elem = comment.cssselect('p > a[class~="author"]')
        self.assertIsNotNone(author_elem)

        comment_author = author_elem[0].text
        author_obj, _ = RedditUser.objects.get_or_create(name=comment_author)
        author = get_comment_author(comment)
        self.assertEqual(author_obj.name, author.name)


    def test_get_comment_text(self):
        comment = self.comments[1]
        comment_text_elem = comment.cssselect('div[class~="usertext-body"] > div[class="md"]')
        self.assertIsNotNone(comment_text_elem)

        comment_text = comment_text_elem[0].text_content().strip()
        text = get_comment_text(comment)
        self.assertEqual(comment_text, text)

    def test_get_comment_punctuation(self):
        comment = self.comments[1]
        comment_punctuation_elem = comment.cssselect('p > span[class="score unvoted"]')
        self.assertIsNotNone(comment_punctuation_elem)

        comment_punctuation = int(comment_punctuation_elem[0].text.split(' ')[0])
        punctuation = get_comment_punctuation(comment)
        self.assertEqual(comment_punctuation, punctuation)


    def test_get_comment_creation_date(self):
        comment = self.comments[1]
        comment_creation_date_elem = comment.cssselect('p > time[class="live-timestamp"]')
        self.assertIsNotNone(comment_creation_date_elem)

        comment_creation_date = parser.parse(comment_creation_date_elem[0].get('datetime'), ignoretz=True)
        creation_date = get_comment_creation_date(comment)
        self.assertEqual(comment_creation_date, creation_date)

    def test_process_comment(self):
        comment = self.comments[1]


class TestApi(TestCase):

    def setUp(self):

        with vcr.use_cassette(CASSETES_DIR + 'reddit_python_submissions.yaml'):
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


class TestTasks(TestCase):

    def setUp(self):
        with vcr.use_cassette(CASSETES_DIR + 'reddit_python_submissions.yaml'):
            self.response = requests.get(settings.PYTHON_SUBREDDIT_URL, verify=False)

        self.assertEqual(self.response.status_code, 200)
        dom = html.fromstring(self.response.content)
        submissions = dom.cssselect('#siteTable > div.thing')

        self.comments = dom.cssselect(
            'div[class~="comment"] > div[class="entry unvoted"]')

        for submission in submissions:
            process_submission(submission)

        self.submissions = Submision.objects.all()

    def test_get_and_process_user_page_task(self):
        sub = self.submissions.first()
        res = get_and_process_user_page(sub.submitter_url, sub.submitter)

        self.assertEquals(res.get('state'), 'ok')

    def test_get_and_process_comments_page_task(self):
        sub = self.submissions.first()
        res = get_and_process_comments_page(sub.comments_url, sub)

        self.assertEquals(res.get('state'), 'ok')
