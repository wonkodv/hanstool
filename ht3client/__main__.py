from . import main, ARG_PARSER
import sys

o = ARG_PARSER.parse_args()
sys.exit(main(o))
