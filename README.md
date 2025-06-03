# teamworksams
A Python wrapper for the Teamworks AMS (Athlete Management System) API. <img src="man/figures/logo.png" align="right" height="100" style="float:right; height:90px; width:90px">

[![PyPI version](https://badge.fury.io/py/teamworksams.svg)](https://badge.fury.io/py/teamworksams)
[![Tests](https://github.com/brandonyach/teamworksams/actions/workflows/ci.yml/badge.svg)](https://github.com/brandonyach/teamworksams/actions)

`teamworksams` is a Python package that connects to the Teamworks AMS API, enabling users to return a flat export of Teamworks AMS data, import data from Python to Teamworks AMS, create and edit users, upload and attach files to events, update user avatars, work with database forms and related entries, and retrieve form metadata and schemas. It streamlines automation and data management for Teamworks AMS users, leveraging Python’s data processing capabilities.

## Installation
```bash
pip install teamworksams
```
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
`teamworksams` respects all permissions configured in your Teamworks AMS instance. For example, if you lack access to a form in the web or mobile app, you cannot access it via `teamworksams`. Similarly, delete permissions in AMS apply to `teamworksams` operations.

**Warning**: `teamworksams` is powerful but requires caution:
- Read all documentation thoroughly.
- Test extensively in a non-production environment.
- Contact Teamworks Support or your Teamworks AMS Product Success Manager for assistance.

## Usage
Below are examples of the core functions:

### Import Event Form Data
```python
from teamworksams import insert_event_data
from teamworksams import InsertEventOption
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
print(results)
```

### Retrieve Event Form Data
```python
from teamworksams import get_event_data
from teamworksams import EventFilter
from teamworksams import EventOption
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
print(df)
```

## Get Started
To securely provide credentials, store them in a `.env` file:
```
AMS_URL=https://example.smartabase.com/site
AMS_USERNAME=user
AMS_PASSWORD=pass
```
Read more in the [Credentials Vignette](https://brandonyach.github.io/teamworksams/credentials.html).

## Further Reading
Explore the documentation for detailed guides:
- [File Uploads](https://brandonyach.github.io/teamworksams/file-uploads.html): Uploading and attaching files to events and avatars.
- [Form Management](https://brandonyach.github.io/teamworksams/form-management.html): Retrieving form metadata and schemas.
- [API Reference](https://brandonyach.github.io/teamworksams/api-reference.html): Detailed function documentation.

## License
MIT License (see [LICENSE](LICENSE))

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.