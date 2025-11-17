# Testing Agent Guide

This document provides AI coding assistants with essential context for working with the tests in this repository.

## Key Files
*   **`tests/`**: This directory contains all the tests for the project.
*   **`run_tests.sh`**: This script is used to run the test suite.
*   **`pytest.ini`**: This file contains the configuration for `pytest`.

## How to Work with Tests
When working with tests, you will primarily be adding, modifying, or running tests in the `tests/` directory. Here are some common tasks:
*   **Running Tests**: Use the `run_tests.sh` script to run the entire test suite.
*   **Running a Specific Test**: Use `pytest` to run a specific test file or test case. For example:
    ```bash
    pytest tests/spendee_mcp/test_server.py
    ```
*   **Writing New Tests**: When adding new functionality, please add corresponding tests in the `tests/` directory.
