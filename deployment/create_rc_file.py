# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Standard Library
import os
import sys
from typing import Any

# Third Party Libraries
import yaml

# Define file paths
YAML_FILE = "deployment/rc_variables.yaml"
CMSRC_FILE = ".cmsrc"

# ANSI color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No color


def load_yaml() -> Any:
    """Load YAML config file and return dictionary."""
    if not os.path.exists(YAML_FILE):
        print(f"{RED}Error: {YAML_FILE} not found!{NC}")
        sys.exit(1)

    with open(YAML_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_existing_env() -> dict[str, str]:
    """Load existing .cmsrc values if available."""
    env = {}

    if os.path.exists(CMSRC_FILE):
        with open(CMSRC_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("export"):
                    key, value = line.replace("export ", "").strip().split("=", 1)
                    env[key] = value.strip('"')

    return env


def prompt_for_values(
    variables: list[Any], existing_env: dict[str, str]
) -> dict[str, str]:
    """Prompt the user for missing environment variables with required validation."""
    updated_env = existing_env.copy()

    for var in variables:
        name = var["name"]
        required = var["required"]
        default = var["default"]
        description = var["description"]

        # If the variable already exists, keep it
        if name in existing_env:
            existing_value = existing_env[name]
            if not required or (existing_value and existing_value.strip()):
                print(
                    f"{NC}Found existing value for {YELLOW}{name}{NC}: {GREEN}{existing_env[name]}{NC}\n"
                )
                continue

        # Prompt user for input (loop if required variable is empty)
        print(f"Key: {YELLOW}{name}{NC}")
        if default:
            print(f"Default: {YELLOW}{default}{NC}")
        print(f"Required: {required}")
        print(f"Description: {description}")
        while True:
            if not required:
                user_input = (
                    input(f"{CYAN}Enter value [press Enter to skip]: {NC}") or default
                )
            elif default:
                user_input = (
                    input(f"{CYAN}Enter value [press Enter to use default]: {NC}")
                    or default
                )
            else:
                user_input = input(f"{CYAN}Enter value: {NC}") or default
            if required and (not user_input or not user_input.strip()):
                print(f"{RED}Error: {name} is required! Please enter a value.{NC}")
            else:
                print()
                break

        updated_env[name] = user_input if user_input else ""

    return updated_env


def save_env_file(env: dict[str, str]) -> None:
    """Write the updated environment variables to .cmsrc."""
    with open(CMSRC_FILE, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        for key, value in env.items():
            f.write(f'export {key}="{value}"\n')

    print(f"{GREEN}Finished updating {CMSRC_FILE}.{NC}")
    print(
        f"{YELLOW}Run {CYAN}`source {CMSRC_FILE}`{YELLOW} before performing a deployment.{NC}"
    )


def suggest_manual_creation(variables: list[Any]) -> None:
    """Suggest manual creation of .cmsrc if it does not exist."""
    print(
        f"{YELLOW}No .cmsrc file found. You can manually create and edit your .cmsrc file instead of running this script.\n{NC}"
    )
    print("cat > .cmsrc <<EOL")
    print("#!/bin/bash")
    for var in variables:
        print(f'export {var["name"]}="{var["default"]}"')
    print("EOL\n")
    print(f"{YELLOW}Then edit the file as needed and run:{CYAN} source .cmsrc")
    print(
        f"\n{YELLOW}Press {CYAN}Enter{YELLOW} to continue with interactive setup, or {CYAN}CTRL+C{YELLOW} to exit and create the file manually.{NC}"
    )
    input()


def main() -> None:
    """Main function to handle environment variable creation."""
    yaml_data = load_yaml()

    if len(sys.argv) > 1:
        config_key = sys.argv[1].strip()  # Remove any accidental whitespace
    else:
        config_key = None

    # Validate key
    if not config_key or config_key not in yaml_data:
        print(f"{RED}Error: Configuration key '{config_key}' not found!{NC}")
        print(
            f"{YELLOW}Available configuration keys: {CYAN}{list(yaml_data.keys())}{NC}"
        )
        sys.exit(1)

    # Proceed with environment variable setup
    existing_env = load_existing_env()

    # If .cmsrc does not exist, suggest manual creation
    if not os.path.exists(CMSRC_FILE):
        suggest_manual_creation(yaml_data[config_key])
    else:
        print(f"{YELLOW}.cmsrc file found. Checking for all values.\n{NC}")

    updated_env = prompt_for_values(yaml_data[config_key], existing_env)

    save_env_file(updated_env)


if __name__ == "__main__":
    main()
