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

*   setup.py

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

Create Unit Tests tht test:
*   Argparsers
*   `load_script` sorting


TestScript:
*   Script which uses many functionallity of HT3,
    has a cmd test which invokes some of them plus unittests

