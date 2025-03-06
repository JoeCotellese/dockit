#!/usr/bin/env python3
import os
import sys
import subprocess
import configparser
import argparse


def expand_path(path):
    """Expands ~ and environment variables in a path."""
    return os.path.expanduser(os.path.expandvars(path))


def load_config():
    home = os.path.expanduser("~")
    config_file = os.path.join(home, ".dockit_config")

    if not os.path.exists(config_file):
        print(
            f"Config file not found at {config_file}. Please create it with the required settings."
        )
        exit(1)

    config = configparser.ConfigParser()
    config.read(config_file)

    try:
        base_directory = config["global"]["base_directory"]
    except KeyError:
        print(
            "Config file must contain a [global] section with a 'base_directory' entry."
        )
        exit(1)

    return expand_path(base_directory)


def run_container(container_name, base_directory):
    container_dir = os.path.join(base_directory, container_name)

    if not os.path.isdir(container_dir):
        print(f"Error: Container directory '{container_dir}' does not exist.")
        sys.exit(1)

    compose_file = os.path.join(container_dir, "docker-compose.yml")
    if not os.path.isfile(compose_file):
        print(f"Error: No docker-compose.yml file found in '{container_dir}'.")
        sys.exit(1)

    try:
        subprocess.run(["docker-compose", "up", "-d"], cwd=container_dir, check=True)
        print("Container started successfully.")
    except subprocess.CalledProcessError as err:
        print("Failed to start container using docker-compose:", err)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Run a Docker container from its docker-compose configuration."
    )
    parser.add_argument("container_name", help="Name of the container directory")
    args = parser.parse_args()

    base_directory = load_config()
    run_container(args.container_name, base_directory)


if __name__ == "__main__":
    main()
