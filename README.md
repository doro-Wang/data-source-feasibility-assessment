# Data Source Feasibility Assessment

This repository contains a feasibility assessment of public data sources for a recurring user-generated text ingestion pipeline.

## Recommendation

Based on the controlled tests, **Steam is recommended as the source for the first recurring ingestion prototype**.

It provided the strongest combination of public accessibility, structured review data, repeatable extraction, scalable pagination, and low maintenance complexity.

## Repository Contents

- `Data Source Feasibility Comparison Report.md`  
  Detailed source evaluation, test methodology, scorecards, trade-offs, and final recommendation.

- `scripts/`  
  Python scripts used for extraction, pagination, and repeatability testing.

- `sample_outputs/`  
  Small sample datasets and test results used as supporting evidence.

## Sources Tested

### Amazon
Rich product and review data, but recurring review collection is limited by authentication requirements and restricted review access.

### Steam
Public structured review data with successful pagination, repeatable collection, and strong data completeness.

### Hacker News
Public discussion data with strong accessibility and repeatability, but additional preprocessing and per-item retrieval are required.

## Now a dataset of 10,000 recent Steam reviews across five games has been collected, and exploratory data analysis (EDA) has been completed.

## A dataset of 10,000 recent Google Play reviews across five apps has been collected, and exploratory data analysis (EDA) has been completed.
