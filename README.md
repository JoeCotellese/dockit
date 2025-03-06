# Dockit

A simple app to run Docker containers easily.

## Installation

Install via pipx or pip:

```bash
# Using pipx
pipx install .

# Or using pip
pip install .
```

## Usage

1. Create a config file at `~/.dockit_config` with the following content:

    ```ini
    [global]
    base_directory = ~/docker-apps  # Supports ~, $HOME, $PWD
    ```

2. Run a container:

    ```bash
    dockit <container_name>
    ```

## Contribution

We welcome contributions! To get started:

1. **Fork the repository** and clone your local copy.
2. **Install dependencies** using Poetry:
    ```bash
    poetry install
    ```
3. **Make changes** to the codebase.
4. **Run tests** before submitting a pull request:
    ```bash
    pytest
    ```
5. **Submit a pull request** with a clear description of your changes.

### Code Style

- Follow **PEP8** for Python code formatting.
- Use **ruff** for formatting and linting:
    ```bash
    ruff check .
    ruff format .
    ```
- Ensure all changes are **type-checked** with `mypy`:
    ```bash
    mypy dockit/
    ```

### Feature Requests & Issues

- Report issues or suggest features in the **GitHub Issues** section.
- For major changes, please open an issue first to discuss the direction.

Happy coding! 🚀

