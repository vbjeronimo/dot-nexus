import tomllib
from pathlib import Path

CONFIG_DIR = Path.home().joinpath(".config")
NEXUS_DIR = CONFIG_DIR.joinpath("nexus")
COMPONENTS_DIR = NEXUS_DIR.joinpath("components")
PROFILES_DIR = NEXUS_DIR.joinpath("profiles")

FILE_EXTENSIONS = {
    "kitty": "conf",
    "qtile": "py",
}


def load_nexus_config() -> dict:
    nexus_config_file = NEXUS_DIR.joinpath("nexus.toml")
    if not nexus_config_file.exists():
        raise FileNotFoundError(f"{nexus_config_file.absolute()} not found. "
                                "Could not load the base config for Nexus. Exiting...")

    with open(nexus_config_file, "rb") as nexus_toml:
        nexus_config = tomllib.load(nexus_toml).get("nexus", {})

    return nexus_config
