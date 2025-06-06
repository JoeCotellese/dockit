#!/usr/bin/env python3
import os
import sys
import configparser
import click
import webbrowser

from ezdocker.manager import ContainerManager


def expand_path(path):
    """Expands ~ and environment variables in a path."""
    return os.path.expanduser(os.path.expandvars(path))


def load_config():
    home = os.path.expanduser("~")
    config_file = os.path.join(home, ".ezdocker_config")

    if not os.path.exists(config_file):
        print(
            f"Config file not found at {config_file}. "
            "Please create it with the required settings."
        )
        exit(1)

    config = configparser.ConfigParser()
    config.read(config_file)

    try:
        base_directory = config["global"]["base_directory"]
    except KeyError:
        print(
            "Config file must contain a [global] section with a "
            "'base_directory' entry."
        )
        exit(1)

    return expand_path(base_directory)


@click.group()
@click.version_option("2025.6.1", prog_name="ezdocker")
def cli():
    """Manage Docker containers via docker-compose."""
    pass


@cli.command(help="Show the status of running containers.")
def status():
    base_directory = load_config()
    manager = ContainerManager(base_directory)
    stats = manager.status()
    if not stats:
        print("No running containers found.")
        return
    for proj, ports in stats.items():
        if ports:
            urls = ", ".join(f"http://localhost:{p}" for p in sorted(ports))
            print(f"{proj} – {urls}")
        else:
            print(f"{proj} – No ports exposed")


@cli.command(help="Start the specified container.")
@click.argument("container_name")
def start(container_name):
    base_directory = load_config()
    manager = ContainerManager(base_directory)
    try:
        manager.start(container_name)
        print("Container started successfully.")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


@cli.command(help="Stop the specified container.")
@click.argument("container_name")
def stop(container_name):
    base_directory = load_config()
    manager = ContainerManager(base_directory)
    try:
        manager.stop(container_name)
        print("Container(s) stopped successfully.")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


@cli.command(help="Restart the specified container.")
@click.argument("container_name")
def restart(container_name):
    base_directory = load_config()
    manager = ContainerManager(base_directory)
    try:
        manager.restart(container_name)
        print("Container restarted successfully.")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


@cli.command(help="Open the container's URL in the default web browser")
@click.argument("container_name")
def open(container_name):
    base_directory = load_config()
    manager = ContainerManager(base_directory)
    try:
        url = manager.open_url(container_name)
        print(f"Opening {url}")
        webbrowser.open(url)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()


if __name__ == "__main__":
    cli()
