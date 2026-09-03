# Google Play SQLite Ingestion Test Summary

## Test Scope

An initial end-to-end ingestion test was conducted using live Google Play review collection.

Five apps were included:

- Instagram
- Canvas Student
- PayPal
- Strava
- Spotify

For each app, 20 of the most recent U.S. English reviews were collected, for a total of 100 reviews.

---

## Ingestion Results

| App | Reviews Fetched | Reviews Stored |
|---|---:|---:|
| Instagram | 20 | 20 |
| Canvas Student | 20 | 20 |
| PayPal | 20 | 20 |
| Strava | 20 | 20 |
| Spotify | 20 | 20 |
| **Total** | **100** | **100** |

Database results:

- Apps stored: 5
- Reviews stored: 100
- Developer replies stored: 2
- Records that could not be processed or stored: 0
- Foreign key issues: 0

---

## Database Verification

The final SQLite database contained:

- 5 records in `apps`
- 100 records in `reviews`
- 2 records in `developer_replies`

Each app was associated with exactly 20 review records.

The SQLite foreign-key integrity check returned zero violations, confirming that:

- every review references a valid app;
- every developer reply references a valid review.

---

## End-to-End Workflow

The tested workflow was:

    Google Play live source
            ↓
    Python collection process
            ↓
    Field mapping
            ↓
    SQLite insertion
            ↓
    apps
    reviews
    developer_replies
            ↓
    Database verification

The test confirms that reviews can be collected programmatically from the live Google Play source and successfully mapped into the proposed relational schema.

---

## Notes

The Python runtime produced a deprecation warning related to SQLite's default datetime adapter. This did not prevent any records from being inserted, but datetime serialization should be updated in a future revision.

The ingestion process uses primary keys together with `INSERT OR IGNORE`, so previously stored review IDs are not duplicated when the script is run again.
