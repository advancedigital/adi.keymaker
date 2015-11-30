import os
import unittest

from mock import patch

from adi.keymaker.keymaker import KeyMaker


class KeyMaker_tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.role = os.environ.get('KEYMAKER_TEST_ROLE', None)
        cls.key_maker = KeyMaker(cls.role, 'test-session')

    def setUp(self):
        if self.role is None:
            self.skipTest(
                "Specify a role using the KEYMAKER_TEST_ROLE "
                "environment variable"
            )

    def test_assume_smiles_with_glee_when_called(self):
        self.key_maker.assume()

    def test_assume_hates_you_today(self):
        with patch.object(self.key_maker, 'role', return_value='stingy') as _:
            with self.assertRaises(Exception):
                self.key_maker.assume()
