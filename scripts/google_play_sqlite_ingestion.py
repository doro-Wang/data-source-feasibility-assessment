import sqlite3

# 1. Database path

DB_PATH = "data/google_play_reviews.db"

# 2. Create database connection

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

# 3. Enable foreign key constraints

cursor.execute("PRAGMA foreign_keys = ON;")

# 4. Create apps table

cursor.execute("""
CREATE TABLE IF NOT EXISTS apps (
    app_id TEXT PRIMARY KEY,
    app_name TEXT NOT NULL,
    category TEXT
);
""")

# 5. Create reviews table

cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    app_id TEXT NOT NULL,
    user_name TEXT,
    review_text TEXT,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    thumbs_up_count INTEGER,
    review_created_version TEXT,
    review_timestamp TIMESTAMP,
    FOREIGN KEY (app_id)
        REFERENCES apps(app_id)
);
""")

# 6. Create developer_replies table

cursor.execute("""
CREATE TABLE IF NOT EXISTS developer_replies (
    review_id TEXT PRIMARY KEY,
    reply_content TEXT,
    reply_timestamp TIMESTAMP,
    FOREIGN KEY (review_id)
        REFERENCES reviews(review_id)
);
""")

# 7. Save changes

conn.commit()

conn.close()


print("SQLite database and tables created successfully.")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name;
""")

tables = cursor.fetchall()

print("\nTables in database:")
for table in tables:
    print(table[0])

conn.close()
from google_play_scraper import reviews, Sort


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

REVIEWS_PER_APP = 20


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")


for app_name, app_info in APPS.items():

    app_id = app_info["app_id"]
    category = app_info["category"]

    print("\n======================================")
    print("Collecting:", app_name)
    print("======================================")

    # Insert app
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

    # Live collection from Google Play
    result, continuation_token = reviews(
        app_id,
        lang="en",
        country="us",
        sort=Sort.NEWEST,
        count=REVIEWS_PER_APP
    )

    print("Fetched:", len(result))

    for review in result:

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
            review.get("at")
        ))

        # Insert developer reply only if one exists
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
                review.get("repliedAt")
            ))


conn.commit()
conn.close()

print("\nLive collection and database insertion completed.")

# 8. Verify database contents

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")


# Count apps
cursor.execute("SELECT COUNT(*) FROM apps;")
app_count = cursor.fetchone()[0]


# Count reviews
cursor.execute("SELECT COUNT(*) FROM reviews;")
review_count = cursor.fetchone()[0]


# Count developer replies
cursor.execute("SELECT COUNT(*) FROM developer_replies;")
reply_count = cursor.fetchone()[0]


print("\n======================================")
print("DATABASE VERIFICATION")
print("======================================")

print("Apps stored:", app_count)
print("Reviews stored:", review_count)
print("Developer replies stored:", reply_count)


# Reviews by app
print("\nReviews by app:")

cursor.execute("""
SELECT
    a.app_name,
    COUNT(r.review_id)
FROM apps a
LEFT JOIN reviews r
    ON a.app_id = r.app_id
GROUP BY
    a.app_id,
    a.app_name
ORDER BY
    a.app_name;
""")

for row in cursor.fetchall():
    print(row)


# Foreign key check
cursor.execute("PRAGMA foreign_key_check;")

foreign_key_issues = cursor.fetchall()

print("\nForeign key issues:", len(foreign_key_issues))

if foreign_key_issues:
    print(foreign_key_issues)
else:
    print("All foreign key relationships are valid.")


conn.close()
