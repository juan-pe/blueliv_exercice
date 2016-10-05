import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from lxml import html

from news_crawler.models import Comment, RedditUser, Submision
from news_crawler.utils import (get_user_comment_karma, get_user_karma,
                                process_comment)

logger = get_task_logger(__name__)


@shared_task
def get_and_process_comments_page(url, submission):
    msg = 'Getting comments from submision ({}): {}'
    logger.info(msg.format(url, submission.title))

    headers = {'user-agent': settings.AGENT}
    res = requests.get(url, headers=headers, verify=False)

    if res.status_code == 200:
        dom = html.fromstring(res.content)
        comments = dom.cssselect('div[class~="comment"] > div[class="entry unvoted"]')
        for comment in comments:
            c = process_comment(comment, submission)

        return {'state': 'ok'}

    logger.info('requests failed: {}'.format(res.reason))
    return {'state': 'ko'}


@shared_task
def get_and_process_user_page(url, submitter):
    msg = 'Getting user karma ({}): {}'
    logger.info(msg.format(url, submitter.name))

    headers = {'user-agent': settings.AGENT}
    res = requests.get(url, headers=headers, verify=False)

    if res.status_code == 200:
        dom = html.fromstring(res.content)
        submitter.post_karma = get_user_karma(dom)
        submitter.comment_karma = get_user_comment_karma(dom)
        submitter.save()
        return {'state': 'ok'}

    logger.info('requests failed: {}'.format(res.reason))
    return {'state': 'ko'}
