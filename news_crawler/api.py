import json
import logging
from collections import namedtuple
from operator import attrgetter, itemgetter

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from lxml import html

from news_crawler.models import Comment, RedditUser, Submision
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
        msg['state'] = 'ko'
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
            get_and_process_user_page.delay(sub.submitter_url, sub.submitter)
            get_and_process_comments_page.delay(sub.comments_url, sub)

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
        msg['state'] = 'ko'
        msg['error_message'] = 'An error has ocrred: {}'.format(res.reason)
        msg['message'] = 'I only scaned {} pages'.format(loop)
    else:
        msg['message'] = 'All submissions has been processed'
        msg['state'] = 'ok'

    msg['pages_processed'] = loop
    msg['statistics_urls'] = {
        'top10_articles': reverse('get_top10_articles'),
        'top10_discussions': reverse('get_top10_discussions'),
        'top10': reverse('get_top10_all'),
        'top_submitters': reverse('get_top_submitters'),
        'top_commenters': reverse('get_top_commenters'),
        'top_active': reverse('get_top_active'),
        'top10_valued_users': reverse('get_top_valued')
    }
    msg['users_info'] = {
        'user_posts': reverse('get_user_posts', args=['_user_name']),
        'user_posts_comented': reverse('get_user_posts_commented', args=['_user_name']),
        'user_karma': reverse('get_user_karma', args=['_user_name'])
    }
    return JsonResponse(msg, status=200, safe=False)


def get_top10_articles(request):
    msg = {}
    if request.method != 'GET':
        msg['state'] = 'ko'
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
        msg['state'] = 'ko'
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
        msg['state'] = 'ko'
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


def get_user_posts(request, user):
    res = {}
    if request.method != 'GET':
        res['state'] = 'ko'
        res['message'] = 'Invalid method'
        return JsonResponse(res, status=200)

    try:
        user = RedditUser.objects.get(name=user)
    except ObjectDoesNotExist as e:
        res['state'] = 'ko'
        res['message'] = 'User does not exist'
        return JsonResponse(res, status=200)

    posts = Submision.objects.filter(submitter=user)
    res['posts'] = [to_json(post) for post in posts]
    res['state'] = 'ok'
    return JsonResponse(res, status=200, safe=False)


def get_user_posts_commented(request, user):
    res = {}
    if request.method != 'GET':
        res['state'] = 'ko'
        res['message'] = 'Invalid method'
        return JsonResponse(res, status=200)

    try:
        user = RedditUser.objects.get(name=user)
    except ObjectDoesNotExist as e:
        res['state'] = 'ko'
        res['message'] = 'User does not exist'
        return JsonResponse(res, status=200)

    comments = Comment.objects.filter(author=user)
    submisions_id = comments.values_list('submission', flat=True).distinct()
    posts = Submision.objects.filter(
        id__in=submisions_id
    )
    res['posts'] = [to_json(post) for post in posts]
    res['state'] = 'ok'
    return JsonResponse(res, status=200, safe=False)


def get_user_karma(request, user):
    res = {}
    if request.method != 'GET':
        res['state'] = 'ko'
        res['message'] = 'Invalid method'
        return JsonResponse(res, status=200)

    try:
        user = RedditUser.objects.get(name=user)
    except ObjectDoesNotExist as e:
        res['state'] = 'ko'
        res['message'] = 'User does not exist'
        return JsonResponse(res, status=200)

    res['karma'] = user.post_karma
    res['state'] = 'ok'
    return JsonResponse(res, status=200, safe=False)


def get_top_submitters(request):
    res = {}
    if request.method != 'GET':
        res['state'] = 'ko'
        res['message'] = 'Invalid method'
        return JsonResponse(res, status=200)

    try:
        count = int(request.GET.get('count'))
    except:
        count = None

    posts = [
        {'user':user.name, 'posts': user.submissions.count()}
        for user in RedditUser.objects.all()
    ]
    posts = sorted(posts, key=itemgetter('posts'), reverse=True)[:count]
    res['state'] = 'ok'
    res['top_submiters'] = posts
    return JsonResponse(res, status=200, safe=False)


def get_top_commenters(request):
    res = {}
    if request.method != 'GET':
        res['state'] = 'ko'
        res['message'] = 'Invalid method'
        return JsonResponse(res, status=200)

    try:
        count = int(request.GET.get('count'))
    except:
        count = None

    posts = [
        {'user': user.name, 'comments': user.comments.count()}
        for user in RedditUser.objects.all()
    ]
    posts = sorted(posts, key=itemgetter('comments'), reverse=True)[:count]
    res['state'] = 'ok'
    res['top_commenters'] = posts
    return JsonResponse(res, status=200, safe=False)


def get_top_active(request):
    res = {}
    if request.method != 'GET':
        res['state'] = 'ko'
        res['message'] = 'Invalid method'
        return JsonResponse(res, status=200)

    try:
        count = int(request.GET.get('count'))
    except:
        count = None

    users = [
        {'user': user.name, 'active_criteria': user.comments.count() + user.submissions.count()}
        for user in RedditUser.objects.all()
    ]

    users = sorted(users, key=itemgetter('active_criteria'), reverse=True)[:count]
    res['state'] = 'ok'
    res['top_valued'] = users
    return JsonResponse(res, status=200, safe=False)

def get_top_valued(request):
    res = {}
    count = 10
    if request.method != 'GET':
        res['state'] = 'ko'
        res['message'] = 'Invalid method'
        return JsonResponse(res, status=200)

    users = [
        {'user': user.name, 'most_valued': user.post_karma + user.comment_karma}
        for user in RedditUser.objects.all() if user.post_karma and user.comment_karma
    ]
    users = sorted(users, key=itemgetter('most_valued'), reverse=True)[:count]
    res['state'] = 'ok'
    res['top_valued'] = users
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
