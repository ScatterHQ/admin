import json
import sys

import treq
from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks, returnValue

URL = u"https://clusterhq.atlassian.net/rest/api/2/search"

@inlineCallbacks
def some_issues(start_at, max_results):
    sys.stderr.write(b"start_at: %i\n" % (start_at,))
    params = dict(
        startAt=start_at,
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
        raise Exception("HTTP error", response.code, content)
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
            sys.stderr.write(b"Total: %i\n" % (new_total,))
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
    sys.stderr.write(
        b"Issue Count: %i\n" % (
            len(issues),
        )
    )
    returnValue(0)


def main():
    raise SystemExit(react(backup))
