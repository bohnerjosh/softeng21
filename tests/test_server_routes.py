import pytest
import requests
from requests.auth import HTTPBasicAuth

# This test requires a server to be running locally on port 5000.
# Start the server before running the tests using './run-server.sh'.
# Note that it would be really cool to automate this, too, in the
# future, to where this test script would check port 5000 to see
# if anything is listening, and then if not, manually start the server
# and then kill the server at this script's completion.
# Maybe some day!
base_url = 'http://localhost:5000'


@pytest.fixture(scope="function")
def diarykey():
    result = requests.post('{}/api/init'.format(base_url),
                           data={
                                'diaryname': 'new_diary',
                                'username': 'test_user',
                           })
    r = result.json()

    yield r['key']

    result = requests.delete('{}/api/wipe'.format(base_url),
                             auth=HTTPBasicAuth(r['key'], ''),
                             data={})


def test_log(diarykey):
    result = requests.post('{}/api/log'.format(base_url),
                           auth=HTTPBasicAuth(diarykey, ''),
                           data={
                                'text': 'This is a test.',
                           })
    r = result.json()
    assert r.get('result') == 'ok'


def test_rm(diarykey):
    test_log(diarykey)

    result = requests.delete('{}/api/rm/1/'.format(base_url),
                             auth=HTTPBasicAuth(diarykey, ''))
    r = result.json()
    assert r.get('result') == 'ok'


def test_list(diarykey):
    # Add two log entries.
    text_contents = ['Text 1', 'Text 2']

    for text in text_contents:
        result = requests.post('{}/api/log'.format(base_url),
                               auth=HTTPBasicAuth(diarykey, ''),
                               data={
                                    'text': text,
                               })
        r = result.json()
        assert r.get('result') == 'ok'

    # Get the list of posts.  It should contain only two.
    result = requests.get('{}/api/list'.format(base_url),
                          auth=HTTPBasicAuth(diarykey, ''))

    entries = result.json().get('result')

    assert len(entries) == 2

    for entry in entries:
        entry['text'] = entry['text'].strip()
        if entry['text'] in text_contents:
            text_contents.remove(entry['text'])

    assert text_contents == []


def test_verify_success(diarykey):
    result = requests.get('{}/api/verify'.format(base_url),
                          auth=HTTPBasicAuth(diarykey, ''),
                          data={})
    r = result.json()
    assert r['result'] == 'ok'
    assert r['diaryname'] == 'new_diary'


def test_verify_fail():
    bogus_key = 'bogus_key'
    result = requests.get('{}/api/verify'.format(base_url),
                          auth=HTTPBasicAuth(bogus_key, ''),
                          data={})
    r = result.json()
    assert r['result'] == 'error'
