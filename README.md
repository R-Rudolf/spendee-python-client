# Spendee Python Client

This is a Python client for interfacing with the wonderful [Spendee app](https://www.spendee.com/).

The codebase was forked from [dionysio/spendee](https://github.com/dionysio/spendee) (many thanks! <3) in 2025, which was authored in 2019-2020 and archived since then.

About Spendee:
> Spendee.com is a budget and expense tracker application to manage personal finances. It allows users to connect bank accounts, e-wallets, and crypto wallets to get an aggregated overview of their financial situation. The app helps users organize and analyze spending through automatic transaction categorization, visually appealing graphs, and insights.

## ⚠️ Warning

This is a work in progress and is not recommended for general use yet. The original Spendee API is undocumented, and while this client works at the time of writing, it might stop working at any time. The author is not associated with Spendee in any way.

---

## Setup

Only linux is documented:

1. Set credentials in a newly created `.env` file.
   ```bash
   echo 'EMAIL=<email>' > .env
   echo 'PASSWORD=<password>' >> .env
   ```
2. Start the setup script.
    ```bash
    ./setup.sh
    ```
3. Adapt `run.py` for your experiment and execute.


### Backstory and Roadmap

As the forked repo was started to be used in 2025, the fetched data from the REST API was outdated by multiple days compared to what is visible on connected Bank accounts and the online webpage.

In the interim time since the original author implemented the REST API calls in 2020, Spendee most possibly migrated to another architecture. Based on browser debugging the new setup relies on Google firestore.

Authentication was extracted into a base class, to keep REST API functionalities if needed, and new firestore based one was started to benefit from the same functionalities available from the original application.

Next step will be to abstract away the most common operations.

After that groundwork, the plan is to implement an MCP server enabling AI agent collaboration to have smarter categorization and conversational exploration of spending habits.

### Contributing

If you can improve anything in this repo, feel free to add a pull request or add an issue!
