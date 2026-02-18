# EIA Pipeline: Daily NY Electricity Generation

This project is a pipeline for a daily extraction of data regarding electricity generation by fuel type for the New York region from the U.S. Energy Information Administration (EIA) Open Data API. It then loads the data to an Amazon S3 bucket as JSON files. This process is automated by a GitHub Action to run daily

## Project Overview

### Data Source

Data is retrieved from the EIA Open Data API v2:
https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/

### Directory Structure

```
├── main.py               # Primary execution script
├── modules.py            # Functions for logging and S3 upload
├── requirements.txt      # Project dependencies
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

## Installation and setup

1. **Clone the repository to your local machine**
2. **Create a virtual environment:**

```Bash
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

```Bash
pip install -r requirements.txt
```

5. **Create a .env file with your credentials in the root directory using the template below:**

```
api_key= {{ your_eia_api_key_here }}
aws_access_key= {{ your_aws_access_key_here }}
aws_secret_key= {{ your_aws_secret_key_here }}
s3_bucket_name= {{ your_s3_bucket_name_here }}
```

6. **Include the same variables as secrets in a GitHub environment (this is an alternative to the local, manual usage of this pipeline; it would allow the automated daily run of main.py on GitHub with a GitHub Action defined in .github/workflows/main.yml)**

## Usage

You can run the pipeline manually using the following command:

```Bash
python main.py
```

Alternatively, there's a Github Action in .github/workflows/main.yml that's set up to run the pipeline automatically each day at 4:10pm UTC (in order to give the API time to have the prior day's data complete)

## What it does:

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

## Python scripts

### main.py

Manages the primary control flow, API parameter configuration, and error handling logic

---

### modules.py

#### make_logger:

Initializes the logging configuration

#### print_and_log:

Outputs the provided message to both the console and the log file

#### upload_to_s3:

Loads data to AWS S3 as JSON files
