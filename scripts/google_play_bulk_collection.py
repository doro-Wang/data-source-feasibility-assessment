import time
import pandas as pd

from google_play_scraper import reviews, Sort


# 1. Apps to collect

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

TARGET_PER_APP = 2000
BATCH_SIZE = 200


# 2. Collect reviews for one app

def collect_app_reviews(
    app_name,
    app_id,
    category,
    target=2000
):

    print("\n======================================")
    print("Collecting:", app_name)
    print("Category:", category)
    print("App ID:", app_id)
    print("Target:", target)
    print("======================================")

    collected_reviews = []
    seen_ids = set()

    continuation_token = None
    request_number = 0

    while len(collected_reviews) < target:

        request_number += 1

        remaining = target - len(collected_reviews)

        count = min(
            BATCH_SIZE,
            remaining
        )

        try:

            result, continuation_token = reviews(
                app_id,
                lang="en",
                country="us",
                sort=Sort.NEWEST,
                count=count,
                continuation_token=continuation_token
            )

        except Exception as e:

            print(
                "Collection failed:",
                e
            )

            break


        if not result:

            print(
                "No more reviews returned."
            )

            break


        new_reviews = 0

        for review in result:

            review_id = review.get(
                "reviewId"
            )

            if review_id in seen_ids:
                continue

            seen_ids.add(
                review_id
            )


            record = {

                "app_name":
                    app_name,

                "category":
                    category,

                "app_id":
                    app_id,

                "review_id":
                    review_id,

                "user_name":
                    review.get(
                        "userName"
                    ),

                "review":
                    review.get(
                        "content"
                    ),

                "score":
                    review.get(
                        "score"
                    ),

                "thumbs_up_count":
                    review.get(
                        "thumbsUpCount"
                    ),

                "review_created_version":
                    review.get(
                        "reviewCreatedVersion"
                    ),

                "timestamp":
                    review.get(
                        "at"
                    ),

                "reply_content":
                    review.get(
                        "replyContent"
                    ),

                "reply_timestamp":
                    review.get(
                        "repliedAt"
                    )
            }

            collected_reviews.append(
                record
            )

            new_reviews += 1


            if len(collected_reviews) >= target:
                break


        print(
            f"Request {request_number}:",
            f"+{new_reviews} reviews |",
            f"Total = {len(collected_reviews)}"
        )


        if continuation_token is None:

            print(
                "No continuation token returned."
            )

            break


        # Small delay to avoid aggressive requesting
        time.sleep(0.5)


    print(
        f"Finished {app_name}:",
        len(collected_reviews),
        "reviews collected"
    )


    return collected_reviews


# 3. Collect all apps

all_reviews = []


for app_name, app_info in APPS.items():

    app_reviews = collect_app_reviews(
        app_name=app_name,
        app_id=app_info["app_id"],
        category=app_info["category"],
        target=TARGET_PER_APP
    )

    all_reviews.extend(
        app_reviews
    )


# 4. Convert to DataFrame

df = pd.DataFrame(
    all_reviews
)


# 5. Dataset checks

print("\n======================================")
print("FINAL DATASET SUMMARY")
print("======================================")

print(
    "Total reviews:",
    len(df)
)

print(
    "\nReviews by app:"
)

print(
    df["app_name"].value_counts()
)

print(
    "\nUnique review IDs:",
    df["review_id"].nunique()
)

print(
    "\nDuplicate review IDs:",
    df["review_id"].duplicated().sum()
)

print(
    "\nMissing values:"
)

print(
    df.isna().sum()
)


# 6. Save dataset

output_path = (
    "/Users/pst/Documents/UCB ANALYTICS/Python/"
    "data/google_play_reviews.csv"
)

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8"
)

print(
    "\nDataset saved to:",
    output_path
)
