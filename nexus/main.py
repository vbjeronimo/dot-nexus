import argparse
import logging
import re
import sys
import tomllib
from pathlib import Path


FILE_EXTENSIONS = {
    "kitty": ".conf",
    "qtile": ".py",
}

NEXUS_DIR = Path.home().joinpath(".config", "nexus")
COMPONENTS_DIR = NEXUS_DIR.joinpath("components")
PROFILES_DIR = NEXUS_DIR.joinpath("profiles")

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
        list_profiles()
        sys.exit(0)

    if args.load:
        load_profile(args.load)
        sys.exit(0)


def list_profiles() -> None:
    profiles = [profile.stem for profile in PROFILES_DIR.iterdir()]

    print("\nAvailable profiles:")
    for profile_name in profiles:
        print(f"  - {profile_name}")


def load_profile(profile_name: str) -> None:
    profile_to_load = None
    for profile in PROFILES_DIR.iterdir():
        if profile.stem == profile_name:
            profile_to_load = profile
            break

    if profile_to_load is None:
        logging.error(f"Could not find profile '{profile_name}' in {PROFILES_DIR}.")
        list_profiles()
        return

    with open(profile_to_load, "rb") as toml_file:
        profile_contents = tomllib.load(toml_file)

    components_to_update = profile_contents["nexus"]["components"]
    logging.debug(f"Profile '{profile_to_load.stem}' updates the following components: {components_to_update}")

    for component in components_to_update:
        component_to_load = COMPONENTS_DIR.joinpath(component)
        if not component_to_load.exists():
            logging.error(f"Could not find component '{component_to_load.stem}' in {COMPONENTS_DIR}.")
            sys.exit(1)

        component_contents = component_to_load.read_text()

        logging.debug(f"Updating component '{component}'...")

        updated_component = []
        for line in component_contents:
            re_match = re.search("<<(.*)>>", line)

            if re_match is None:
                updated_component.append(line)
                continue

            keys = re_match.group(1)
            print(f"keys: {keys}")

        # TODO: continue here...


def main():
    logging.basicConfig(
        format="[%(levelname)s] %(funcName)s: %(message)s",
        level=logging.INFO,
        stream=sys.stdout
    )

    COMPONENTS_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    parser = get_parser()
    parse_args(parser)


if __name__ == "__main__":
    main()
