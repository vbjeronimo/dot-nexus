import argparse
import logging
import re
import sys
import tomllib
from pathlib import Path


EXTENSIONS = {
    "kitty": ".conf"
}

MISSING_ARGS = "no_args"

def get_parser() -> argparse.ArgumentParser:
    description = "A centralized .dotfiles management system."
    parser = argparse.ArgumentParser(prog="nexus", description=description)

    parser.add_argument("-l", "--list", action="store_true",
                        help="list the nexus profiles available to use")
    parser.add_argument("-p","--load", nargs="?", const=MISSING_ARGS,
                        help="load a nexus profile (specified by profile name)")

    return parser


def parse_args(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.list or args.load == MISSING_ARGS:
        list_profiles()
        sys.exit(0)

    if args.load:
        load_profile(args.load)
        sys.exit(0)


def list_profiles() -> None:
    nexus_dir = Path.home().joinpath(".config", "nexus")
    profiles_dir = nexus_dir.joinpath("profiles")

    profiles = [file.stem for file in profiles_dir.iterdir()]

    print("List of profiles available:")
    for profile in profiles:
        print(f"  - {profile}")


def load_profile(profile_name: str) -> None:
    config_dir = Path.home().joinpath(".config")
    nexus_dir = config_dir.joinpath("nexus")
    components_dir = nexus_dir.joinpath("components")
    profiles_dir = nexus_dir.joinpath("profiles")

    profiles = [file.stem for file in profiles_dir.iterdir()]

    if profile_name in profiles:
        with open(profiles_dir.joinpath(f"{profile_name}.toml"), "rb") as toml_file:
            profile = tomllib.load(toml_file)

        components_to_update = profile["nexus"]["components"]

        for component in components_to_update:
            component_content = components_dir.joinpath(component).read_text()

            updated_component: list[str] = []
            for line in component_content.split("\n"):
                match = re.search("<<(.*)>>", line)
                if match is None:
                    updated_component.append(line)
                    continue

                keys = match.group(1).split(".")

                nested_value = profile
                for key in keys:
                    if key in nested_value:
                        nested_value = nested_value[key]
                    else:
                        nested_value = None

                updated_line = re.sub("<<.*>>", str(nested_value), line)
                updated_component.append(updated_line)

            output = "\n".join(updated_component)

            output_file = profile["nexus"]["generated_file_name"]
            ext = EXTENSIONS[component]
            generated_file = config_dir.joinpath(component, f"{output_file}{ext}")
            generated_file.write_text(output)

            print(f"Generated file at '{generated_file.absolute()}' for component '{component}'.")


def setup_logger() -> None:
    logging.basicConfig(
        format="[%(levelname)s] %(funcName)s: %(message)s",
        level=logging.DEBUG,
        stream=sys.stdout
    )


def main():
    setup_logger()

    parser = get_parser()
    parse_args(parser)


if __name__ == "__main__":
    main()
