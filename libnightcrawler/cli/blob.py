import libnightcrawler.cli.utils as cu
import libnightcrawler.settings as ls


def parser_name():
    return "blob"


def add_parser(subparsers, parents):
    parser = subparsers.add_parser(parser_name(), help="Postgresql helpers", parents=parents)
    subparser = parser.add_subparsers(help="Modules", dest="case", required=True)

    settings = ls.BlobSettings()
    list_blob = subparser.add_parser("list", help="List all blobs in a container", parents=parents)
    list_blob.add_argument(
        "container",
        choices=[settings.image_container, settings.process_container, settings.public_container],
        help="Blob conatiner",
    )
    list_blob.add_argument("--full", action="store_true", help="Print all details")

    get = subparser.add_parser("get", help="List all cases", parents=parents)
    get.add_argument(
        "container",
        choices=[settings.image_container, settings.process_container, settings.public_container],
        help="Blob conatiner",
    )
    get.add_argument("path", help="Blob path")
    get.add_argument("--cache", type=int, default=0, help="Get cached data with this lifetime")
    return parser


def apply(args):
    from libnightcrawler.context import Context

    context = Context()
    if args.case == "list":
        service_client = context.blob_client.service_client
        container = service_client.get_container_client(args.container)
        cu.print_json([x.__dict__ if args.full else x.name for x in container.list_blobs()])

    elif args.case == "get":
        if args.cache:
            cu.print_json(context.blob_client.get_cached(args.path, args.cache))
            return
        service_client = context.blob_client.service_client
        client = service_client.get_blob_client(args.container, blob=args.path)
        cu.print_json(client.download_blob().readall())
