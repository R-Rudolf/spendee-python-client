# Firestore

## High-Level Overview
Firestore is a NoSQL document database from Google Firebase. It is used in this project to store and sync data in real-time.

## Focused Examples
Here's a basic example of how we interact with Firestore:

```python
from google.cloud import firestore

# Initialize the client
db = firestore.Client()

# Get a reference to a document
doc_ref = db.collection(u'users').document(u'alovelace')

# Set data
doc_ref.set({
    u'first': u'Ada',
    u'last': u'Lovelace',
    u'born': 1815
})
```

## Pointers
*   [Official Firestore Documentation](https://firebase.google.com/docs/firestore)
*   [Python Client Library Documentation](https://googleapis.dev/python/firestore/latest/index.html)

---
For implementation details, see `spendee/agents.md`.
