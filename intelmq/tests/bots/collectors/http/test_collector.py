# -*- coding: utf-8 -*-
"""
Testing HTTP collector
"""

import unittest

import intelmq.lib.test as test
import intelmq.lib.utils as utils
from intelmq.bots.collectors.http.collector_http import HTTPCollectorBot


OUTPUT = [{"__type": "Report",
           "feed.name": "Example feed",
           "feed.accuracy": 100.,
           "feed.url": "http://localhost/two_files.tar.gz",
           "raw": utils.base64_encode('bar text\n'),
           "extra.file_name": "bar",
           },
          {"__type": "Report",
           "feed.name": "Example feed",
           "feed.accuracy": 100.,
           "feed.url": "http://localhost/two_files.tar.gz",
           "raw": utils.base64_encode('foo text\n'),
           "extra.file_name": "foo",
           },
          ]


@test.skip_local_web()
class TestHTTPCollectorBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for HTTPCollectorBot.
    """

    @classmethod
    def set_bot(cls):
        cls.bot_reference = HTTPCollectorBot
        cls.sysconfig = {'http_url': 'http://localhost/two_files.tar.gz',
                         'extract_files': True,
                         'name': 'Example feed',
                         }

    def test_targz_twofiles(self):
        """ Test if correct Events have been produced. """
        self.input_message = None
        self.run_bot(iterations=1)

        self.assertMessageEqual(0, OUTPUT[0])
        self.assertMessageEqual(1, OUTPUT[1])

    def test_formatting(self):
        """ Test if correct Events have been produced. """
        self.input_message = None
        self.allowed_warning_count = 1  # message has empty raw
        self.sysconfig = {'http_url': 'http://localhost/{time[%Y]}.txt',
                          'extract_files': None,
                          'name': 'Example feed',
                          'http_url_formatting': True,
                          }
        self.run_bot(iterations=1)

    def test_gzip(self):
        self.sysconfig = {'http_url': 'http://localhost/foobar.gz',
                          'extract_files': True,
                          'name': 'Example feed',
                          }
        self.run_bot(iterations=1)

        output = OUTPUT[0].copy()
        output['feed.url'] = self.sysconfig['http_url']
        del output['extra.file_name']
        self.assertMessageEqual(0, output)

    def test_zip_auto(self):
        """
        Test automatic unzipping
        """
        self.sysconfig = {'http_url': 'http://localhost/two_files.zip',
                          'name': 'Example feed',
                          }
        self.run_bot(iterations=1)

        output0 = OUTPUT[0].copy()
        output0['feed.url'] = self.sysconfig['http_url']
        output1 = OUTPUT[1].copy()
        output1['feed.url'] = self.sysconfig['http_url']
        self.assertMessageEqual(0, output0)
        self.assertMessageEqual(1, output1)

    def test_zip(self):
        """
        Test unzipping with explicit extract_files
        """
        self.sysconfig = {'http_url': 'http://localhost/two_files.zip',
                          'extract_files': ['bar', 'foo'],
                          'name': 'Example feed',
                          }
        self.run_bot(iterations=1)

        output0 = OUTPUT[0].copy()
        output0['feed.url'] = self.sysconfig['http_url']
        output1 = OUTPUT[1].copy()
        output1['feed.url'] = self.sysconfig['http_url']
        self.assertMessageEqual(0, output0)
        self.assertMessageEqual(1, output1)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
