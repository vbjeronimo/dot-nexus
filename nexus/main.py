import argparse
import logging
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


FILE_EXTENSIONS = {
    "kitty": ".conf",
    "qtile": ".py",
}

CONFIG_DIR = Path.home().joinpath(".config")
NEXUS_DIR = CONFIG_DIR.joinpath("nexus")
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

    nexus_config = profile_contents.get("nexus", None)
    if nexus_config is None:
        if not NEXUS_DIR.joinpath("nexus.toml").exists():
            logging.error(f"Could not load the base config for Nexus. Exiting...")
            sys.exit(1)

        with open(NEXUS_DIR.joinpath("nexus.toml"), "rb") as nexus_file:
            nexus_config = tomllib.load(nexus_file).get("nexus", {})

    components_to_update = nexus_config.get("components", None)

    if components_to_update is None:
        # TODO: update this message. We're not defining 'components to load' only in profiles anymore
        logging.error(f"Could not find list of components to update in {profile_to_load}. "
                      f"Please add a 'components' list under the '[nexus]' header to your config.")
        sys.exit(1)

    logging.debug(f"Profile '{profile_to_load.stem}' updates the following components: {components_to_update}")

    for component in components_to_update:
        component_to_load = COMPONENTS_DIR.joinpath(component)
        if not component_to_load.exists():
            logging.error(f"Could not find component '{component_to_load.stem}' in {COMPONENTS_DIR}.")
            sys.exit(1)

        component_contents = component_to_load.read_text().split("\n")

        logging.debug(f"Updating component '{component}'...")

        updated_component = []
        for line in component_contents:
            re_match = re.search("<<(.*)>>", line)

            if re_match is None:
                updated_component.append(line)
                continue

            keys = re_match.group(1).split(".")

            nested_value: Any = profile_contents
            for key in keys:
                if key in nested_value:
                    nested_value = nested_value[key]
                else:
                    logging.error(f"Key '{keys}' in component '{component}' not in {profile_to_load.name}. Double check your config ({profile_to_load}).")
                    sys.exit(1)

            updated_line = re.sub("<<.*>>", str(nested_value), line)
            updated_component.append(updated_line)

        updated_file_stem = nexus_config.get("generate_file_name", "nexus")
        updated_file_name = f"{updated_file_stem}{FILE_EXTENSIONS[component]}"
        updated_file_path = CONFIG_DIR.joinpath(component, updated_file_name)
        logging.debug(f"Saving updated component to {updated_file_path}...")

        updated_file_content = "\n".join(updated_component)
        updated_file_path.parent.mkdir(parents=True, exist_ok=True)
        updated_file_path.write_text(updated_file_content)
        logging.info(f"Successfully updated component '{component}' at {updated_file_path}")


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
