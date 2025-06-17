# teamworksams
A Python wrapper for the Teamworks AMS (Athlete Management System) API. <img src="docs/source/_static/logo.png" align="right" height="100" style="float:right; height:90px; width:90px">

[![PyPI version](https://badge.fury.io/py/teamworksams.svg)](https://badge.fury.io/py/teamworksams)
[![Tests](https://github.com/brandonyach/teamworksams/actions/workflows/ci.yml/badge.svg)](https://github.com/brandonyach/teamworksams/actions)

`teamworksams` is a Python package that connects to the Teamworks AMS API, enabling users to return a flat export of Teamworks AMS data, import data from Python to Teamworks AMS, create and edit users, upload and attach files to events, update user avatars, work with database forms and entries, and retrieve form metadata and schemas. It streamlines automation and data management for Teamworks AMS, leveraging Python’s data processing capabilities.

## Installation
*Note*: Until available on PyPI, install from GitHub:
```bash
pip install git+https://github.com/brandonyach/teamworksams.git
```

## Requirements
- Python 3.8 or higher
- pandas
- Valid Teamworks AMS API credentials (`AMS_URL`, `AMS_USERNAME`, `AMS_PASSWORD`)
- Teamworks AMS version 6.14 or greater (or 6.13 with superadmin/site owner privileges)
- Calendar versioning (e.g., 2023.1, 2023.2) is supported

*Note*: Use your Teamworks AMS username, not email address, for authentication.

## Security
`teamworksams` respects all permissions configured in your Teamworks AMS instance. For example, if you lack access to a form in the native platform, you cannot access it via the `teamworksams` package. Similarly, delete permissions in AMS apply to `teamworksams` operations.

**Warning**: `teamworksams` is powerful but requires caution:
- Read all documentation thoroughly.
- Test extensively in a non-production environment.
- Contact Teamworks Support or your Teamworks AMS Product Success Manager for assistance.

## Usage
Below are examples of the core functions:

### Import Event Form Data
```python
from teamworksams import insert_event_data, InsertEventOption
from pandas import DataFrame

df = pd.DataFrame({
        "username": ["john.doe", "jane.smith"],
        "start_date": ["01/01/2025", "01/01/2025"],
        "duration": [60, 45],
        "intensity": ["High", "Medium"]
        })

insert_event_data(
        df = df,
        form = "Training Log",
        url = "https://example.smartabase.com/site",
        username = "user",
        password = "pass",
        option = InsertEventOption(id_col = "username", interactive_mode = True)
        )

ℹ Inserting 2 events for 'Training Log'
✔ Processed 2 events for 'Training Log'
ℹ Form: TrainingLog
ℹ Result: Success
ℹ Records inserted: 2
ℹ Records attempted: 2
```

### Retrieve Event Form Data
```python
from teamworksams import get_event_data, EventFilter, EventOption
from pandas import DataFrame


df = get_event_data(
        form = "Training Log",
        start_date = "01/01/2025",
        end_date = "31/01/2025",
        url = "https://example.smartabase.com/site",
        username = "user",
        password = "pass",
        filter = EventFilter(user_key = "group", user_value = "Example Group"),
        option = EventOption(interactive_mode = True, clean_names = True)
        )

ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
ℹ Processing 10 events...
✔ Retrieved 10 event records for form 'Training Log'.

print(df)

   about   user_id   event_id  form         start_date  duration  intensity
0  John Doe    12345    67890  Training Log  01/01/2025        60       High
1  Jane Smith  12346    67891  Training Log  02/01/2025        45     Medium
```

## Get Started
To securely provide credentials, store them in a `.env` file:
```
AMS_URL=https://example.smartabase.com/site
AMS_USERNAME=user
AMS_PASSWORD=pass
```
Read more in the [Geting Started Vignette](https://brandonyach.github.io/teamworksams/vignettes/getting_started.html).

## Further Reading
Explore the documentation for detailed guides:
- [Credentials](https://brandonyach.github.io/teamworksams/vignettes/credentials.html): Manage credentials and authentication.
- [User Management](https://brandonyach.github.io/teamworksams/vignettes/exporting_data.html): Retreive user and group data, update user accounts, and create new users
- [Exporting Data](https://brandonyach.github.io/teamworksams/vignettes/exporting_data.html): Retrieve event and profile data from Teamworks AMS.
- [Importing Data](https://brandonyach.github.io/teamworksams/vignettes/importing_data.html): Insert, update, and upsert event data to Teamworks AMS.
- [Uploading Files](https://brandonyach.github.io/teamworksams/vignettes/uploading_files.html): Upload and attach files to events and profile avatars.
- [Database Operations](https://brandonyach.github.io/teamworksams/vignettes/database_operations.html): Retrieve, create, update, and delete database entries.
- [Managing Forms](https://brandonyach.github.io/teamworksams/vignettes/managing_forms.html): List accessible forms and summarize form schemas.

## License
MIT License (see [LICENSE](LICENSE))

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.