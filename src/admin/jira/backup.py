import json
import sys

import attr
from eliot import start_action, to_file
import treq
from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks, returnValue

URL = u"https://clusterhq.atlassian.net/rest/api/2/search"


to_file(sys.stderr)


@attr.s(frozen=True)
class HTTPError(Exception):
    """
    A HTTP response had an error code.
    """
    code = attr.ib()
    content = attr.ib()

    def __unicode__(self):
        return repr(self)


@inlineCallbacks
def some_issues(start_at, max_results):
    with start_action(
            action_type=u"admin:jira:backup:some_issues",
            start_at=start_at,
            max_results=max_results
    ):
        params = dict(
            startAtX=start_at,
            maxResults=max_results,
            jql="project=FLOC",
        )
        response = yield treq.post(
            URL,
            json.dumps(params),
            headers={'Content-Type': ['application/json']},
        )
        if response.code != 200:
            content = yield response.content()
            raise HTTPError(response.code, content)
        else:
            content = yield response.json()

    returnValue(content)


@inlineCallbacks
def all_issues():
    issues = []
    start_at = 0
    max_results = 50
    total = None
    while True:
        content = yield some_issues(start_at, max_results)
        new_total = content["total"]
        if total is None:
            total = new_total
        else:
            if total != new_total:
                raise Exception("Total changed", total, new_total)
        next_issues = content['issues']
        if next_issues:
            issues = issues + next_issues
            start_at = start_at + max_results
        else:
            break
    returnValue(issues)


@inlineCallbacks
def backup(reactor):
    issues = yield all_issues()
    sys.stdout.write(json.dumps(issues))
    returnValue(0)


def main():
    raise SystemExit(react(backup))
