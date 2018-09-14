
"""
RUN THESE COMMANDS FILE IN A HEROKU DJANGO SHELL
$ heroku git:remote -a <prod-deployment>
$ heroku run bash
# In Heroku bash:
$ app/manage.py shell

Paste the following script:
"""

import django
django.setup()

import requests
from os import environ
from cms.models.report import Report

URL = environ['AMP_SERVICE_ENDPOINT'] + 'updateReport'
reports = Report.objects.filter(published=True).order_by('id').values_list('id', flat=True)
total = len(reports)

for num, rid in enumerate(reports, start=1):
    print('{: >5.1f}% - {: >5}/{: <5} - id = {: >5} -'.format(num/total * 100, num, total, rid),
          requests.post(URL, json={'id': rid}).text)
