# Environment Setup

This project uses [mise](https://mise.jdx.dev/) to manage the development environment. `mise` is a tool that helps you manage your development tools and environment variables.

## Getting Started

1.  **Install `mise`**: Follow the [official installation instructions](https://mise.jdx.dev/getting-started.html#installing-mise-cli) to install `mise` on your system.

2.  **Activate `mise`**: Activate `mise` in your shell by following the instructions for your shell in the [official documentation](https://mise.jdx.dev/getting-started.html#activate-mise).

3.  **Install Tools**: Once `mise` is activated, navigate to the project's root directory and run the following command to install the tools defined in the `.mise.toml` file:
    ```bash
    mise install
    ```

## Tools
This project uses the following tools, which are managed by `mise`:
*   **Python 3.11**
*   **jq**: A command-line JSON processor.
*   **Bitwarden CLI**: The command-line interface for Bitwarden.
