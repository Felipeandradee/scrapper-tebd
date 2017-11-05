import datetime
import json
import re

import requests
import time

from models import Congress, Paper, db, Review


def create_tables():
    if not Congress.table_exists():
        Congress.create_table()

    if not Paper.table_exists():
        Paper.create_table()


def congress():

    url = 'http://www.globaleventslist.elsevier.com/controls/events_list_control.ashx?a=true&_t='
    page = 0
    n_congress = 0
    print(f'Started populate congress at: {datetime.datetime.now()}')
    while True:
        page += 1
        print(f'Request page {page}')
        payload = {
            'page': page,
            'sortBy': 'recency'
        }
        response = requests.post(url + str(int(time.time())), payload)
        conferences = json.loads(response.text)['results']
        if (page % 10) == 0:
            db.commit()
            print(f'committed : {page}')
            print(f'insert {n_congress} rows')
        if len(conferences) <= 0:
            db.commit()
            print(f'{datetime.datetime.now()}- Finished, populated with {n_congress} congress')
            break

        for conference in conferences:
            name = conference['Name']
            data_str = re.search('(\d+)', conference['DateStart']).group(1)
            submission_deadline = datetime.datetime.fromtimestamp(int(data_str[:10]))
            review_deadline = submission_deadline + datetime.timedelta(days=10)

            Congress.get_or_create(name=name, submissionDeadline=submission_deadline.date(),
                                   reviewDeadline=review_deadline.date())
            n_congress += 1


def paper():
    url = 'http://ieeexplore.ieee.org/rest/search'
    page = 31501
    n_paper = 0
    print(f'Started populate paper at: {datetime.datetime.now()}')

    print("Request search page for get cookies.")
    response = requests.get('http://ieeexplore.ieee.org/search/searchresult.jsp')
    cookies = response.cookies
    while True:
        try:
            page += 1
            print(f'Request page {page}')
            payload = {
                'pageNumber': str(page),
            }
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json;charset=UTF-8',
                'Content-Length': '18',
                'Accept-Language': 'en-US,en;q=0.8,pt;q=0.6',
                'Referer': 'http://ieeexplore.ieee.org/search/searchresult.jsp',
                'Origin': 'http://ieeexplore.ieee.org',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/60.0.3112.113 Safari/537.36',

            }

            response = requests.post(url, json=payload, headers=headers, cookies=cookies, timeout=15)

            papers = json.loads(response.text)['records']
            if (page % 150) == 0:
                db.commit()
                print(f'committed at: {page}')
                print(f'insert {n_paper} rows')
                print("Request search page for get cookies.")
                response = requests.get('http://ieeexplore.ieee.org/search/searchresult.jsp')
                cookies = response.cookies
            if len(papers) <= 0:
                db.commit()
                print(f'{datetime.datetime.now()}- Finished, populated with {n_paper} papers')
                break

            for p in papers:

                if p.get('title'):
                    Paper.create(title=p['title'], abstract=p.get('abstract', ''),
                                        finalScore=0., accepted=True)
                    n_paper += 1

        except Exception as e:
            print(f'{datetime.datetime.now()} - Error: {e} \nretry in 30 seconds')
            time.sleep(30)
            continue


def update_paper():
    all_papers = Paper.select()
    counter = 0
    for p in all_papers:
        counter += 1
        reviews = Review.select().where(Review.idPaper == p.paperId)
        num_reviews = len(reviews)
        sum_score = sum([r.score for r in reviews])
        avg_score = int(sum_score / num_reviews)
        p.finalScore = int(sum_score/num_reviews)
        if num_reviews < 3 or avg_score < 7:
            p.accepted = False
        p.save()

        if (counter % 10000) == 0:
            print(f"{counter} papers updated")





