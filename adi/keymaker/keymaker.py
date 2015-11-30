"""

keymaker uses the boto Python library to assume an AWS role. Before
you can use this utility, you'll need to make sure you have AWS keys set
up in your environment, either as environment variables or in your
~/.aws/config file. These keys should be permitted to assume the roles
you are requesting to assume with keymaker

"""
import argparse
import datetime
import os
from subprocess import check_call, check_output, CalledProcessError
import sys

import boto.exception
from boto.sts import STSConnection


def parse_args(argv=None):  # pragma: no cover
    """Parses input parameters and return args list
    """
    user = os.environ['USER']
    parser = argparse.ArgumentParser("assume an aws role")
    parser.add_argument("role", help="Role name you want to assume")
    parser.add_argument(
        "-a",
        "--account-id",
        help="Specify the AWS Account ID to use"
    )
    parser.add_argument(
        "-n",
        "--session-name",
        default=user,
        help="Supply a different session name "
        "(default={})".format(user)
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Show output from command"
    )
    parser.add_argument(
        "-e",
        "--export",
        action="store_true",
        default=False,
        help="Produce export statements"
    )
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        default=False,
        help="Save the new keys to your ~/.aws/credentials "
        "file"
    )
    return parser.parse_args(argv)


class KeyMaker(object):
    """KeyMaker class
    Attributes:
        role (str): Desire role to assume
        session_name (Optional[str]): Session name
        account_id (str): AWS account id
        save (boolean): Save the credential
        verbose (boolean): Show verbose information
        export (boolean): export credentials
    """
    map_ = {
        'access_key': 'AWS_ACCESS_KEY_ID',
        'secret_key': 'AWS_SECRET_ACCESS_KEY',
        'session_token': 'AWS_SESSION_TOKEN',
        'security_token': 'AWS_SECURITY_TOKEN',
        'expiration': 'AWS_EXPIRATION'
    }

    def __init__(
            self,
            role,
            session_name,
            account_id=None,
            save=False,
            verbose=False,
            export=False
    ):
        self.role = role
        self.account_id = account_id
        if account_id is None:
            self.account_id = self.get_account_id()
        self.session_name = session_name
        self.save = save
        self.verbose = verbose
        self.export = export
        self.credentials = None

    @staticmethod
    def get_account_id():
        """Get AWS Account id from environment variable or config file
        """
        try:
            return os.environ['AWS_ACCOUNT_ID']
        except KeyError:
            pass
        args = ['aws', 'configure', 'get', 'account_id']
        try:
            output = check_output(args)
        except CalledProcessError:
            sys.stderr.write(
                'ERROR: Unable to determine AWS Account ID.\n\n'
                'You can specify the Account ID in one of several '
                'ways:\n'
                ' - The AWS_ACCOUNT_ID environment variable\n'
                ' - Your awscli config (~/.aws/config)\n'
                ' - Specify the [-a, --account-id] option\n\n'
                'Use `aws configure set account_id <id>` to set '
                'it from the command line.\n'
            )
            sys.exit(1)
        else:
            return output.strip()

    def get_role_arn(self):
        """Returns the arn for the role you want to assume.
        """
        return 'arn:aws:iam::{}:role/{}'.format(self.account_id, self.role)

    def set_env(self, key, value):
        """Prints the value and sets the environment variable for a credential
        component.
        """
        os.environ[key] = value
        if self.verbose or self.export:
            export = 'export ' if self.export else ''
            print '{}{}={}'.format(export, key, value)

    def _clear_expired(self):
        """If assumed keys are expired, we probably don't want to use those in
        a subsequent keymaker call.  Clear them from the environment and move
        on.
        """
        exp = os.environ.get('AWS_EXPIRATION', None)
        if exp is not None:
            parsed = datetime.datetime.strptime(exp, '%Y-%m-%dT%H:%M:%SZ')
            if parsed < datetime.datetime.utcnow():
                for _, key in self.map_.items():
                    try:
                        del os.environ[key]
                    except KeyError:  # pragma: no cover
                        pass  # key already deleted

    def assume(self):
        """Assume a role a collect the AWS keys for that role.  This will set
        the environment variables AND will print the results.  It returns the
        credentials object from the assume_role function.
        """
        self._clear_expired()
        try:
            sts = STSConnection()
        except boto.exception.NoAuthHandlerFound:
            sys.stderr.write(
                "Please ensure that your AWS keys can "
                "assume roles.\n"
            )
            sys.exit(1)
        output = sts.assume_role(self.get_role_arn(), self.session_name)
        for source, dest in self.map_.items():
            # SVC-4728 - Add security_token support
            if source is 'security_token':
                source = 'session_token'
            value = getattr(output.credentials, source)
            self.set_env(dest, value)
        self.credentials = output.credentials
        if self.save:
            self._save()
        return self.credentials

    def _save(self):
        """Save the credentials to your .aws directory.
        """
        if self.credentials == None:
            raise Exception("You need to generate keys with assume() first.")
        for source, dest in self.map_.items():
            if source is 'security_token':
                continue
            value = getattr(self.credentials, source)
            check_call([
                'aws',
                'configure',
                'set',
                dest.lower(),
                value,
                '--profile',
                self.session_name
            ])


def main():  # pragma: no cover
    """keymaker main function
    """
    args = parse_args()
    keymaker = KeyMaker(
        args.role, args.session_name, args.account_id, args.save, args.verbose,
        args.export
    )
    keymaker.assume()


if __name__ == '__main__':  # pragma: no cover
    main()
