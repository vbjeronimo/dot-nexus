import logging
import tomllib

from nexus import components
from nexus import config


def list_profiles() -> None:
    profiles = [profile.stem for profile in config.PROFILES_DIR.iterdir()]

    print("\nAvailable profiles:")
    for profile_name in profiles:
        print(f"  - {profile_name}")


def load_profile(profile_name: str) -> None:
    profile_contents = load_profile_config(profile_name)
    nexus_config = config.load_nexus_config()

    components_to_update = nexus_config.get("components", [])
    if components_to_update == []:
        raise KeyError (f"Could not find list of components to update. Please add "
                        "a 'components' list under the '[nexus]' header to your config.")

    logging.debug(f"Profile '{profile_name}' updates the following components: {components_to_update}")

    for component in components_to_update:
        logging.debug(f"Updating component '{component}'...")

        component_contents = components.load_component_contents(component)

        try:
            updated_component_contents = components.update_component(component_contents, profile_contents)
        except KeyError as err:
            raise KeyError(f"Could not update component '{component}' with the contents "
                           f"of the profile '{profile_name}': {err}")

        components.write_updated_component(component, updated_component_contents)


def load_profile_config(profile_name: str) -> dict:
    profile_to_load = None
    for profile in config.PROFILES_DIR.iterdir():
        if profile.stem == profile_name:
            profile_to_load = profile
            break

    if profile_to_load is None:
        raise FileNotFoundError(f"Could not find profile '{profile_name}' in {config.PROFILES_DIR}.")

    with open(profile_to_load, "rb") as profile_toml:
        profile_contents = tomllib.load(profile_toml)

    return profile_contents
