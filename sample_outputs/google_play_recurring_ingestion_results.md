# Google Play Recurring Ingestion Test Results

## Test Objective

This test evaluates whether the Google Play ingestion pipeline remains reliable when run repeatedly at a larger collection volume.

The test focuses on:

- higher collection volume;
- repeated ingestion runs;
- duplicate handling;
- newly available reviews;
- failed records;
- database integrity.

## Test Setup

- Source: Google Play
- Apps: Instagram, Canvas Student, PayPal, Strava, Spotify
- Reviews requested per app per run: 200
- Total reviews requested per run: 1,000
- Language: English
- Country: United States
- Sort order: Newest
- Database: SQLite

## Run-Level Results

| Run | Reviews Fetched | Newly Inserted | Duplicates | Failed | Database Review Count | Foreign Key Issues |
|---|---:|---:|---:|---:|---:|---:|
| Run 1 | 1,000 | 960 | 40 | 0 | 1,060 | 0 |
| Run 2 | 1,000 | 147 | 853 | 0 | 1,207 | 0 |
| Run 3 | 1,000 | 0 | 1,000 | 0 | 1,207 | 0 |

## Run 1

The first larger-volume run fetched 1,000 reviews and inserted 960 new records.

Forty reviews were already present in the database from the earlier end-to-end test, so they were correctly identified as duplicates rather than inserted again.

No records failed, and the foreign-key integrity check returned zero issues.

## Run 2

The second run fetched another 1,000 reviews.

Of which:

- 147 were newly available reviews;
- 853 overlapped with records already stored;
- 0 failed to process.

The database increased from 1,060 to 1,207 review records.

New reviews were concentrated mainly in higher-activity apps, particularly Instagram and Spotify, while lower-activity apps showed little or no change.

## Run 3

The third run fetched 1,000 reviews, but all 1,000 were already present in the database.

No new records were inserted and the database remained at 1,207 reviews.

This demonstrates that repeated ingestion does not create duplicate review records when the source window has not materially changed.

## Reliability Findings

Across all three recurring ingestion runs:

- 3,000 reviews were fetched in total;
- no records failed to process;
- duplicate records were safely ignored using the review primary key;
- the database remained internally consistent;
- all foreign-key checks returned zero violations.

The pipeline therefore handled both newly available reviews and repeated source records without creating duplicate database entries.

## Conclusion

The repeated ingestion test demonstrates that the Google Play ingestion pipeline can support higher-volume and recurring collection.

The system successfully distinguishes newly available reviews from previously stored reviews, preserves database integrity across repeated runs, and remains stable when the same source records are encountered multiple times.

These results support moving from an initial proof-of-concept ingestion process toward a more regularly scheduled collection workflow.
