import argparse
import json


def pagination_options():
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group('Search options')
    group.add_argument("--offset", default=0, type=int, help="Pagination offset (%(default)s)")
    group.add_argument("--limit", default=10, type=int, help="Pagination limit (%(default)s)")
    return parser


def print_json(res):
    print(json.dumps(res, indent=4, ensure_ascii=False, default=str))
