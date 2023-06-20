import logging
import re
from typing import Any

from nexus import config


def load_component_contents(component_name: str) -> list[str]:
    component_to_load = config.COMPONENTS_DIR.joinpath(component_name)
    if not component_to_load.exists():
        raise FileNotFoundError(f"Could not find component '{component_name}' in {config.COMPONENTS_DIR}.")

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
                raise KeyError(f"Key '{re_match.group(1)}' not in profile config.")

        updated_line = re.sub("<<.*>>", str(nested_value), line)
        updated_component.append(updated_line)

    return "\n".join(updated_component)


def write_updated_component(component_name: str, updated_component_contents: str) -> None:
    ext = config.FILE_EXTENSIONS[component_name]
    updated_file_name = f"nexus.{ext}"
    updated_file_path = config.CONFIG_DIR.joinpath(component_name, updated_file_name)
    logging.debug(f"Saving updated component to {updated_file_path}...")

    updated_file_path.parent.mkdir(parents=True, exist_ok=True)
    updated_file_path.write_text(updated_component_contents)
    logging.info(f"Successfully updated component '{component_name}' at {updated_file_path}")
