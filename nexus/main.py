import logging
import sys

from nexus import cli
from nexus import config


def main():
    logging.basicConfig(
        format="[%(levelname)s] %(funcName)s: %(message)s",
        level=logging.INFO,
        stream=sys.stdout
    )

    config.COMPONENTS_DIR.mkdir(parents=True, exist_ok=True)
    config.PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    parser = cli.get_parser()

    try:
        cli.parse_args(parser)
    except Exception as err:
        logging.error(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
