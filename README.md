
# NEWS CRAWLER

This peace of software is a news crawler of the Python subreddit website. It's recollect some attributes from posts, comments and users and stores them into a SQlite database and exposes an API to access to that data and statistics

## Design concept

### Framwork
The basis software of the project is the framwork **Django**. Why Django?, beacuse is a very potent tool that has an very complete ORM and model management become very easy. On the other hand, Django may be is a little big and can be 'heavy', but with some triks can be very lightweith.

### Paralelism
The basic idea of this news crawler is scrap the Python subreddit website. That is a heavy task, so to address the problem I make 3 tasks, one to scrap the a single page, other to scan the commentaries pages and othe to scan user pages. The first one is syncronous. Because how are structured the pagination in the Python subreddit website, for every page, we have to to get the "next link". So if we have to scann 10 pages, under the scrapping solution (after we will see that may be there is an alternative) we have to go page by page.
On the other hand, the other two tasks are concurrent, for every commentaries link or user link i launch a task to get it.
To achieve this I use **Celery** because is easy and very configurable and for batch tasks i think goes very well.

## Implementation
Except the point 1 of the bonus point (in a rigorous way), i implemented all of them, why?, why not.
Here is the API to adress them:

### Obtain submissions [GET /api/v1/submissions/{pages}]

+ Parameters
    + pages: 10 (required, integer) - Number of pages to analyze.


+ Response 200 (application/json)

    + Body

             {
                "pages_processed": 1,
                "users_info": {
                  "user_karma": "/api/v1/user/\_user_name/karma",
                  "user_posts_comented": "/api/v1/user/\_user_name/posts_commented",
                  "user_posts": "/api/v1//user/\_user_name/posts"
                },
                "message": "submissions has been processed",
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


+ Response 400 (application/json)

    + Body

            {
              "state" = "ko"
              "error_message" = "Invalid Method"
            }


### Obtain top10 article submissions [GET /api/v1/submissions/articles/top10?order_by={criteria}]
Obtain the top10 articles submissions order by comments or points. If no order criteria is provides, the articles are ordered by rank

+ Parameters
    + criteria: comments, point


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


+ Response 400 (application/json) (invalid method)

    + Body

            {
              "state" = "ko"
              "error_message" = "Invalid Method"
            }


+ Response 400 (application/json) (invalid criteria)

    + Body

            {
              "state" = "ko"
              "error_message" = "Incorrect order criteria"
            }


### Obtain top10 discussions submissions [GET /api/v1/submissions/discussions/top10?order_by={criteria}]
Obtain the top10 articles discussions order by comments or points. If no order criteria is provides, the articles are ordered by rank

+ Parameters
    + criteria: comments, point


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


+ Response 400 (application/json) (invalid method)

    + Body

            {
              "state" = "ko"
              "error_message" = "Invalid Method"
            }


+ Response 400 (application/json) (invalid criteria)

    + Body

            {
              "state" = "ko"
              "error_message" = "Incorrect order criteria"
            }
