#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import datetime

from db import db_session
from extract_id_title_url import get_webcompat_data
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = 'sqlite:////tmp/test.db'

Base = declarative_base()
Base.query = db_session.query_property()


class Issue(Base):
    '''Issue database class.'''
    __tablename__ = 'webcompat_issues'
    id = Column(String(128), unique=True, primary_key=True)
    summary = Column(String(256))
    url = Column(String(1024))
    domain = Column(String(1024))
    body = Column(String(2048))
    state = Column(String(128))
    creation_time = Column(DateTime)
    last_change_time = Column(DateTime)

    def __init__(self, id, summary, url, domain, body, state, creation_time, last_change_time):
        self.id = id
        self.summary = summary
        self.url = url
        self.domain = domain
        self.body = body
        self.state = state
        self.creation_time = datetime.datetime.strptime(creation_time.split('Z')[0],
                                                             "%Y-%m-%dT%H:%M:%S")
        self.last_change_time = datetime.datetime.strptime(last_change_time.split('Z')[0],
                                                             "%Y-%m-%dT%H:%M:%S")



def main():
    '''Core program.'''
    engine = create_engine(DB_PATH, convert_unicode=True)
    Base.metadata.create_all(bind=engine)
    live = False
    if live:
        data = get_webcompat_data()[1]
    else:
        f = open('webcompatdata-bzlike.json', 'r')
        data = json.load(f)
        f.close()
    # stuff data into database..
    for bug in data['bugs']:
        db_session.add(
            Issue(bug['id'], bug['summary'], bug['url'], extract_domain_name(bug['url']), bug['body'], bug['state'], bug['creation_time'], bug['last_change_time']))
    db_session.commit()


if __name__ == "__main__":
    main()
