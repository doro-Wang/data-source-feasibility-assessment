# Google Play Review Database Schema Proposal

## 1. Design Overview

The proposed database is designed to store Google Play review data in a clean and practical relational structure.

The schema uses three main tables:

- `apps`: stores app-level information
- `reviews`: stores individual user reviews
- `developer_replies`: stores developer responses to reviews

This structure separates app metadata from review-level data and avoids storing mostly empty developer-reply fields directly in the review table.

---

## 2. Entity Relationship Diagram

```text
APPS
-------------------------
PK  app_id
    app_name
    category
        |
        | 1 : many
        |
        v
REVIEWS
-------------------------
PK  review_id
FK  app_id
    user_name
    review_text
    rating
    thumbs_up_count
    review_created_version
    review_timestamp
        |
        | 1 : 0..1
        |
        v
DEVELOPER_REPLIES
-------------------------
PK/FK review_id
      reply_content
      reply_timestamp
```

## 3. Table Definitions

### 3.1 `apps`

Stores information that describes each Google Play application.

| Field | Data Type | Key | Description |
|---|---|---|---|
| `app_id` | VARCHAR(255) | Primary Key | Google Play package identifier |
| `app_name` | VARCHAR(255) |  | Human-readable app name |
| `category` | VARCHAR(100) |  | Google Play app category |

Example:

    com.instagram.android | Instagram | Social

---

### 3.2 `reviews`

Stores one record for each Google Play user review.

| Field | Data Type | Key | Description |
|---|---|---|---|
| `review_id` | VARCHAR(255) | Primary Key | Unique Google Play review identifier |
| `app_id` | VARCHAR(255) | Foreign Key | References `apps.app_id` |
| `user_name` | VARCHAR(255) |  | Public reviewer display name |
| `review_text` | TEXT |  | Review content |
| `rating` | SMALLINT |  | Star rating from 1 to 5 |
| `thumbs_up_count` | INTEGER |  | Number of helpful/thumbs-up votes |
| `review_created_version` | VARCHAR(100) | Nullable | App version associated with the review |
| `review_timestamp` | TIMESTAMP |  | Review timestamp |

Foreign key:

    reviews.app_id → apps.app_id

A basic constraint should also ensure that:

    rating BETWEEN 1 AND 5

---

### 3.3 `developer_replies`

Stores developer replies separately from user reviews.

| Field | Data Type | Key | Description |
|---|---|---|---|
| `review_id` | VARCHAR(255) | Primary Key / Foreign Key | Review receiving the developer reply |
| `reply_content` | TEXT |  | Developer reply text |
| `reply_timestamp` | TIMESTAMP | Nullable | Timestamp associated with the developer reply |

Foreign key:

    developer_replies.review_id → reviews.review_id

Because `review_id` is also the primary key of this table, each review can have at most one developer reply.

---

## 4. Google Play Field Mapping

| Collected Field | Destination Table | Database Field |
|---|---|---|
| `app_name` | `apps` | `app_name` |
| `category` | `apps` | `category` |
| `app_id` | `apps`, `reviews` | `app_id` |
| `review_id` | `reviews` | `review_id` |
| `user_name` | `reviews` | `user_name` |
| `review` | `reviews` | `review_text` |
| `score` | `reviews` | `rating` |
| `thumbs_up_count` | `reviews` | `thumbs_up_count` |
| `review_created_version` | `reviews` | `review_created_version` |
| `timestamp` | `reviews` | `review_timestamp` |
| `reply_content` | `developer_replies` | `reply_content` |
| `reply_timestamp` | `developer_replies` | `reply_timestamp` |

---

## 5. Primary and Foreign Keys

### Primary Keys

- `apps.app_id`
- `reviews.review_id`
- `developer_replies.review_id`

These identifiers provide stable uniqueness for the main entities in the database.

### Foreign Keys

    reviews.app_id
        → apps.app_id

    developer_replies.review_id
        → reviews.review_id

These relationships ensure that reviews cannot reference nonexistent apps and developer replies cannot exist without a corresponding review.

---

## 6. Main Design Choices

### Separate app information from reviews

App name and category are repeated for every review in the current CSV dataset. Storing this information once in the `apps` table reduces repetition and makes app metadata easier to update.

### Keep reviews as the central table

The review is the main unit of analysis. Rating, text, helpful votes, app version, and timestamp therefore remain together in the `reviews` table.

This supports common analytical queries such as:

- rating distributions by app
- review-length analysis
- helpful-vote analysis
- version-specific review analysis
- review trends over time

### Store developer replies separately

Only 254 of the 10,000 collected reviews contained developer replies. Keeping reply information in a separate table avoids storing thousands of unnecessary null values in the main review table.

It also clearly represents the optional one-to-zero-or-one relationship between a review and a developer reply.

### Store version as text

App-version values have formats such as:

    443.0.0.48.82
    9.1.76.2055
    8.2.0

These values should therefore be stored as strings.

### Use timestamps for review and reply dates

Review and developer-reply dates should be stored using timestamp data types to support filtering, ordering, and future time-based analysis.

---

## 7. Data Quality Considerations

The EDA identified several issues that should be considered during implementation.

### App-version information

`review_created_version` is missing for 2,012 of the 10,000 reviews. This field should therefore allow null values.

### Developer replies

Developer replies are sparse and highly app-specific. Only 254 reviews contained replies, with most coming from Spotify.

For this reason, developer replies are represented as an optional related table rather than a required component of every review.

### Reply timestamps

Some combinations of review and reply timestamps produced implausible negative response delays during EDA. The raw timestamp should therefore be preserved, but derived response-time metrics should not be stored until the timestamp semantics are better understood.

### Repeated and low-information text

The dataset contains short and repeated review texts. These records should remain in the raw database because they are legitimate source records, while downstream analytical pipelines can decide whether to filter them.

---

## 8. Proposed Structure

The final proposed schema is:

    apps
        app_id
        app_name
        category

    reviews
        review_id
        app_id
        user_name
        review_text
        rating
        thumbs_up_count
        review_created_version
        review_timestamp

    developer_replies
        review_id
        reply_content
        reply_timestamp

This three-table structure provides a practical foundation for storing recurring Google Play review data while remaining simple enough for the initial implementation stage.
