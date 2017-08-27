import datetime
import json
import re

import requests
import time

from models import Congress, Paper, db


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
    page = 0
    n_paper = 0
    print(f'Started populate paper at: {datetime.datetime.now()}')
    while True:
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
        response = requests.get('http://ieeexplore.ieee.org/search/searchresult.jsp')
        cookies = response.cookies

        response = requests.post(url, json=payload, headers=headers, cookies=cookies)
        papers = json.loads(response.text)['records']
        if (page % 10) == 0:
            db.commit()
            print(f'committed : {page}')
            print(f'insert {n_paper} rows')
        if len(papers) <= 0:
            db.commit()
            print(f'{datetime.datetime.now()}- Finished, populated with {n_paper} papers')
            break

        for p in papers:

            Paper.get_or_create(title=p['title'], abstract=p.get('abstract', ''),
                                finalScore=0., accepted=True)
            n_paper += 1
