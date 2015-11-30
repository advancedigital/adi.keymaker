"""
  Unittest cases of keymaker.

  Use below command to perform the test:

        $ nosetests -c nose.cfg tests/integration tests

"""
import os
from StringIO import StringIO
import subprocess
import unittest

import boto
from mock import patch, Mock, MagicMock, sentinel, DEFAULT

from adi.keymaker import KeyMaker


class KeyMaker_tests(unittest.TestCase):
    """unit test class for keymaker
    """
    @classmethod
    def setUpClass(cls):
        cls.key_maker = KeyMaker('test-role', 'test-session', '1234567890')

    def test_get_arn_returns_proper_arn(self):
        """test of get_role_arn(), check if correct arn is return
        """
        expected_arn = 'arn:aws:iam::1234567890:role/test-role'
        self.assertEqual(self.key_maker.get_role_arn(), expected_arn)

    def get_output(self):
        output = Mock()
        output.credentials.access_key = 'access_key'
        output.credentials.secret_key = 'secret_key'
        output.credentials.session_token = 'session_token'
        output.credentials.expiration = '2015-10-28T16:30:51Z'
        return output

    def test_assume_calls__clear_expired(self):
        """test to check if _clear_expired() being called when credential expired
        """
        sts = MagicMock()
        output = self.get_output()
        with patch('adi.keymaker.keymaker.STSConnection') as STSConn:
            with patch.object(self.key_maker, '_clear_expired') as _clear_exp:
                STSConn.return_value = sts
                sts.assume_role.return_value = output
                self.key_maker.assume()
                self.assertTrue(_clear_exp.called)

    def test__clear_expired_clears_keys_when_expired(self):
        """test to check if env variable AWS_EXPIRATION is cleared
        """
        os.environ['AWS_EXPIRATION'] = '2001-01-01T00:00:00Z'
        self.key_maker._clear_expired()
        self.assertFalse(os.environ.has_key('AWS_EXPIRATION'))

    def test__clear_expired_does_not_clear(self):
        """test to ensure env variable AWS_EXPIRATION
        is not cleared when credential is not yet expired
        """
        os.environ['AWS_EXPIRATION'] = '2201-01-01T00:00:00Z'
        self.key_maker._clear_expired()
        self.assertTrue(os.environ.has_key('AWS_EXPIRATION'))

    def test_assume_calls_assume_role(self):
        """test to ensure key_maker.assume() is called once
        """
        sts = MagicMock()
        output = self.get_output()
        with patch('adi.keymaker.keymaker.STSConnection') as STSConn:
            STSConn.return_value = sts
            sts.assume_role.return_value = output
            self.key_maker.assume()
            sts.assume_role.assert_called_once_with(
                'arn:aws:iam::1234567890:role/test-role', 'test-session'
            )

    def test_assume_calls_set_env_five_times(self):
        """test to check if set_env called five times
        """
        sts = MagicMock()
        output = self.get_output()
        with patch('adi.keymaker.keymaker.STSConnection') as STSConn:
            with patch.object(self.key_maker, 'set_env') as mock_set_env:
                STSConn.return_value = sts
                sts.assume_role.return_value = output
                self.key_maker.assume()
                self.assertEqual(mock_set_env.call_count, 5)

    def test_assume_returns_credentials(self):
        """test credentials return properly
        """
        sts = MagicMock()
        output = self.get_output()
        with patch('adi.keymaker.keymaker.STSConnection') as STSConn:
            STSConn.return_value = sts
            sts.assume_role.return_value = output
            ret = self.key_maker.assume()
            self.assertEqual(ret, output.credentials)

    def test_set_env_sets_environment_variables(self):
        """test case of key_maker.set_env()
        """
        self.key_maker.set_env(str(sentinel.key), str(sentinel.value))
        self.assertIn(str(sentinel.key), os.environ)
        self.assertEqual(os.environ[str(sentinel.key)], str(sentinel.value))

    def test_set_env_prints_export_statements_when_asked(self):
        """test if key_maker.set_env() exports expect output
        """
        with patch.object(self.key_maker, 'export', return_value=True) as _:
            with patch('sys.stdout', new=StringIO()) as out:
                self.key_maker.set_env(str(sentinel.key), str(sentinel.value))
                expected_out = 'export sentinel.key=sentinel.value\n'
                self.assertEqual(out.getvalue(), expected_out)

    def test_set_env_prints_when_asked(self):
        """test if set_env() has right verbose output
        """
        with patch.object(self.key_maker, 'verbose', return_value=True) as _:
            with patch('sys.stdout', new=StringIO()) as out:
                self.key_maker.set_env(str(sentinel.key), str(sentinel.value))
                expected_out = 'sentinel.key=sentinel.value\n'
                self.assertEqual(out.getvalue(), expected_out)

    def test_no_auth_exception_is_handled_politely(self):
        """test if keymaker raise exception correctly
        """
        with patch('adi.keymaker.keymaker.STSConnection') as STSConn:
            STSConn.side_effect = boto.exception.NoAuthHandlerFound
            with self.assertRaises(SystemExit) as e:
                self.key_maker.assume()
            self.assertEqual(e.exception.code, 1)

    def test__save_raises_exception_when_no_credentials(self):
        """test if exception raised correctly when no aws credentials available
        """
        with self.assertRaises(Exception) as e:
            self.key_maker._save()
        self.assertEqual(
            e.exception.message,
            "You need to generate keys with assume() first."
        )

    def test__save_calls_aws_configure_set(self):
        """test if check_call() get called correctly
        """
        with patch('adi.keymaker.keymaker.check_call') as check_call:
            with patch.object(self.key_maker, 'credentials'):
                self.key_maker._save()
                self.assertEqual(check_call.call_count, 4)

    def test_assume_calls__save_when_asked(self):
        """test if save option functions correctly
        """
        sts = MagicMock()
        output = self.get_output()
        save = Mock(return_value=True)
        with patch.multiple(self.key_maker, save=save, _save=DEFAULT) as mocks:
            with patch('adi.keymaker.keymaker.STSConnection') as STSConn:
                STSConn.return_value = sts
                sts.assume_role.return_value = output
                ret = self.key_maker.assume()
                self.assertTrue(mocks['_save'].called)

    def test_assume_prints_to_stderr_when_user_cannot_assume_role(self):
        """test if stderr message printed out correctly
        """
        msg = "Please ensure that your AWS keys can assume roles.\n"
        with patch('adi.keymaker.keymaker.STSConnection') as STSConn:
            STSConn.side_effect = boto.exception.NoAuthHandlerFound()
            with patch('sys.stderr') as _err:
                with self.assertRaises(SystemExit) as cm:
                    self.key_maker.assume()
                _err.write.assert_called_once_with(msg)
                self.assertEqual(cm.exception.code, 1)

    def test_get_account_id_reads_from_aws_config(self):
        """test to get AWS account id from local aws config
        """
        expected_acct_id = 'fake'
        keep = os.environ.get('AWS_ACCOUNT_ID', None)
        if os.environ.has_key('AWS_ACCOUNT_ID'):
            del os.environ['AWS_ACCOUNT_ID']
        with patch('adi.keymaker.keymaker.check_output') as check_output:
            check_output.return_value = 'fake\n'
            acct_id = self.key_maker.get_account_id()
            self.assertEqual(acct_id, expected_acct_id)
        if keep:
            os.environ['AWS_ACCOUNT_ID'] = keep

    def test_get_account_id_reads_from_env(self):
        """test to get AWS account id from env variable
        """
        expected_acct_id = 'fake'
        os.environ['AWS_ACCOUNT_ID'] = expected_acct_id
        acct_id = self.key_maker.get_account_id()
        self.assertEqual(acct_id, expected_acct_id)

    def test_get_account_id_produces_error_when_needed(self):
        """test if exception raised up while failed to get aws credential
        """
        keep = os.environ.get('AWS_ACCOUNT_ID', None)
        if os.environ.has_key('AWS_ACCOUNT_ID'):
            del os.environ['AWS_ACCOUNT_ID']
        with patch('adi.keymaker.keymaker.check_output') as check_output:
            args = (1, 'null', 'null')
            check_output.side_effect = subprocess.CalledProcessError(*args)
            with self.assertRaises(SystemExit) as e:
                self.key_maker.get_account_id()
            self.assertEqual(e.exception.code, 1)
        if keep:
            os.environ['AWS_ACCOUNT_ID'] = keep
