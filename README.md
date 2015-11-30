adi.keymaker
============

### Installation

#### pip

Make sure you’ve [configured pip] to use pypi.advance.net, and then just do:

    pip install adi.keymaker
    
> **Tip!** Installing from source keeps you more up to date!

#### source

    git clone https://<user>@stash.advance.net/scm/svc/adi.keymaker.git
    cd adi.keymaker
    pip install -e .

> **Tip!** This will be robust against upgrades that don’t require a new dependency, at which point you should do `pip install -e .` again.

### Scripts
#### keymaker

`keymaker` uses the `boto` Python library to assume an AWS role. Before
you can use this utility, you’ll need to make sure you have AWS keys set
up in your environment, either as environment variables or in your
`~/.aws/config` file. These keys should be permitted to assume the roles
you are requesting to assume with `keymaker`.

##### Usage

Here’s the help for the command:

    $ keymaker -h
    usage: assume an aws role [-h] [-a ACCOUNT_ID] [-n SESSION_NAME] [-v] [-e]
                              [-s]
                              role

    positional arguments:
      role                  Role name you want to assume

    optional arguments:
      -h, --help            show this help message and exit
      -a ACCOUNT_ID, --account-id ACCOUNT_ID
                            Specify the AWS Account ID to use
      -n SESSION_NAME, --session-name SESSION_NAME
                            Supply a different session name (default=$USER)
      -v, --verbose         Show output from command
      -e, --export          Produce export statements
      -s, --save            Save the new keys to your ~/.aws/credentials file

##### Python

You can also use Python to get keys to use for boto:

    >>> from adi.keymaker.keymaker import KeyMaker
    >>> km = KeyMaker('my_role', 'my_session', 'my_account_id')
    >>> creds = km.assume()
    >>> print creds.access_key, creds.secret_key

##### Bash

You can also import the credentials to use in a bash script:

    #!/bin/bash
    eval $(keymaker -e <role-name>)

The `-e` option will force the command to output export statements, which you then need to eval for inclusion in your current shell.

#### keymaker-completion.bash

A bash completion script is included that will list the roles you have acccess to.  Your personal AWS keys must be able to list roles.

    $ keymaker<tab>
    keymaker                  keymaker-completion.bash
    $ source $(which keymaker-completion.bash)
    $ keymaker<tab>
    keymaker                  keymaker-completion.bash  keymaker-reset            keymaker-show
    
To use the tab-completion with roles you'll have to include a space before you press tab, like this:

    $ keymaker<space><tab>
    # list of roles should appear
    
The completion script also creates some handy aliases for you. Read on...

#### keymaker-show
If you quickly want to see the keys that `keymaker` has made for you, you can use the `keymaker-show` command.

    $ eval $(keymaker -e my-role)

    $ keymaker-show
    AWS_SESSION_TOKEN=AQoDYXdzEF8agAIgffxeSmvB82FeLtdk74Xem0p8lJY2kSJED6wJd4U4LTwLvr5hWPoMNcPFXbnixPv0Piqq3s3rBxGiRl1ZoJDh0lGEAdpy1iSTx+5apNqWtl7hT31SkLtI3OmdrfM5wN5tSzUar30ukIzRbh4vCTYVhZHieTOVOFq0FZh36PExMqVU/haWnbCotDe2Bpn9+c31ZzVN7B5EpSfDYIiLujjDmEGJJkOFFVkeJSxn7Um6d28eI/bAYh42g7Gh+jBbPWHqLaQkQuf5XGgHS3HVwEAonrpsDJH7ULEfpbwhQPs/OBZKgldjPMbxT7xE5KTdjaC+it6TCNNhPCuMaIRAOvFYIMLt8rEF
    AWS_EXPIRATION=2015-11-06T15:18:42Z
    AWS_SECRET_ACCESS_KEY=oNmNmtazmYJDIhyj5dj7ONwyT6NWRq65JPmP5S5T
    AWS_ACCESS_KEY_ID=ASIAJCTJO272AMR3UBXA
    AWS_SECURITY_TOKEN=AQoDYXdzEF8agAIgffxeSmvB82FeLtdk74Xem0p8lJY2kSJED6wJd4U4LTwLvr5hWPoMNcPFXbnixPv0Piqq3s3rBxGiRl1ZoJDh0lGEAdpy1iSTx+5apNqWtl7hT31SkLtI3OmdrfM5wN5tSzUar30ukIzRbh4vCTYVhZHieTOVOFq0FZh36PExMqVU/haWnbCotDe2Bpn9+c31ZzVN7B5EpSfDYIiLujjDmEGJJkOFFVkeJSxn7Um6d28eI/bAYh42g7Gh+jBbPWHqLaQkQuf5XGgHS3HVwEAonrpsDJH7ULEfpbwhQPs/OBZKgldjPMbxT7xE5KTdjaC+it6TCNNhPCuMaIRAOvFYIMLt8rEF

> **Tip!** This is installed when the `keymaker-completion.bash` script is sourced into your shell.

#### keymaker-reset
If you want to remove keys that are in your current shell, use the `keymaker-reset` command:

    $ keymaker-show
    AWS_SESSION_TOKEN=AQoDYXdzEF8agAIgffxeSmvB82FeLtdk74Xem0p8lJY2kSJED6wJd4U4LTwLvr5hWPoMNcPFXbnixPv0Piqq3s3rBxGiRl1ZoJDh0lGEAdpy1iSTx+5apNqWtl7hT31SkLtI3OmdrfM5wN5tSzUar30ukIzRbh4vCTYVhZHieTOVOFq0FZh36PExMqVU/haWnbCotDe2Bpn9+c31ZzVN7B5EpSfDYIiLujjDmEGJJkOFFVkeJSxn7Um6d28eI/bAYh42g7Gh+jBbPWHqLaQkQuf5XGgHS3HVwEAonrpsDJH7ULEfpbwhQPs/OBZKgldjPMbxT7xE5KTdjaC+it6TCNjuPCuMaIRAOvFYIMLt8rEF
    AWS_EXPIRATION=2015-11-06T15:18:42Z
    AWS_SECRET_ACCESS_KEY=oNmNmtazmYJDIhyj5dj7ONwy6aNWRq65JPmP5S5T
    AWS_ACCESS_KEY_ID=ASIAJCTJO272BVR3UBXA
    AWS_SECURITY_TOKEN=AQoDYXdzEF8agAIgffxeSmvB82FeLtdk74Xem0p8lJY2kSJED6wJd4U4LTwLvr5hWPoMNcPFXbnixPv0Piqq3s3rBxGiRl1ZoJDh0lGEAdpy1iSTx+5apNqWtl7hT31SkLtI3OmdrfM5wN5tSzUar30ukIzRbh4vCTYVhZHieTOVOFq0FZh36PExMqVU/haWnbCotDe2Bpn9+c31ZzVN7B5EpSfDYIiLujjDmEGJJkOFFVkeJSxn7Um6d28eI/bAYh42g7Gh+jBbPWHqLaQkQuf5XGgHS3HVwEAonrpsDJH7ULEfpbwhQPs/OBZKgldjPMbxT7xE5KTdjaC+it6TCNjuPCuMaIRAOvFYIMLt8rEF

    $ keymaker-reset
    $ keymaker-show
    # no output
    
> **Tip!** This is installed when the `keymaker-completion.bash` script is sourced into your shell.

### Account ID

You'll need to specify an Account ID to use `keymaker`.  You can do this in one of three ways:

1. Specify using the `AWS_ACCOUNT_ID` environment variable.
2. Specify in your `~/.aws/config` file:
    ```
    [default]
    region = us-east-1
    account_id = 0123456789
    ```
3. Use the [`-a`, `--account-id`] options of `keymaker`.

### Testing

Run unit-tests with:

    $ nosetests tests

A simple integration test is included, but is skipped/disabled unless you set the role you want to assume in an environment variable, `KEYMAKER_TEST_ROLE`.  You can run integration tests with:

    $ export KEYMAKER_TEST_ROLE=my-role
    $ nosetests tests/integration/

[configured pip]: https://wiki.advance.net/display/tech/Get+Started+with+Python+Packaging
