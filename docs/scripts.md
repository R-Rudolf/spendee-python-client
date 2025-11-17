# Scripts and Dockerfile

This page provides a brief overview of the scripts and the Dockerfile in this repository.

## Scripts

*   **`build.sh`**: Builds the Docker image for the MCP server and pushes it to a local registry.
*   **`inspect.sh`**: A development script that sets up a Python virtual environment and executes the `spendee_mcp.py` script.
*   **`inspect2.sh`**: Manages the MCP inspector tool, including cloning the repository, building the Docker image, and running the container.
*   **`run-mcp.sh`**: Activates the Python virtual environment, loads environment variables, and executes the `spendee_mcp.py` script.
*   **`run.py`**: A script for manual testing and interaction with the `SpendeeApi` and `SpendeeFirestore` classes. It's useful for debugging and experimentation.
*   **`run_tests.sh`**: The test runner script. It checks for a `.env` file and then executes the test suite using `pytest`.
*   **`re-deploy.sh`**: This script was requested for documentation but does not exist in the repository.

## Dockerfile
The `Dockerfile` sets up a Python 3.11 environment, installs dependencies from `requirements.txt`, copies the application code, and defines the entry point to run the MCP server.
