# EIA Pipeline: Daily NY Electricity Generation

This project is a pipeline for a daily extraction of data regarding electricity generation by fuel type for the New York region from the U.S. Energy Information Administration (EIA) Open Data API. It then loads the data to an Amazon S3 bucket as JSON files. This process is automated by a GitHub Action to run daily.

There's also a SQL file containing the necessary statements required to set up an automated process to ingest the data from S3 into a raw table in Snowflake and then perform some simple transformations on it

## Project Overview

### Data Source

Data is retrieved from the EIA Open Data API v2:
https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/

### Directory Structure

```text
├── main.py               # Primary execution script
├── modules.py            # Functions for logging and S3 upload
├── requirements.txt      # Project dependencies
├── snowflake_setup.sql   # Setup for the Snowflake part of the pipeline
├── .github/
│   └── workflows/
│       └── main.yml      # GitHub Action schedule for daily execution
├── .env                  # Environment variables. Not tracked by git
├── .venv/                # Python virtual environment. Not tracked by git
└── logs/                 # Execution logs. Not tracked by git
```

### Prerequisites

- Python 3.12 or higher
- An EIA API Key
- An AWS Account with an S3 bucket and IAM credentials (access key and secret key)
- A Snowflake account

## Installation and setup

1. **Clone the repository to your local machine**
2. **Create a virtual environment:**

```bash
python -m venv .venv
```

3. **Activate the virtual environment:**

Windows:

```
.venv\Scripts\activate
```

Unix/macOS:

```
source .venv/bin/activate
```

4. **Install the required dependencies:**

```bash
pip install -r requirements.txt
```

5. **Create a .env file with your credentials in the root directory using the template below:**

```text
api_key= {{ your_eia_api_key_here }}
aws_access_key= {{ your_aws_access_key_here }}
aws_secret_key= {{ your_aws_secret_key_here }}
s3_bucket_name= {{ your_s3_bucket_name_here }}
```

6. **Include those same variables as secrets in a GitHub environment (this is an alternative to the local, manual usage of this pipeline; it would allow the automated daily run of main.py on GitHub with a GitHub Action defined in .github/workflows/main.yml)**

7. **Copy the SQL from snowflake_setup.sql into a SQL file in Snowflake and run each statement from top to bottom, replacing anything in {{ }} with your own equivalent values (e.g. the ARN for your AWS role)**

## Usage

You can run the extract and load part of the pipeline manually using the following command:

```bash
python main.py
```

Alternatively, there's a Github Action in .github/workflows/main.yml that's set up to run the pipeline automatically each day at 4:10pm UTC (in order to give the API time to update with the prior day's data). This will only work if the necessary secrets have been added to a GitHub environment (see the installation and setup section above).

Completing the Snowflake setup will automate the refresh of a series of tables to run daily, connecting to S3 to ingest the newly loaded-in data

## What it does:

### The Python portion

#### Initialization:

The script determines the prior day's date to ensure it captures the most recent complete daily data

#### Logging:

A new log file is created in the logs/ folder for every run, tracking successes, retries, and errors

#### Data retrieval:

The script queries v2 of the EIA API. If the resulting data exceeds 5,000 rows, the script paginates through all available results

#### Resiliency:

If a 500-series server error occurs, the script waits 10 seconds and retries up to 3 times before terminating

#### S3 upload:

Data is converted to JSON strings and uploaded to the configured S3 bucket with the naming convention: YYYY-MM-DD_HH-MM-SS_Iteration.json

---

### The Snowflake portion

#### Integration with AWS

Creates a storage integration to allow Snowflake and AWS to communicate. Creates an external stage in Snowflake connected to the S3 bucket

#### Table and stream initial creation

Creates the raw and fact tables (bronze and silver layers). Creates a stream that captures new inserts into the raw table, which is later used to insert only new data into the fact table

#### Stored procedure and task setup

Creates a stored procedure to refresh all the tables. Creates a task to automate the daily run of the Snowflake portion of the pipeline

## The key files

### main.py

Manages the primary control flow for the extract and load

---

### modules.py

#### make_logger:

Initializes the logging configuration

#### print_and_log:

Outputs the provided message to both the console and the log file

#### upload_to_s3:

Loads data to AWS S3 as JSON files

---

#### snowflake_setup.sql

Contains the SQL code needed to orchestrate the Snowflake portion of the pipeline
