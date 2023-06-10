import argparse
import sys
from pathlib import Path


def get_parser() -> argparse.ArgumentParser:
    description = "A centralized .dotfiles management system."
    parser = argparse.ArgumentParser(prog="dotnexus", description=description)

    return parser


def parse_args(parser: argparse.ArgumentParser) -> None:
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)


def main():
    dotnexus_dir = Path.home().joinpath(".config", "dotnexus")
    dotnexus_dir.mkdir(parents=True, exist_ok=True)
    dotnexus_dir.joinpath("components").mkdir(parents=True, exist_ok=True)
    dotnexus_dir.joinpath("profiles").mkdir(parents=True, exist_ok=True)

    parser = get_parser()
    parse_args(parser)


if __name__ == "__main__":
    main()
