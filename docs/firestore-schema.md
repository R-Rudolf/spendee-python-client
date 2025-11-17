# Firestore schema (Spendee - inferred on 2025.08)

This document outlines the Firestore hierarchy and the main document/field schema used by the Spendee data export as observed from the client and example documents.

## Top-level hierarchy

- users/{userId}
  - wallets/{walletId}
    - transactions/{transactionId}
      - transactionLabels (collection)
  - categories/{categoryId}
  - labels/{labelId}

Notes:
- Collections are named exactly as above. Documents often include a `path` field which repeats ids for convenience (e.g. `path.wallet`, `path.transaction`).
- `transactions` documents reference categories by ID. There is a separate `transactionLabels` subcollection storing labels used for each transaction.

## Document structures and fields (examples / inferred types)

- users/{user}
  - path: { user: string } (document path metadata)
  - firestoreDataExportDone: boolean
  - name: string (user name)
  - email: string
  - legacyId: integer (legacy numeric id)
  - profile: object (profile metadata)
    - birthDate: string (YYYY-MM-DD)
    - gender: nullable string
    - email: string
    - firstname: string
    - lastname: string
    - photo: url string (profile image)
  - subscription: object (optional)
    - introOfferUsedOn: array
    - isNftOwner: nullable boolean
    - productId: string
    - renewalPeriod: string
    - pastType: string
    - expirationDate: nullable Timestamp
    - renewalDate: Timestamp
    - type: string (subscription tier)
    - platform: string
  - referral: object (optional)
    - code: string
    - isRegisteredViaReferral: boolean
    - referredUsersCount: integer
  - timezone: string (IANA tz, e.g. `Europe/Budapest`)
  - homeFeed: object (UI state)
    - lastDisplayedCard: string (card id)
  - device: object
    - languageCode: string (e.g. `hu`)
    - countryCode: string (e.g. `HU`)
  - registeredAt: Timestamp
  - updatedAt: Timestamp
  - globalCurrency: string (e.g. `HUF`)
  - modelVersion: number
  - visibleWallets: array of wallet id strings

Notes:
- Many of these are optional; `subscription` and `referral` may be absent or contain nullable members.

- users/{user}/wallets/{wallet}
  - path: { wallet: string, user: string }
  - name: string
  - type: string (e.g., "cash", "bank")
  - currency: string (e.g., "HUF", "EUR")
  - status: string (e.g., "active")
  - startingBalance: string (decimal formatted as string; may be negative and high-precision)
  - updatedAt: Timestamp
  - visibleCategories: array of category id strings (optional)
  - modelVersion: number (integer or float)
  - sharedWithUsers: array of user ids (present for shared wallets; may be empty)
  - bank: object (present for `bank` type wallets)
    - nature: string (e.g. `account`)
    - connection: string (connection id)
    - accountNumber: string (IBAN/account number)

Notes and edge cases:
- `currency` may differ per-wallet (HUF, EUR, etc.).
- `visibleCategories` lists category IDs that are permitted/visible in that wallet; not every wallet has the same set.


- users/{user}/categories/{category}
  - id: string (same as document id) -- some exports show this in list responses
  - name: string (e.g., "Other", "Étkezés")
  - type: string ("expense" or "income")

- users/{user}/labels/{label}
  - text or name: string (label text). In list output `text` appears but client maps it to `name`.
  - (document id) is the label id

- users/{user}/wallets/{wallet}/transactions/{transaction}
  - id: string (in many responses added by the client from `path.transaction`)
  - path: { user: string, wallet: string, transaction: string }
  - author: string (user id who created the transaction)
  - note: string (transaction description)
  - madeAt: Timestamp / DatetimeWithNanoseconds
  - madeAtTimezone: string (e.g., "Europe/Budapest")
  - madeAtTimezoneOffset: integer (seconds)
  - usdValue: { amount: string, exchangeRate: string } (strings in the Firestore export)
  - amount: number or string (local currency amount, sign indicates direction)
  - type: string (e.g., "regular")
  - isPending: boolean
  - category: categoryId (UUID string)
  - updatedAt: Timestamp
  - modelVersion: integer (1 currently)

  Example (extracted):
  {
    'author': 'af150597-5b96-4f8b-9eb3-0b2e0aa72a81',
    'note': '20250705 00074524 1007 MAMMUT BUDAPEST 4.500,00 HUF ...',
    'madeAt': DatetimeWithNanoseconds(2025, 7, 7, 10, 0, tzinfo=datetime.timezone.utc),
    'madeAtTimezoneOffset': 7200,
    'usdValue': {'exchangeRate': '340.45914320', 'amount': '-13.21744500'},
    'type': 'regular',
    'modelVersion': 1,
    'updatedAt': DatetimeWithNanoseconds(...),
    'madeAtTimezone': 'Europe/Budapest',
    'category': '2a4df530-a79f-49f4-8623-60000d434daa',
    'path': {'wallet': 'b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', 'transaction': 'd2b4caa7-12eb-4c04-a744-d2bf7e02bdd2', 'user': 'af150597-5b96-4f8b-9eb3-0b2e0aa72a81'},
    'isPending': False,
    'amount': '-4500'
  }


## transactionLabels subcollection
- users/{user}/wallets/{wallet}/transactions/{transaction}/transactionLabels
  - documents are small and often only contain a `label` field that references the label ID
  - list example (client side): `[x.get('label') for x in collection.get()]` -> `['01e9e6be-34ea-...']`
  - The client resolves IDs to human names using the labels collection

## Cross-references and client-side maps
- Client keeps mappings for convenience:
  - wallet_name_map: { wallet_name: wallet_id }
  - category_name_map: { category_id: category_name }
  - category_type_map: { category_id: 'income'|'expense' }
  - label_name_map: { label_id: label_text }

## How to dump arbitrary documents (helper)
- A helper `_get_raw_document(self, path: str, as_json: bool = False)` is useful to inspect any document by absolute path (for example `users/{userId}`, `users/{userId}/wallets/{walletId}`).
- Example use (the project `run.py` now calls several examples):
  - `spendee._get_raw_document(f"users/{spendee.user_id}", as_json=True)`
  - `spendee._get_raw_document(f"users/{spendee.user_id}/wallets/{walletId}", as_json=True)`

Provide outputs of these helper calls and I will update this schema with exact fields and types where necessary.
