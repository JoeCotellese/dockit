from ezdocker.utils import get_docker_client


class ContainerManager:
    """
    Encapsulates container operations for Docker Compose projects.
    """
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.client = get_docker_client()

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
