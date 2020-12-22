from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class ComandTest(TestCase):
    def test_wait_for_db_ready(self):
        """TEST WAITING FOR DB WHEN ITS READY"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """TEST WAITING FOR DB"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
