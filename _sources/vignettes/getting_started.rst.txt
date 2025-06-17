.. _login_ref: ../reference/login.html
.. _get_user_ref: ../reference/get_user.html

.. _getting_started:

Getting Started with teamworksams
=================================

**teamworksams** is a Python package that connects to the Teamworks AMS API, enabling users to return a flat export of Teamworks AMS data, import data from Python to Teamworks AMS, create and edit users, upload and attach files to events, update user avatars, work with database forms and related entries, and retrieve form metadata and schemas. It streamlines automation and data management for Teamworks AMS, leveraging Python’s data processing capabilities.


This guide walks you through installing `teamworksams`, setting up credentials, and running your first API call. Explore advanced features in the workflow vignettes and :ref:`reference` vignettes.

Overview
--------

The Teamworks AMS (Athlete Management System) API enables programmatic access to data stored in your AMS instance, such as user accounts and event data. `teamworksams` abstracts the complexity of API authentication, request handling, and data processing, delivering results as pandas DataFrames for easy analysis. Key features include:

- **Authentication**: Secure login with credentials via environment variables, direct arguments, or keyring.
- **Caching**: Optimize performance with reusable API clients.
- **Data Management**: Fetch, import, update, and delete event, profile, and database entries.
- **User Management**: Fetch, create, and edit users.
- **File Operations**: Upload avatars and event attachments.
- **Form Handling**: Retrieve AMS form information and schemas.


Use cases include automating athlete data exports, updating user permissions in bulk, or integrating AMS data with analytics pipelines. For example, a sports scientist might use `teamworksams` to fetch daily training logs for analysis in Jupyter notebooks, while a team administrator could update user information programmatically.

Prerequisites
-------------

Before using `teamworksams`, ensure you have:

1. **Teamworks AMS Account**: Obtain API access from your AMS administrator, including:
   - **URL**: Your AMS instance URL (e.g., `https://example.smartabase.com/site`).
   - **Username**: Your username (e.g., `username`).
   - **Password**: Your password (e.g., `password`).
2. **Python Environment**: Python 3.8 or higher. A virtual environment (e.g., `venv`, `conda`) is recommended to isolate dependencies.
3. **Optional Tools**:
   - `python-dotenv` for loading `.env` files (included with `teamworksams`).
   - `keyring` for secure credential storage (included).

Installation
------------

Currently, `teamworksams` is available for installation from GitHub. Use pip to install the package:

.. code-block:: bash

   pip install git+https://github.com/brandonyach/teamworksams.git

Verify the installation:

.. code-block:: python

   import teamworksams
   print(teamworksams.__version__)  # Should print '0.1.0'

**Requirements**:
- Python 3.8 or higher.
- Dependencies (installed automatically): `pandas`, `requests`, `requests_toolbelt`, `python-dotenv`, `tqdm`, `keyring`.

For testing or contributing, install test dependencies:

.. code-block:: bash

   pip install git+https://github.com/brandonyach/teamworksams.git#egg=teamworksams[test]

If Python 3.8+ is not installed, download from `python.org <https://www.python.org/downloads/>`_ or use:

.. code-block:: bash

   # macOS (Homebrew)
   brew install python@3.12

   # Ubuntu
   sudo apt-get update
   sudo apt-get install python3.12

   # Windows
   # Download installer from python.org and follow prompts

Environment Setup
-----------------

Set up your project workspace to organize scripts and configuration files:

1. Create a project directory:

   .. code-block:: bash

      mkdir teamworksams_project
      cd teamworksams_project

2. Create and activate a virtual environment:

   .. code-block:: bash

      # macOS/Linux
      python -m venv venv
      source venv/bin/activate

      # Windows
      python -m venv venv
      venv\Scripts\activate

3. Install `teamworksams` (as shown in the Installation section above).

Setting Up Credentials
----------------------

`teamworksams` requires an AMS instance URL and credentials for authentication. You can provide these in three ways, ensuring flexibility and security. Below are detailed instructions for each method, with best practices to avoid common pitfalls.

1. **Using Environment Variables (Recommended)**

   Store credentials in a `.env` file for secure, reusable access. This method is ideal for scripts and CI pipelines, as it avoids hardcoding sensitive information.

   Create a `.env` file in your project root:

   .. code-block:: text

      AMS_URL=https://example.smartabase.com/site
      AMS_USERNAME=username
      AMS_PASSWORD=password

   Load the `.env` file in your Python script:

   .. code-block:: python

      from dotenv import load_dotenv
      from teamworksams import login, LoginOption

      load_dotenv()
      login_result = login(
          url="https://example.smartabase.com/site",
          option=LoginOption(interactive_mode=True)
      )
      print(f"Session cookie: {login_result['cookie']}")
      # Output: ℹ Logging username into https://example.smartabase.com/site...
      #         ✔ Successfully logged username into https://example.smartabase.com/site.
      #         Session cookie: JSESSIONID=abc123



   Alternatively, you can load environment variables directly using Python’s ``os`` module, which **teamworksams** supports as a fallback. This method requires manually setting environment variables or sourcing a ``.env`` file in your shell, then using the ``os`` library:

   .. code-block:: python

      import os
      from teamworksams import get_user, UserOption

      url = os.getenv("AMS_URL")
      df = get_user(
         url=url,
         option=UserOption(interactive_mode=True)
      )
      print(df[['user_id', 'first_name']].head())

   **Output**:

   .. code-block:: text

      ℹ Fetching user data...
      ✔ Retrieved 5 users.
         user_id first_name
      0    12345       John
      ...

**Note**:

.. note::

   Using ``os.getenv`` requires manual environment variable setup, which can be error-prone for end users. Prefer ``python-dotenv`` for simplicity, as it automatically loads ``.env`` files.


2. **Using Direct Arguments**

   Pass credentials directly to functions like `get_event_data`. This is useful for quick tests or when credentials are dynamically generated.

   .. code-block:: python

      from teamworksams import get_event_data, EventOption, EventFilter

      df = get_event_data(
        form = "Training Log",
        start_date = "01/01/2025",
        end_date = "31/01/2025",
        url = "https://example.smartabase.com/site",
        username = "username",
        password = "password",
        filter = EventFilter(user_key = "group", user_value = "Example Group"),
        option = EventOption(interactive_mode = True, clean_names = True)
        )
      print(df)

      from teamworksams import get_client, get_user

      client = get_client(
          url="https://example.smartabase.com/site",
          username="username",
          password="password",
          interactive_mode=True
      )
      print(f"Authenticated: {client.authenticated}")


3. **Using Keyring (Secure Storage)**

   Store credentials securely using the `keyring` library, ideal for local development or when sharing scripts across machines.

   Set credentials:

   .. code-block:: python

      import keyring
      keyring.set_password("teamworksams", "username", "username")
      keyring.set_password("teamworksams", "password", "password")

   Use in `teamworksams`:

   .. code-block:: python

      from teamworksams import get_user

      df = get_user(url="https://example.smartabase.com/site")
      print(df.head())
      # Fetches users using keyring credentials if environment variables are unset

   **Notes**:
   - Ensure `keyring` is installed (included with `teamworksams`).
   - Use a consistent service name (`teamworksams`) for keyring entries.
   - Test keyring setup locally, as some systems (e.g., CI) may lack a keyring backend.


Troubleshooting Credentials
---------------------------

If you encounter authentication errors (:py:class:`AMSError`):

- **Invalid URL**: Ensure the URL includes the site name (e.g., `https://example.smartabase.com/site`, not `https://example.smartabase.com`).
- **Invalid Credentials**: Verify username and password with your AMS administrator.
- **Missing `.env`**: Check that `load_dotenv()` is called before API functions.
- **Keyring Issues**: Install `keyrings.alt` for CI compatibility (`pip install keyrings.alt`).

Example error handling:

.. code-block:: python

   from teamworksams import login
   try:
       login(
           url="https://invalid.smartabase.com/site",
           username="wrong",
           password="wrong"
       )
   except AMSError as e:
       print(e)  # Invalid URL or login credentials...


Quick Start
-----------

Let’s authenticate and fetch user data to get started. This example logs in, retrieves a list of users, and displays their IDs and names.

.. code-block:: python

   from teamworksams import login, get_user
   from teamworksams import LoginOption
   from dotenv import load_dotenv

   # Load credentials from .env
   load_dotenv()

   # Authenticate
   login_result = login(
       url="https://example.smartabase.com/site",
       option=LoginOption(interactive_mode=True)
   )
   print(f"Session header: {login_result['session_header']}")

   # Fetch users
   df = get_user(
       url="https://example.smartabase.com/site",
       option=UserOption(interactive_mode=True)
   )


**What’s Happening**

- `login() <login_ref_>`_ authenticates with the AMS API, returning session details.

- `get_user() <get_user_ref_>`_ fetches user data as a pandas DataFrame, with interactive feedback enabled.

- The output includes user IDs, names, and group affiliations, ready for analysis.

Next Steps
----------

- Explore :ref:`credentials` for advanced credential management, caching, and authentication details.
- Learn about user management in :ref:`user_management`.
- Dive into the :ref:`reference` for detailed function documentation.