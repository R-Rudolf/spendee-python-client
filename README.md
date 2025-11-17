# Spendee Python Client

This is a Python client for interfacing with the wonderful [Spendee app](https://www.spendee.com/).

The codebase was forked from [dionysio/spendee](https://github.com/dionysio/spendee) (many thanks! <3) in 2025, which was authored in 2019-2020 and archived since then.

## ⚠️ Warning

This is a work in progress and is not recommended for general use yet. The original Spendee API is undocumented, and while this client works at the time of writing, it might stop working at any time. The author is not associated with Spendee in any way.

---

## For Users

*This section is for people who want to use the `spendee-python-client` library in their own projects.*

_(Coming soon)_

---

## For Developers & Contributors

*This section is for people who want to contribute to the development of this library.*

### Development Environment Setup

This project uses [mise](https://mise.jdx.dev/) to manage the development environment.

1.  **Install `mise`**: Follow the [official installation instructions](https://mise.jdx.dev/getting-started.html#installing-mise-cli) to install `mise` on your system.

2.  **Activate `mise`**: Activate `mise` in your shell by following the instructions for your shell in the [official documentation](https://mise.jdx.dev/getting-started.html#activate-mise).

3.  **Install Tools**: Once `mise` is activated, navigate to the project's root directory and run `mise install` to install the required tools.

4.  **Set Credentials**: Create a `.env` file in the project root and add your Spendee credentials:
    ```bash
    echo 'EMAIL=<your-email>' > .env
    echo 'PASSWORD=<your-password>' >> .env
    ```

5.  **Run**: You can now run the `run.py` script to experiment with the library:
    ```bash
    python run.py
    ```

### Backstory and Roadmap

As the forked repo was started to be used in 2025, the fetched data from the REST API was outdated by multiple days compared to what is visible on connected Bank accounts and the online webpage.

In the interim time since the original author implemented the REST API calls in 2020, Spendee most possibly migrated to another architecture. Based on browser debugging the new setup relies on Google firestore.

Authentication was extracted into a base class, to keep REST API functionalities if needed, and new firestore based one was started to benefit from the same functionalities available from the original application.

Next step will be to abstract away the most common operations.

After that groundwork, the plan is to implement an MCP server enabling AI agent collaboration to have smarter categorization and conversational exploration of spending habits.

### Contributing

If you can improve anything in this repo, feel free to add a pull request or add an issue!
