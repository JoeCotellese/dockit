#!/usr/bin/env python3
import os
import sys
import subprocess
import configparser
import argparse
import docker
import time


def expand_path(path):
    """Expands ~ and environment variables in a path."""
    return os.path.expanduser(os.path.expandvars(path))


def load_config():
    home = os.path.expanduser("~")
    config_file = os.path.join(home, ".ezdocker_config")

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


def get_project_containers(client, project_name):
    """Get containers for a specific compose project."""
    filters = {"label": [f"com.docker.compose.project={project_name}"]}
    return client.containers.list(filters=filters, all=True)


def run_container(container_name, base_directory):
    container_dir = os.path.join(base_directory, container_name)

    if not os.path.isdir(container_dir):
        print(f"Error: Container directory '{container_dir}' does not exist.")
        sys.exit(1)

    compose_file = os.path.join(container_dir, "docker-compose.yml")
    if not os.path.isfile(compose_file):
        print(f"Error: No docker-compose.yml file found in '{container_dir}'.")
        sys.exit(1)

    client = docker.from_env()
    project_name = os.path.basename(container_dir)

    # Check for any running containers with the same project name
    running_containers = get_project_containers(client, project_name)
    if any(c.status == "running" for c in running_containers):
        print(f"Container(s) for project '{project_name}' are already running.")
        return
    if running_containers:
        print(f"Container(s) for project '{project_name}' are already running.")
        return

    # Use docker-compose through API
    try:
        subprocess.run(["docker-compose", "up", "-d"], cwd=container_dir, check=True)
        print("Container started successfully.")
    except subprocess.CalledProcessError as err:
        print("Failed to start container using docker-compose:", err)
        sys.exit(1)


def stop_container(container_name, base_directory):
    container_dir = os.path.join(base_directory, container_name)

    if not os.path.isdir(container_dir):
        print(f"Error: Container directory '{container_dir}' does not exist.")
        sys.exit(1)

    compose_file = os.path.join(container_dir, "docker-compose.yml")
    if not os.path.isfile(compose_file):
        print(f"Error: No docker-compose.yml file found in '{container_dir}'.")
        sys.exit(1)

    client = docker.from_env()
    project_name = os.path.basename(container_dir)

    containers = get_project_containers(client, project_name)
    running_containers = [c for c in containers if c.status == "running"]

    if not running_containers:
        print("No running containers found.")
        return

    for container in running_containers:
        container.stop()
        container.remove()

    print("Container(s) stopped successfully.")


def restart_container(container_name, base_directory):
    # Stop any running containers
    stop_container(container_name, base_directory)

    # Small delay to ensure containers are fully stopped
    time.sleep(2)

    # Then start them up again
    run_container(container_name, base_directory)

def status_containers(base_directory):
    client = docker.from_env()
    containers = client.containers.list()

    if not containers:
        print("No running containers found.")
        return

    for container in containers:
        project_name = container.labels.get("com.docker.compose.project")
        if project_name:
            ports = container.attrs['NetworkSettings']['Ports']
            for port, mappings in ports.items():
                if mappings:
                    for mapping in mappings:
                        host_port = mapping['HostPort']
                        print(f"{project_name} - http://localhost:{host_port}")
                else:
                    print(f"{project_name} - No ports exposed")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Docker containers from their docker-compose configurations."
    )
    parser.add_argument(
        "command",
        choices=["start", "stop", "restart", "status"],
        help="Command to execute (start, stop, restart, or status)",
    )
    parser.add_argument("container_name", nargs='?', help="Name of the container directory")
    args = parser.parse_args()

    base_directory = load_config()

    if args.command == "start":
        run_container(args.container_name, base_directory)
    elif args.command == "stop":
        stop_container(args.container_name, base_directory)
    elif args.command == "restart":
        restart_container(args.container_name, base_directory)
    elif args.command == "status":
        status_containers(base_directory)


if __name__ == "__main__":
    main()
