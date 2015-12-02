#TODO

Things that need to be done sometime:


## Soon


License:
*   GPL all the files

Code Cleanup
*   Make all of it PEP8

*   Collect all scripts, load at once

## Sometime

### Setup

    `dirname $0`/../scripts
    look for scripts in ~/.config/ht3/


### Documentation
What functions to overwrite:
*   `cli_prompt`
*   `command_not_found_hook`
*   `handle_exception`

More Examples
Generate Examples.md from scripts/


### Features

*   ArgParsing:
*   getopt
*   getlongopt
*   The weird spec for which a stub exists

### Stabillity

Unittests:
*   Argparsers
*   Documentation of Commands
*   all params of `register_command`
*   `execute_command`


Integration Tests:
*   showing and logging of return values

Automated Tests with Travis:
*   .travis.yml

    python:  3.5
    install: python setup.py install
    script:  python -m ht3 -s test_scripts -x "test" -s "unittest"
