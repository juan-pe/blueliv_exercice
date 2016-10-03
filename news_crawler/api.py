import logging

import requests
from django.conf import settings
from django.http.response import JsonResponse
from lxml import html

from news_crawler.utils import process_submission

logger = logging.getLogger(__name__)


def get_submissions(request, pages):
    msg = {}
    if request.method != 'GET':
        msg['error_message'] = 'Invalid Method'
        return JsonResponse(msg, status=400)

    res = requests.get(settings.PYTHON_SUBREDDIT_URL, verify=False)
    next_link = True
    loop = 0
    while loop < int(pages) and res.status_code == 200 and next_link:
        dom = html.fromstring(res.content)
        submissions = dom.cssselect('#siteTable > div.thing')
        for submission in submissions:
            process_submission(submission)

        loop += 1
        if loop < int(pages):
            next_link = dom.xpath('//a[@rel="nofollow next"]')
            if next_link:
                res = requests.get(next_link[0].get('href'),
                                   verify=False,
                                   allow_redirects=True)
        else:
            next_link = False


    if res.status_code != 200:
        msg['error_message'] = 'An error has ocrred: {}'.format(res.reason)
    else:
        msg['message'] = '{} pages of submissions has been processed'.format(loop)
    return JsonResponse(msg, status=200)
