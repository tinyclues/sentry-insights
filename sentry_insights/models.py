"""
sentry_insights.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Linovia, see AUTHORS for more details.
:copyright: (c) 2014 by tinyclues, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms
from django.conf import settings

from sentry.plugins.bases.notify import NotifyPlugin

import sentry_hipchat

import requests
import json
import logging


DEFAULT_ENDPOINT = "https://insights-collector.newrelic.com/v1/accounts/{account_id}/events"


class InsightsOptionsForm(forms.Form):
    account_id = forms.CharField(help_text="Your insights account id.")
    key = forms.CharField(help_text="Your insights key.")
    event_type = forms.CharField(help_text="The event type.")


class InsightsMessage(NotifyPlugin):
    author = 'Boris Feld'
    author_url = 'https://github.com/tinyclues/sentry-insights'
    version = sentry_hipchat.VERSION
    description = "Event notification to Insights."
    resource_links = [
        ('Bug Tracker', 'https://github.com/tinyclues/sentry-insights/issues'),
        ('Source', 'https://github.com/tinyclues/sentry-insights'),
    ]
    slug = 'insights'
    title = 'Insights'
    conf_title = title
    conf_key = 'insights'
    project_conf_form = InsightsOptionsForm

    def is_configured(self, project):
        return all((self.get_option(k, project) for k in ('account_id', 'key', 'event_type')))

    def on_alert(self, alert, **kwargs):
        project = alert.project
        account_id = self.get_option('account_id', project)
        key = self.get_option('key', project)
        event_type = self.get_option('event_type', project)

        if account_id and key and event_type:

            self.send_payload(account_id, key, event_type, alert)

    def notify_users(self, group, event, fail_silently=False):
        pass
        # project = event.project
        # token = self.get_option('token', project)
        # room = self.get_option('room', project)
        # notify = self.get_option('notify', project) or False
        # include_project_name = self.get_option('include_project_name', project) or False
        # level = group.get_level_display().upper()
        # link = group.get_absolute_url()
        # endpoint = self.get_option('endpoint', project) or DEFAULT_ENDPOINT


        # if token and room:
        #     self.send_payload(
        #         endpoint=endpoint,
        #         token=token,
        #         room=room,
        #         message='[%(level)s]%(project_name)s %(message)s [<a href="%(link)s">view</a>]' % {
        #             'level': level,
        #             'project_name': (' <strong>%s</strong>' % project.name) if include_project_name else '',
        #             'message': event.error(),
        #             'link': link,
        #         },
        #         notify=notify,
        #         color=COLORS.get(level, 'purple'),
        #     )

    def send_payload(self, account_id, key, event_type, alert):

        endpoint = DEFAULT_ENDPOINT.format(account_id=account_id)

        values = {
            'eventType': event_type,
        }

        values.update(alert.__dict__)

        headers = {'content-type': 'application/json',
                   'X-Insert-Key': key}
        result = requests.post(endpoint, data=json.dumps([values]),
                               headers=headers)
        try:
            result.raise_for_status()
        except:
            logger = logging.getLogger('sentry.plugins.insights')
            logger.error('Event was not sent to insights',
                         exc_info=True, extra={'data': {'payload': values}})
