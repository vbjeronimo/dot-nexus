import argparse
import logging
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


FILE_EXTENSIONS = {
    "kitty": "conf",
    "qtile": "py",
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
    profile_contents = load_profile_config(profile_name)
    nexus_config = load_nexus_config()

    components_to_update = nexus_config.get("components", [])
    if components_to_update == []:
        raise KeyError (f"Could not find list of components to update. Please add "
                        "a 'components' list under the '[nexus]' header to your config.")

    logging.debug(f"Profile '{profile_name}' updates the following components: {components_to_update}")

    for component in components_to_update:
        logging.debug(f"Updating component '{component}'...")

        component_contents = load_component_contents(component)
        updated_component_contents = update_component(component_contents, profile_contents)

        write_updated_component(component, updated_component_contents)


def load_profile_config(profile_name: str) -> dict:
    profile_to_load = None
    for profile in PROFILES_DIR.iterdir():
        if profile.stem == profile_name:
            profile_to_load = profile
            break

    if profile_to_load is None:
        raise FileNotFoundError(f"Could not find profile '{profile_name}' in {PROFILES_DIR}.")

    with open(profile_to_load, "rb") as profile_toml:
        profile_contents = tomllib.load(profile_toml)

    return profile_contents


def load_nexus_config() -> dict:
    nexus_config_file = NEXUS_DIR.joinpath("nexus.toml")
    if not nexus_config_file.exists():
        raise FileNotFoundError(f"{nexus_config_file.absolute()} not found. "
                                "Could not load the base config for Nexus. Exiting...")

    with open(nexus_config_file, "rb") as nexus_toml:
        nexus_config = tomllib.load(nexus_toml).get("nexus", {})

    return nexus_config


def load_component_contents(component_name: str) -> list[str]:
    component_to_load = COMPONENTS_DIR.joinpath(component_name)
    if not component_to_load.exists():
        raise FileNotFoundError(f"Could not find component '{component_name}' in {COMPONENTS_DIR}.")

    component_contents = component_to_load.read_text()

    return component_contents.split("\n")


def update_component(component_contents: list[str], profile_contents: dict) -> str:
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
                # TODO: write a more informative error message
                #logging.error(f"Key '{keys}' in component '{component}' not in {profile_to_load.name}. Double check your config ({profile_to_load}).")
                raise KeyError

        updated_line = re.sub("<<.*>>", str(nested_value), line)
        updated_component.append(updated_line)

    return "\n".join(updated_component)


def write_updated_component(component_name: str, updated_component_contents: str) -> None:
    ext = FILE_EXTENSIONS[component_name]
    updated_file_name = f"nexus.{ext}"
    updated_file_path = CONFIG_DIR.joinpath(component_name, updated_file_name)
    logging.debug(f"Saving updated component to {updated_file_path}...")

    updated_file_path.parent.mkdir(parents=True, exist_ok=True)
    updated_file_path.write_text(updated_component_contents)
    logging.info(f"Successfully updated component '{component_name}' at {updated_file_path}")


def main():
    logging.basicConfig(
        format="[%(levelname)s] %(funcName)s: %(message)s",
        level=logging.INFO,
        stream=sys.stdout
    )

    COMPONENTS_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    parser = get_parser()

    try:
        parse_args(parser)
    except Exception as err:
        logging.error(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
