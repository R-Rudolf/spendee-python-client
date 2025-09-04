# Firestore Client Test Fixtures

This directory contains shared fixtures for testing the SpendeeFirestore client. The fixtures are defined in `conftest.py` and can be used across all test files in this directory.

## How Fixtures Work

Pytest automatically discovers fixtures defined in `conftest.py` files. When you define a fixture in a `conftest.py` file, it becomes available to all test files in that directory and its subdirectories.

## Available Shared Fixtures

### Authentication and Client Fixtures

- **`firestore_client`** (session scope): Authenticated SpendeeFirestore client instance
- **`spendee_client`** (session scope): Alternative name for the same client (from parent conftest.py)

### Data Fixtures

- **`sample_wallet_id`** (session scope): A valid wallet ID for testing
- **`sample_transaction_id`** (session scope): A valid transaction ID for testing
- **`editable_transaction_id_with_wallet`** (session scope): Tuple of (wallet_id, transaction_id) for edit tests
- **`test_categories`** (session scope): List of all available categories
- **`test_labels`** (session scope): List of all available labels

### Sample Data Fixtures

- **`sample_transaction_data`** (function scope): Mock transaction data for testing
- **`sample_filter_data`** (function scope): Mock filter data for testing
- **`sample_date_range`** (function scope): Tuple of (start_date, end_date) in ISO format

### Error Testing Fixtures

- **`invalid_uuid`** (function scope): Invalid UUID string for testing error cases
- **`invalid_date_format`** (function scope): Invalid date format for testing error cases

## How to Use Shared Fixtures

### Basic Usage

Simply add the fixture name as a parameter to your test function:

```python
def test_my_function(firestore_client, sample_wallet_id):
    result = firestore_client.some_method(sample_wallet_id)
    assert result is not None
```

### Using Multiple Fixtures

You can use multiple fixtures in a single test:

```python
def test_complex_scenario(firestore_client, sample_wallet_id, test_categories, sample_date_range):
    # Your test logic here
    pass
```

### Fixture Scopes

- **Session scope**: Fixture is created once per test session and reused
- **Function scope**: Fixture is created fresh for each test function

## Adding New Shared Fixtures

To add a new shared fixture:

1. Open `conftest.py`
2. Add your fixture function with the `@pytest.fixture` decorator
3. Choose an appropriate scope (session, function, etc.)
4. Document the fixture with a docstring

Example:

```python
@pytest.fixture(scope="session")
def my_new_fixture(firestore_client):
    """
    Description of what this fixture provides.
    
    Returns: Description of return value
    """
    # Your fixture logic here
    return some_value
```

## Best Practices

1. **Use session scope** for expensive operations (like authentication)
2. **Use function scope** for simple data that can be recreated easily
3. **Document your fixtures** with clear docstrings
4. **Make fixtures reusable** by keeping them generic
5. **Use descriptive names** for your fixtures
6. **Test your fixtures** to ensure they work as expected

## Running Tests

To run tests in this directory:

```bash
# Run all tests in the firestore_client directory
pytest tests/firestore_client/

# Run a specific test file
pytest tests/firestore_client/test_transactions.py

# Run tests with verbose output
pytest tests/firestore_client/ -v

# Run tests and show fixture setup/teardown
pytest tests/firestore_client/ -v --setup-show
```

## Environment Variables

Make sure you have the following environment variables set in your `.env` file:

- `EMAIL`: Your Spendee account email
- `PASSWORD`: Your Spendee account password

## Example Test File

See `test_shared_fixtures_example.py` for a complete example of how to use the shared fixtures.
