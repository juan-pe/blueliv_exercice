
# NEWS CRAWLER

This peace of software is a news crawler of the Python subreddit website. It's recollect some attributes from posts, comments and users and stores them into a SQlite database and exposes an API to access to that data and statistics

## Design concept

### Framework
The basis software of the project is the framework **Django**. Why Django?, because is a very potent tool that has an very complete ORM and model management become very easy. On the other hand, Django may be is a little big and can be 'heavy', but with some tricks can be very lightweight.

### Paralelism
The basic idea of this news crawler is scrap the Python subreddit website. That is a heavy task, so to address the problem I decided to decompose it in 3 tasks. One to scrap a single page, other to scan the commentaries pages and other to scan user pages. The first one is synchronous. Because how are structured the pagination in the Python subreddit website, for every page, we have to get the "next link". So if we have to scann 10 pages, under the scrapping solution (after we will see that may be there is an alternative) we have to go page by page.
On the other hand, the other two tasks are concurrent, for every commentary link or user link a task is launched to get it.
To achieve this I use **Celery** because is easy and very configurable and for batch tasks i think goes very well.

## Implementation
Except the point 1 of the bonus point, in a rigorous way, i implemented all of them, why?, why not.
Here is the API to address them:

### Obtain submissions [GET /api/v1/submissions/{pages}]
Analyze `pages` submissions

+ Parameters
    + pages (required, integer) - Number of pages to analyze.

+ Response 200 (application/json)
If the request works without error, the body of the response is like following:

    + Body

			{
			    "pages_processed": 1,
			    "users_info": {
			        "user_karma": "/api/v1/user/\_user_name/karma",
			        "user_posts_comented": "/api/v1/user/\_user_name/posts_commented",
			        "user_posts": "/api/v1//user/\_user_name/posts"
			    },
			    "message": "All submissions has been processed",
			    "state": "ok"
			    "statistics_urls": {
			        "top10_valued_users": "/api/v1//statistics/most_valued/top10",
			        "top10_discussions": "/api/v1/submissions/discussions/top10",
			        "top_submitters": "/api/v1/statistics/submitters/top",
			        "top_commenters": "/api/v1/statistics/commenters/top",
			        "top10_articles": "/api/v1/submissions/articles/top10",
			        "top_active": "/api/v1//statistics/most_active/top",
			        "top10": "/api/v1/submissions/all/top10"
			    }
			}
In case some page request didn't work, the process stops and the resultant body of the response is quite similar, except `state` that will be *"ko"* and `message` will be *"I only scaned **pages** pages"*.

+ Response 400 (application/json)
If the request is made with other method distinct of GET, this is the body for that request.

    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


### Obtain top10 article submissions [GET /api/v1/submissions/articles/top10?order_by={criteria}]
Obtain the top10 articles submissions order by comments or points. If no order criteria is provides, the articles are ordered by rank.

+ Parameters
    + order_by (string, optional) - Criteria order. Can be `points` or `comments`


+ Response 200 (application/json)

    + Body:

			[
			    {
			        "external_url": "https://www.cheatography.com/davechild/cheat-sheets/python/",
			        "comments_url": "https://www.reddit.com/r/Python/comments/55ym3j/python_cheat_sheet/",
			        "submitter_id": 27,
			        "discusion_url": null,
			        "submitter_url": "https://www.reddit.com/user/liranbh",
			        "rank": 1,
			        "creation_date": "2016-10-05T09:11:19",
			        "number_of_comments": 18,
			        "submitter": "liranbh",
			        "title": "Python Cheat Sheet",
			        "id": 27,
			        "punctuation": 69
			    },
			    {
			        "external_url": "http://www.discoversdk.com/blog/python-image-processing-with-opencv",
			        "comments_url":   "https://www.reddit.com/r/Python/comments/560ix4/python_image_processing_with_opencv/",
			        "submitter_id": 27,
			        "discusion_url": null,
			        "submitter_url": "https://www.reddit.com/user/liranbh",
			        "rank": 3,
			        "creation_date": "2016-10-05T17:03:26",
			        "number_of_comments": 0,
			        "submitter": "liranbh",
			        "title": "Python Image Processing With OpenCV",
			        "id": 29,
			        "punctuation": 10
			    },
			    .....
			]


+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


+ Response 400 (application/json) 
If the `order_by` has a different value than `points` or `comments`
    + Body

            {
                "state" = "ko"
                "error_message" = "Incorrect order criteria"
            }


### Obtain top10 discussions submissions [GET /api/v1/submissions/discussions/top10?order_by={criteria}]
Obtain the top10 articles discussions order by comments or points. If no order criteria is provides, the articles are ordered by rank.

+ Parameters
    + order_by (string, optional) - Criteria order. Can be `points` or `comments`


+ Response 200 (application/json)

    + Body:

			[
			    {
			        "submitter_url": "https://www.reddit.com/user/aphoenix",
			        "number_of_comments": 43,
			        "submitter": "aphoenix",
			        "id": 26,
			        "external_url": null,
			        "punctuation": 299,
			        "discusion_url": "/r/Python/comments/3kestk/post_learning_questions_to_rlearnpython/",
			        "comments_url": "https://www.reddit.com/r/Python/comments/3kestk/post_learning_questions_to_rlearnpython/",
			        "rank": 0,
			        "submitter_id": 1,
			        "creation_date": "2015-09-10T15:19:36",
			        "title": "Post learning questions to /r/LearnPython"
			    },
			    {
			        "submitter_url": "https://www.reddit.com/user/nilsgarland",
			        "number_of_comments": 15,
			        "submitter": "nilsgarland",
			        "id": 28,
			        "external_url": null,
			        "punctuation": 11,
			        "discusion_url": "/r/Python/comments/560gov/flask_or_django/",
			        "comments_url": "https://www.reddit.com/r/Python/comments/560gov/flask_or_django/",
			        "rank": 2,
			        "submitter_id": 28,
			        "creation_date": "2016-10-05T16:51:39",
			        "title": "Flask or Django?"
			    },
			    .....
			]


+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


+ Response 400 (application/json) 
If the `order_by` has a different value than `points` or `comments`
    + Body

            {
                "state" = "ko"
                "error_message" = "Incorrect order criteria"
            }

### Obtain all submissions [GET /api/v1/submissions/all/top10?order_by={criteria}]
Obtain the top10 of all kind of submissions (discussions and articles)

+ Parameters
    + order_by (string, optional) - Criteria order. Can be `points` or `comments`


+ Response 200 (application/json)

    + Body:

			[
			    {
			        "submitter_url": "https://www.reddit.com/user/aphoenix",
			        "number_of_comments": 43,
			        "submitter": "aphoenix",
			        "id": 26,
			        "external_url": null,
			        "punctuation": 299,
			        "discusion_url": "/r/Python/comments/3kestk/post_learning_questions_to_rlearnpython/",
			        "comments_url": "https://www.reddit.com/r/Python/comments/3kestk/post_learning_questions_to_rlearnpython/",
			        "rank": 0,
			        "submitter_id": 1,
			        "creation_date": "2015-09-10T15:19:36",
			        "title": "Post learning questions to /r/LearnPython"
			    },
			    {
			        "submitter_url": "https://www.reddit.com/user/nilsgarland",
			        "number_of_comments": 15,
			        "submitter": "nilsgarland",
			        "id": 28,
			        "external_url": null,
			        "punctuation": 11,
			        "discusion_url": "/r/Python/comments/560gov/flask_or_django/",
			        "comments_url": "https://www.reddit.com/r/Python/comments/560gov/flask_or_django/",
			        "rank": 2,
			        "submitter_id": 28,
			        "creation_date": "2016-10-05T16:51:39",
			        "title": "Flask or Django?"
			    },
			    .....
			]


+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


+ Response 400 (application/json) 
If the `order_by` has a different value than `points` or `comments`
    + Body

            {
                "state" = "ko"
                "error_message" = "Incorrect order criteria"
            }

### Obtain all posts from a user [GET /api/v1/{user}/posts]
This method obtain all posts that a user has made. (In the set of submissions that we scanned)

+ Parameters
    + user (string, required) - Name of the user


+ Response 200 (application/json)
If the call to the method goes fine, the response is a list whit all posts that the user specified has made.
    + Body:

			{
			    "state": "ok",
			    "posts": [
			        {
			            "title": "0b1001 ways to solve Roman Numerals",
			            "external_url": null,
			            "number_of_comments": 4,
			            "discusion_url": "/r/Python/comments/55tno7/0b1001_ways_to_solve_roman_numerals/",
			            "comments_url": "https://www.reddit.com/r/Python/comments/55tno7/0b1001_ways_to_solve_roman_numerals/",
			            "id": 26,
			            "punctuation": 3,
			            "submitter_id": 25,
			            "submitter": "AlexOduvan",
			            "creation_date": "2016-10-04T14:11:43",
			            "submitter_url": "https://www.reddit.com/user/AlexOduvan",
			            "rank": 37
			        }
			    ]
			}


+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


+ Response 400 (application/json) 
In case that the `user` parameter hat somethig wrong or user does not exists, the method return the following body
    + Body

            {
                "state" = "ko"
                "error_message" = "User does not exist"
            }
            
### Obtain all posts commented from a user [GET /api/v1/{user}/posts_commented]
This method obtain all posts that a user commented. (In the set of submissions that we scanned)

+ Parameters
    + user (string, required) - Name of the user


+ Response 200 (application/json)
If the call to the method goes fine, the response is a list whit all posts that the user has commented
    + Body:

			{
			    "state": "ok",
			    "posts": [
			        {
			            "title": "Post learning questions to /r/LearnPython",
			            "external_url": null,
			            "number_of_comments": 43,
			            "discusion_url": "/r/Python/comments/3kestk/post_learning_questions_to_rlearnpython/",
			            "comments_url": "https://www.reddit.com/r/Python/comments/3kestk/post_learning_questions_to_rlearnpython/",
			            "id": 1,
			            "punctuation": 301,
			            "submitter_id": 1,
			            "submitter": "aphoenix",
			            "creation_date": "2015-09-10T15:19:36",
			            "submitter_url": "https://www.reddit.com/user/aphoenix",
			            "rank": 0
			        },
			        {
			            "title": "0b1001 ways to solve Roman Numerals",
			            "external_url": null,
			            "number_of_comments": 4,
			            "discusion_url": "/r/Python/comments/55tno7/0b1001_ways_to_solve_roman_numerals/",
			            "comments_url": "https://www.reddit.com/r/Python/comments/55tno7/0b1001_ways_to_solve_roman_numerals/",
			            "id": 26,
			            "punctuation": 1,
			            "submitter_id": 25,
			            "submitter": "AlexOduvan",
			            "creation_date": "2016-10-04T14:11:43",
			            "submitter_url": "https://www.reddit.com/user/AlexOduvan",
			            "rank": 37
			        }
			    ]
			}


+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


+ Response 400 (application/json) 
In case that the `user` parameter hat somethig wrong or user does not exists, the method return the following body
    + Body

            {
                "state" = "ko"
                "error_message" = "User does not exist"
            }


### Obtain user karma [GET /api/v1/{user}/karma]
Return users posts karma.

+ Parameters
    + user (string, required) - Name of the user


+ Response 200 (application/json)
If the call to the method goes fine, the response is the followinf dictionary
    + Body:

			{
		        "karma": 97,
		        "state": "ok"
			}


+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


+ Response 400 (application/json) 
In case that the `user` parameter hat somethig wrong or user does not exists, the method return the following body
    + Body

            {
                "state" = "ko"
                "error_message" = "User does not exist"
            }

### Obtain top submitters [GET /api/v1/statistics/submitters/top?count={}]
Obtain a list of users order by the number of submissions that they have done.

+ Parameters
    + count (integer, optional) - Number of submitters to show


+ Response 200 (application/json)
If the call to the method goes fine, the response is like the following dictionary. In this case, the top3 submitters.
    + Body:

			{
			    "top_submiters": [
			        {
			            "user": "liranbh",
			            "posts": 5
			        },
			        {
			            "user": "elisebreda",
			            "posts": 5
			        },
			        {
			            "user": "krshowsdotcom",
			            "posts": 3
			        }
			    ],
			    "state": "ok"
			}

+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }

### Obtain top submitters [GET /api/v1/statistics/commenters/top?count={}]
Obtain a list of users order by the number of comments that they have done.

+ Parameters
    + count (integer, optional) - Number of commenters to show


+ Response 200 (application/json)
If the call to the method goes fine, the response is like the following dictionary. In this case, the top3 commenters.
    + Body:

			{
			    "state": "ok",
			    "top_commenters": [
			        {
			            "user": "kurashu89",
			            "comments": 107
			        },
			        {
			            "user": "ilikebigsandwiches",
			            "comments": 76
			        },
			        {
			            "user": "Jajoo",
			            "comments": 75
			        }
			    ]
			}	

+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


### Obtain top submitters [GET /api/v1/statistics/most_active/top?count={}]
Obtain a list of most active users. The criteria for determinate which user is most active that other is the sum of number of comments plus number of submissions.

+ Parameters
    + count (integer, optional) - Number of users to show


+ Response 200 (application/json)
If the call to the method goes fine, the response is like the following dictionary. In this case, the top3 most active users are:
    + Body:

			{
			    "state": "ok",
			    "top_valued": [
			        {
			            "active_criteria": 108,
			            "user": "kurashu89"
			        },
			        {
			            "active_criteria": 76,
			            "user": "ilikebigsandwiches"
			        },
			        {
			            "active_criteria": 75,
			            "user": "markusmeskanen"
			        }
			    ]
			}			

+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }


### Obtain top submitters [GET /api/v1/statistics/most_valued/top10]
Obtain a list of most valued users. The criteria used to determinate which user is most valued than other is the sum of his karmas (posts karma and comment karma)


+ Response 200 (application/json)
If the call to the method goes fine, the response is like the following dictionary. 
    + Body:

			{
			    "state": "ok",
			    "top_valued": [
				    {
				        "most_valued": 486184,
				        "user": "TotesMessenger"
				    },
				    {
				        "most_valued": 299957,
				        "user": "ameoba"
				    },
			        .....
			    ]
			}			

+ Response 400 (application/json)
If the request is made with other method different than GET:
    + Body

            {
                "state" = "ko"
                "error_message" = "Invalid Method"
            }

##Tests
To be sure that everything is still working after make changes, I decide integrate Travis CI. Under this URL one can see the state of the builds (https://travis-ci.org/juan-pe/blueliv_exercice)

## Model design
In the application are modeled three models. One for the submissions, other for the users and the last one for the comments. 
#### RedditUser model
| Attributes    | Type (Django models Fields)|
|---------      |------                      |
| name          | CharField                  |
| post_karma    | IntegerField               |
| comment_karma | IntegerField               |

#### Submission model
| Attributes         | Type (Django models Fields)|
|---------           |------                      |
| submitter          | ForeingKey(RedditUser)     |
| external_url       | UrlField                   |
| discusion_url      | UrlField                   |
| comments_url       | UrlField                   |
| submitter_url      | UrlField                   |
| punctuation        | IntegerField               |
| number_of_comments | IntegerField               |
| creation_date      | DatetimeField              |

#### Comment model
| Attributes    | Type (Django models Fields)| 
|---------      |------                      |
| author        | ForeingKey(RedditUser)     |
| submission    | ForeingKey(Submission)     |
| text          | TextField                  |
| punctiation   | IntegerField               |
| creation_date | DatetimeField              |

## Install code
This code has been tested with python3.4 and 3.5
### Requisits
To run this code a  [Redis server](http://redis.io)  is required.  For a Ubuntu flavor distribution:
```bash
$> sudo apt-get install redis-server 
$> sudo service redis-server start
```

For OSX, we can use brew to install it

```bash
$> brew install redis
$> redis-server /usr/local/etc/redis.conf
```

Also `virtualenv` is necessary.  If we haven't:

- In Ubuntu:
```bash
$> sudo apt-get install python-virtualenv
```
- In OSX:
If we have python installed, virtualenv is also installed, in case not:
```bash
$> brew install pyenv-virtualenv
```

Once we have this requirements installed, we can create and activave our virtual environment were our code run:
```bash
$> mkdir $HOME/venvs
$> virtualenv -p python3 $HOME/venvs/news_crawler
$> source $HOME/venvs/news_crawler/bin/activate
```
### Installation
After activate our virtualenv, we have to clone the code and install the necessary requirements.
```bash
(news_crawler) $> git clone git@github.com:juan-pe/blueliv_exercice.git
(news_crawler) $> cd blueliv_exercice
(news_crawler) $> git checkout master
(news_crawler) $> pip install requirements/base.txt
```
When the installation of the requirements is done, we have to start celery and wake up the server.
```bash
 (news_crawler) $> celery -A blueliv_exercice worker -l info -c 10 &
 (news_crawler) $> ./manage.py start_server
```
Under `http://localhost:8000` we can start make requests


## Final considerations
After implement lots of things, I found that there is an library implemented in Python to interact with Reddit called [PRAW](https://praw.readthedocs.io/en/stable/). Thinking in efficiency, a refactor to use this library in necessary, to provide a better service and don't reinvent the wheel again.
