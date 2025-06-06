#!/usr/bin/env python3
import sys
import docker
from docker.errors import DockerException


def get_docker_client():
    """
    Return a Docker client if the Docker daemon is available, else exit.
    """
    try:
        client = docker.from_env()
        client.ping()  # Test connection to Docker daemon
        return client
    except DockerException as e:
        print("Error: Docker is not available or not running.")
        print(f"Details: {e}")
        sys.exit(1)
