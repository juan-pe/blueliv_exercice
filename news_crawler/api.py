import json
import logging
from collections import namedtuple
from operator import attrgetter

import requests
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from lxml import html

from news_crawler.models import Submision
from news_crawler.tasks import (get_and_process_comments_page,
                                get_and_process_user_page)
from news_crawler.utils import process_submission

logger = logging.getLogger(__name__)


def get_submissions(request, pages):
    msg = {}
    next_link = True
    loop = 0
    headers = {'user-agent': settings.AGENT}

    if request.method != 'GET':
        msg['error_message'] = 'Invalid Method'
        return JsonResponse(msg, status=400)

    res = requests.get(settings.PYTHON_SUBREDDIT_URL,
                       headers=headers,
                       verify=False)
    while loop < int(pages) and res.status_code == 200 and next_link:
        dom = html.fromstring(res.content)
        submissions = dom.cssselect('#siteTable > div.thing')
        for submission in submissions:
            sub = process_submission(submission)
            get_and_process_user_page(sub.submitter_url, sub.submitter)
            get_and_process_comments_page(sub.comments_url, sub)

        loop += 1
        if loop < int(pages):
            next_link = dom.xpath('//a[@rel="nofollow next"]')
            if next_link:
                res = requests.get(next_link[0].get('href'),
                                   headers=headers,
                                   verify=False,
                                   allow_redirects=True)
            else:
                next_link = False

    if res.status_code != 200:
        msg['error_message'] = 'An error has ocrred: {}'.format(res.reason)
    else:
        msg['message'] = 'submissions has been processed'

    msg['pages_processed'] = loop
    msg['statistics_urls'] = {
        'top10_articles': reverse('get_top10_articles'),
        'top10_discussions': reverse('get_top10_discussions'),
        'top10': reverse('get_top10_all')
    }
    return JsonResponse(msg, status=200)


def get_top10_articles(request):
    msg = {}
    if request.method != 'GET':
        msg['error_message'] = 'Invalid Method'
        return JsonResponse(msg, status=400)

    order_by = request.GET.get('order_by', 'default')
    if order_by not in ['points', 'comments', 'default']:
        msg['error_message'] = 'Incorrect order criteria'
        return JsonResponse(msg, status=400)

    order_criteria = _get_order_criteria(order_by)

    submissions = Submision.objects.filter(
        external_url__isnull=False,
        discusion_url__isnull=True
    ).order_by(order_criteria)[:10]

    res = [to_json(submission) for submission in submissions]
    return JsonResponse(res, status=200, safe=False)


def get_top10_discussions(request):
    msg = {}
    if request.method != 'GET':
        msg['error_message'] = 'Invalid Method'
        return JsonResponse(msg, status=400)

    order_by = request.GET.get('order_by', 'default')
    if order_by not in ['points', 'comments', 'default']:
        msg['error_message'] = 'Incorrect order criteria'
        return JsonResponse(msg, status=400)

    order_criteria = _get_order_criteria(order_by)

    submissions = Submision.objects.filter(
        external_url__isnull=True,
        discusion_url__isnull=False
    ).order_by(order_criteria)[:10]

    res = [to_json(submission) for submission in submissions]
    return JsonResponse(res, status=200, safe=False)


def get_top10_all(request):
    msg = {}
    if request.method != 'GET':
        msg['error_message'] = 'Invalid Method'
        return JsonResponse(msg, status=400)

    order_by = request.GET.get('order_by', 'default')
    if order_by not in ['points', 'comments', 'default']:
        msg['error_message'] = 'Incorrect order criteria'
        return JsonResponse(msg, status=400)

    order_criteria = _get_order_criteria(order_by)

    submissions = Submision.objects.all().order_by(order_criteria)[:10]

    res = [to_json(submission) for submission in submissions]
    return JsonResponse(res, status=200, safe=False)


def _get_order_criteria(order_by):
    get_criteria = attrgetter(order_by)
    OrderCriteriaTuple = namedtuple(
        'OrderCriteriaTuple',
        'points, comments, default'
    )
    order_criteria = OrderCriteriaTuple('-punctuation', '-number_of_comments', 'rank')

    return get_criteria(order_criteria)


def to_json(submission):
    res = {}
    for field in submission._meta.get_all_field_names():
        if field == 'submitter':
            res[field] = str(submission.__getattribute__(field))
        elif field != 'comments':
            res[field] = submission.__getattribute__(field)
    return res
