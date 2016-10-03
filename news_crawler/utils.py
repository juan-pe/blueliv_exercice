from datetime import datetime

from django.db.models import Q

from news_crawler.models import RedditUser, Submision

__all__ = ['process_submission', 'get_submision_title', 'get_submision_submitter',
           'get_submision_url', 'get_submision_creation_date', 'get_submision_creation_date',
           'get_submision_punctuation', 'get_submision_punctuation', 'get_submision_rank',
           'get_submisions_comments']

def process_submission(submision):
    '''
    Function that from a python subreddit submision extract:
        - submisions title
        - externals url
        - discusion url
        - submitter
        - punctiation
        - creation_date
        - number_of_comments
    and save them into db
    '''
    sub = {}
    sub['submision_title'] = get_submision_title(submision)

    if 'self' not in submision.get('class'):
        sub['external_url'] = get_submision_url(submision)
    else:
        sub['discusion_url'] = get_submision_url(submision)

    sub['submitter'] = get_submision_submitter(submision)
    sub['punctiation'] = get_submision_punctuation(submision)
    sub['rank'] = get_submision_rank(submision)
    sub['creation_date'] = get_submision_creation_date(submision)
    sub['number_of_comments'] = get_submisions_comments(submision)

    qsub = Q(submitter=sub['submitter'], submision_title=sub['submision_title'])
    try:
        submisions = Submision.objects.filter(qsub)
        if submisions.exists():
            submisions.update(**sub)
        else:
            Submision.objects.create(**sub)
    except Exception as e:
        print(e)


def get_submision_title(submision):
    title_fields = submision.cssselect('a[class^="title"]')
    return title_fields[0].text if title_fields else ''


def get_submision_url(submision):
    return submision.get('data-url')


def get_submision_submitter(submision):
    author = submision.get('data-author')
    return RedditUser.objects.get_or_create(name=author)[0]


def get_submision_creation_date(submision):
    time_stamp = submision.get('data-timestamp')
    return datetime.utcfromtimestamp(int(time_stamp)/1000)


def get_submision_punctuation(submision):
    punctiation_elem = submision.cssselect('[class="score unvoted"]')

    if punctiation_elem and punctiation_elem[0].text != u'•':
        return int(punctiation_elem[0].text)

    return 0


def get_submision_rank(submision):
    return submision.get('data-rank')


def get_submisions_comments(submision):
    comments = submision.cssselect('li > a[class~="comments"]')
    if comments:
        if len(comments[0].text.split(' ')) > 2:
            return int(comments[0].text.split(' ')[0])
    return 0
