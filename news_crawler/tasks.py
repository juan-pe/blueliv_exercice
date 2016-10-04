import requests
from celery import shared_task
from django.conf import settings
from lxml import html

from news_crawler.models import Comments, RedditUser, Submision
from news_crawler.utils import (get_comment_karma, get_user_karma,
                                process_comment)


@shared_task
def get_and_process_comments_page(url, submission):
    headers = {'user-agent': settings.AGENT}
    res = requests.get(url, headers=headers, verify=False)
    if res.status_code == 200:
        dom = html.fromstring(res.content)
        comments = dom.cssselect()
        for comment in comments:
            c = process_comment(comment)


@shared_task
def get_and_process_user_page(url, submitter):
    headers = {'user-agent': settings.AGENT}
    res = requests.get(url, headers=headers, verify=False)
    if res.status_code == 200:
        dom = html.fromstring(res.content)
        submitter.post_karma = get_user_karma(dom)
        submitter.comment_karma = get_comment_karma(dom)
        submitter.save()
