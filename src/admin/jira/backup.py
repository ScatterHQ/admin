import treq
from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks, returnValue

URL = "https://clusterhq.atlassian.net/rest/api/2/search?jql=project=FLOC"


@inlineCallbacks
def backup(reactor):
    response = yield treq.get(URL)
    content = yield response.json()
    print content
    returnValue(0)


def main():
    raise SystemExit(react(backup))
