import sys

from . import ARG_PARSER, main

o = ARG_PARSER.parse_args()
sys.exit(main(o))
