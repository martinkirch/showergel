import random
from datetime import datetime, timedelta
from . import ShowergelTestCase

LIQUIDSOAP_DATEFORMAT = r"%Y/%m/%d %H:%M:%S"

with open("/usr/share/dict/words") as words_file:
    WORDS = words_file.read().splitlines()

def artistic_generator():
    return ' '.join([WORDS[random.randint(0, len(WORDS))] for i in range(2)])


class TestMetadataLog(ShowergelTestCase):

    def test_metadata_log(self):
        tracktime = timedelta(minutes=3)
        now = datetime.now()
        resp = self.app.post_json('/metadata_log', {
            'on_air': now.strftime(LIQUIDSOAP_DATEFORMAT),
            'artist': artistic_generator(),
            'title': artistic_generator(),
            'source': 'test',
        })
        
        now += tracktime
        last = {
            'on_air': now.strftime(LIQUIDSOAP_DATEFORMAT),
            'artist': artistic_generator(),
            'title': artistic_generator(),
            'source': 'test',
            'source_url': "http://check.its.renamed/to/initial_uri"
        }
        # make it robust to repeated posts
        resp = self.app.post_json('/metadata_log', last)
        resp = self.app.post_json('/metadata_log', last)
        resp = self.app.post_json('/metadata_log', last)

        logged = self.app.get('/metadata_log').json['metadata_log']
        self.assertEqual(2, len(logged))
        
        # check source_url is used as initial_uri
        last['initial_uri'] = last['source_url']
        del last['source_url']
        self.assertDictEqual(last, logged[0])

        # at least on_air is required
        resp = self.app.post_json('/metadata_log', {}, status=400)
