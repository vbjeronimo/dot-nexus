import argparse
import logging
import sys

from nexus import profiles


def get_parser() -> argparse.ArgumentParser:
    description = "A centralized .dotfiles management system"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-p", "--load", help="load a nexus profile (specified by profile name)")
    parser.add_argument("-l", "--list", action="store_true", help="list all profiles available")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")

    return parser


def parse_args(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    logging.debug(f"Command-line args: {args}")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.debug:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    if args.list:
        profiles.list_profiles()
        sys.exit(0)

    if args.load:
        profiles.load_profile(args.load)
        sys.exit(0)
