import os
import subprocess
import time

from ezdocker.utils import get_docker_client


class ContainerManager:
    """
    Encapsulates container operations for Docker Compose projects.
    """
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.client = get_docker_client()

    def _get_project_containers(self, project_name: str):
        """Get containers for a specific compose project."""
        filters = {"label": [f"com.docker.compose.project={project_name}"]}
        return self.client.containers.list(filters=filters, all=True)

    def _get_container_dir(self, container_name: str) -> str:
        """Get the directory path for a container and validate it exists."""
        container_dir = os.path.join(self.base_directory, container_name)

        if not os.path.isdir(container_dir):
            raise FileNotFoundError(
                f"Container directory '{container_dir}' does not exist."
            )

        compose_file = os.path.join(container_dir, "docker-compose.yml")
        if not os.path.isfile(compose_file):
            raise FileNotFoundError(
                f"No docker-compose.yml file found in '{container_dir}'."
            )

        return container_dir

    def status(self) -> dict:
        """
        Returns a mapping of project names to a list of exposed host ports.
        Empty list if no ports are exposed.
        """
        containers = self.client.containers.list()
        projects = {}
        for c in containers:
            proj = c.labels.get("com.docker.compose.project")
            if not proj:
                continue
            ports = c.attrs["NetworkSettings"]["Ports"] or {}
            host_ports = []
            for mappings in ports.values():
                if mappings:
                    for m in mappings:
                        host_ports.append(m.get("HostPort"))
            # ensure project appears even if no ports exposed
            projects.setdefault(proj, host_ports)
        return projects

    def start(self, container_name: str) -> None:
        """Start a container using docker-compose."""
        container_dir = self._get_container_dir(container_name)
        project_name = os.path.basename(container_dir)

        # Check for any running containers with the same project name
        running_containers = self._get_project_containers(project_name)
        if any(c.status == "running" for c in running_containers):
            raise RuntimeError(
                f"Container(s) for project '{project_name}' "
                "are already running."
            )

        # Use docker-compose through subprocess
        try:
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=container_dir,
                check=True
            )
        except subprocess.CalledProcessError as err:
            raise RuntimeError(
                f"Failed to start container using docker-compose: {err}"
            )

    def stop(self, container_name: str) -> None:
        """Stop a container and remove it."""
        container_dir = self._get_container_dir(container_name)
        project_name = os.path.basename(container_dir)

        containers = self._get_project_containers(project_name)
        running_containers = [c for c in containers if c.status == "running"]

        if not running_containers:
            raise RuntimeError("No running containers found.")

        for container in running_containers:
            container.stop()
            container.remove()

    def restart(self, container_name: str) -> None:
        """Restart a container by stopping and starting it."""
        try:
            self.stop(container_name)
        except RuntimeError:
            # If no containers are running, just start it
            pass

        # Small delay to ensure containers are fully stopped
        time.sleep(2)

        # Then start them up again
        self.start(container_name)

    def open_url(self, container_name: str) -> str:
        """
        Get the first exposed URL of the named running container.
        Returns the URL string or raises an exception if containers/ports
        are not found.
        """
        project_name = container_name
        containers = self._get_project_containers(project_name)
        running_containers = [c for c in containers if c.status == "running"]

        if not running_containers:
            raise RuntimeError(
                f"No running containers found for '{project_name}'."
            )

        # Look for host port mappings
        ns = running_containers[0].attrs.get("NetworkSettings", {})
        ports = ns.get("Ports", {}) or {}
        for mappings in ports.values():
            if not mappings:
                continue
            host_port = mappings[0].get("HostPort")
            if host_port:
                return f"http://localhost:{host_port}"

        raise RuntimeError(f"{project_name} – No ports exposed")
