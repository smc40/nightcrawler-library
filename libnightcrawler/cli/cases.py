import libnightcrawler.cli.utils as cu


def parser_name():
    return "cases"

def add_parser(subparsers, parents):
    parser = subparsers.add_parser(parser_name(), help="Postgresql helpers", parents=parents)
    subparser = parser.add_subparsers(help="Modules", dest="case", required=True)

    subparser.add_parser("list", help="List all cases", parents=parents)
    
    get = subparser.add_parser("get", help="List all cases", parents=parents)
    get.add_argument("identifier", help="Case identifier")

    return parser

def apply(args):
    from libnightcrawler.context import Context
    context = Context()
    if args.case == "list":
        cu.print_json(context.db_client.list_cases())
