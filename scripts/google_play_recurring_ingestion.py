import sqlite3
from datetime import datetime
from google_play_scraper import reviews, Sort

DB_PATH = "data/google_play_reviews.db"

APPS = {
    "Instagram": {
        "app_id": "com.instagram.android",
        "category": "Social"
    },
    "Canvas Student": {
        "app_id": "com.instructure.candroid",
        "category": "Education"
    },
    "PayPal": {
        "app_id": "com.paypal.android.p2pmobile",
        "category": "Finance"
    },
    "Strava": {
        "app_id": "com.strava",
        "category": "Health & Fitness"
    },
    "Spotify": {
        "app_id": "com.spotify.music",
        "category": "Music & Audio"
    }
}

TARGET_PER_APP = 200
BATCH_SIZE = 100


def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apps (
        app_id TEXT PRIMARY KEY,
        app_name TEXT NOT NULL,
        category TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        review_id TEXT PRIMARY KEY,
        app_id TEXT NOT NULL,
        user_name TEXT,
        review_text TEXT,
        rating INTEGER CHECK (rating BETWEEN 1 AND 5),
        thumbs_up_count INTEGER,
        review_created_version TEXT,
        review_timestamp TEXT,
        FOREIGN KEY (app_id)
            REFERENCES apps(app_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS developer_replies (
        review_id TEXT PRIMARY KEY,
        reply_content TEXT,
        reply_timestamp TEXT,
        FOREIGN KEY (review_id)
            REFERENCES reviews(review_id)
    );
    """)

    conn.commit()
    conn.close()

    print("SQLite database initialized successfully.")


def collect_app_reviews(app_id, target=200):
    collected = []
    continuation_token = None

    while len(collected) < target:

        remaining = target - len(collected)
        count = min(BATCH_SIZE, remaining)

        result, continuation_token = reviews(
            app_id,
            lang="en",
            country="us",
            sort=Sort.NEWEST,
            count=count,
            continuation_token=continuation_token
        )

        if not result:
            break

        collected.extend(result)

        print(
            f"Fetched batch: {len(result)} | "
            f"Total fetched: {len(collected)}"
        )

        if continuation_token is None:
            break

    return collected[:target]


def run_ingestion():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    run_time = datetime.now().isoformat(timespec="seconds")

    print("\n======================================")
    print("INGESTION RUN")
    print("Run time:", run_time)
    print("======================================")

    total_fetched = 0
    total_inserted = 0
    total_duplicates = 0
    total_failed = 0
    total_replies_inserted = 0

    for app_name, app_info in APPS.items():

        app_id = app_info["app_id"]
        category = app_info["category"]

        print("\n======================================")
        print("Collecting:", app_name)
        print("======================================")

        cursor.execute("""
        INSERT OR IGNORE INTO apps (
            app_id,
            app_name,
            category
        )
        VALUES (?, ?, ?);
        """, (
            app_id,
            app_name,
            category
        ))

        try:
            result = collect_app_reviews(
                app_id,
                TARGET_PER_APP
            )

        except Exception as e:
            print("Collection failed:", e)
            total_failed += TARGET_PER_APP
            continue

        fetched = len(result)
        inserted = 0
        duplicates = 0
        failed = 0
        replies_inserted = 0

        total_fetched += fetched

        for review in result:

            try:
                review_id = review.get("reviewId")

                cursor.execute("""
                INSERT OR IGNORE INTO reviews (
                    review_id,
                    app_id,
                    user_name,
                    review_text,
                    rating,
                    thumbs_up_count,
                    review_created_version,
                    review_timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    review_id,
                    app_id,
                    review.get("userName"),
                    review.get("content"),
                    review.get("score"),
                    review.get("thumbsUpCount"),
                    review.get("reviewCreatedVersion"),
                    review.get("at").isoformat()
                    if review.get("at") is not None
                    else None
                ))

                if cursor.rowcount == 1:
                    inserted += 1
                else:
                    duplicates += 1

                if review.get("replyContent") is not None:

                    cursor.execute("""
                    INSERT OR IGNORE INTO developer_replies (
                        review_id,
                        reply_content,
                        reply_timestamp
                    )
                    VALUES (?, ?, ?);
                    """, (
                        review_id,
                        review.get("replyContent"),
                        review.get("repliedAt").isoformat()
                        if review.get("repliedAt") is not None
                        else None
                    ))

                    if cursor.rowcount == 1:
                        replies_inserted += 1

            except Exception as e:
                failed += 1
                print(
                    "Failed to process review:",
                    review.get("reviewId"),
                    e
                )

        conn.commit()

        total_inserted += inserted
        total_duplicates += duplicates
        total_failed += failed
        total_replies_inserted += replies_inserted

        print("\nApp summary:")
        print("Fetched:", fetched)
        print("Inserted:", inserted)
        print("Duplicates:", duplicates)
        print("Failed:", failed)
        print("Replies inserted:", replies_inserted)

    print("\n======================================")
    print("RUN SUMMARY")
    print("======================================")

    print("Total fetched:", total_fetched)
    print("Total inserted:", total_inserted)
    print("Total duplicates:", total_duplicates)
    print("Total failed:", total_failed)
    print(
        "Developer replies inserted:",
        total_replies_inserted
    )

    cursor.execute(
        "SELECT COUNT(*) FROM reviews;"
    )
    database_review_count = cursor.fetchone()[0]

    cursor.execute(
        "PRAGMA foreign_key_check;"
    )
    foreign_key_issues = cursor.fetchall()

    print(
        "Database review count:",
        database_review_count
    )

    print(
        "Foreign key issues:",
        len(foreign_key_issues)
    )

    conn.close()


initialize_database()
run_ingestion()
