.. _getting_started:

Getting Started with teamworksams
=================================

**teamworksams** is a Python package that connects to the Teamworks AMS API, enabling users to return a flat export of Teamworks AMS data, import data from Python to Teamworks AMS, create and edit users, upload and attach files to events, update user avatars, work with database forms and related entries, and retrieve form metadata and schemas. It streamlines automation and data management for Teamworks AMS, leveraging Python’s data processing capabilities.


This guide walks you through installing `teamworksams`, setting up credentials, and running your first API call. Explore advanced features in the :ref:`vignettes` and :ref:`api_reference` vignettes.

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

Installation
------------

Install `teamworksams` using pip:

.. code-block:: bash

   pip install teamworksams

Verify the installation:

.. code-block:: python

   import teamworksams
   print(teamworksams.__version__)  # Should print '0.1.0'

**Requirements**:

- Python 3.8 or higher.
- Dependencies (installed automatically): `pandas`, `requests`, `requests_toolbelt`, `python-dotenv`, `tqdm`, `keyring`.

If you plan to run tests or contribute, install test dependencies:

.. code-block:: bash

   pip install teamworksams[test]

Prerequisites
-------------

To use `teamworksams`, you need:

1. **Teamworks AMS Account**: Obtain API access from your AMS administrator, including:
   - **URL**: Your AMS instance URL (e.g., `https://example.smartabase.com/site`).
   - **Username**: Your username (e.g., `username`).
   - **Password**: Your password (e.g., `password`).
2. **Python Environment**: A virtual environment (e.g., `venv`, `conda`) is recommended to isolate dependencies.
3. **Optional Tools**:
   - `python-dotenv` for loading `.env` files (included with `teamworksams`).
   - `keyring` for secure credential storage (included).
   - `os` to ...

Environment Setup
-----------------

Before using **teamworksams**, configure your environment to ensure smooth operation across platforms. This section covers setting up Python, installing dependencies, and preparing your workspace.

**Step 1: Install Python**

Ensure Python 3.8 or higher is installed. Verify with:

.. code-block:: bash

   python --version  # Should output Python 3.8.x or higher

If not installed, download from `python.org <https://www.python.org/downloads/>`_ or use:

.. code-block:: bash

   # macOS (Homebrew)
   brew install python@3.12

   # Ubuntu
   sudo apt-get update
   sudo apt-get install python3.12

   # Windows
   # Download installer from python.org and follow prompts

**Step 2: Create a Project Directory**

Organize your scripts and configuration files:

.. code-block:: bash

   mkdir teamworksams_project
   cd teamworksams_project

**Step 3: Install teamworksams**

Activate your virtual environment and install:

.. code-block:: bash

   pip install teamworksams


**Requirements**:

- Python 3.8 or higher.
- Dependencies (installed automatically): `pandas`, `requests`, `requests_toolbelt`, `python-dotenv`, `tqdm`, `keyring`.

If you plan to run tests or contribute, install test dependencies:

.. code-block:: bash

   pip install teamworksams[test]

**Step 4: Verify Installation**

Test the import:

.. code-block:: python

   import teamworksams
   print(teamworksams.__version__)  # Should print 0.1.0


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



   Alternatively, you can load environment variables directly using Python’s ``os`` module, which **teamworksams** supports as a fallback. This method requires manually setting environment variables or sourcing a ``.env`` file in your shell.

 **Example (Manual Setup)**:

Set variables in your shell:

   .. tab-set::

   .. tab-item:: macOS/Linux

      .. code-block:: bash

         export AMS_URL=https://example.smartabase.com/site
         export AMS_USERNAME=username
         export AMS_PASSWORD=password

   .. tab-item:: Windows (Command Prompt)

      .. code-block:: bash

         set AMS_URL=https://example.smartabase.com/site
         set AMS_USERNAME=username
         set AMS_PASSWORD=password

   Use in Python:

   .. code-block:: python

   import os
   from teamworksams import get_user
   from teamworksams.user_option import UserOption

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
      # Output: 
      # ✔ Successfully logged amsbuilder into https://example.smartabase.com/site.
      # ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
      # ℹ Processing 250 events...
      # ✔ Retrieved 250 event records for form 'Training Log'.
      # about  user_id  event_id  form         start_date  duration  intensity
      # 0  John Doe    12345    67890  Training Log  01/01/2025        60       High
      # 1  Jane Smith  12346    67891  Training Log  02/01/2025        45     Medium


      from teamworksams import get_client, get_user

      client = get_client(
          url="https://example.smartabase.com/site",
          username="username",
          password="password",
          interactive_mode=True
      )
      print(f"Authenticated: {client.authenticated}")
      # Output: ✔ Successfully logged username into https://example.smartabase.com/site.
      #         Authenticated: True



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

If you encounter authentication errors (`AMSError`):

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
   # Output: ℹ Logging username into https://example.smartabase.com/site...
   #         ✔ Successfully logged username into https://example.smartabase.com/site.
   #         Session header: abc123

   # Fetch users
   df = get_user(
       url="https://example.smartabase.com/site",
       option=UserOption(interactive_mode=True)
   )
   print(df[['user_id', 'first_name', 'groups']].head())
   # Output: ℹ Fetching user data...
   #         ✔ Retrieved 10 users.
   #            user_id first_name  groups
   #         0   12345   John Doe  Team A
   #         1   12346 Jane Smith  Team A
   #         ...

**What’s Happening**:
- :py:func:`teamworksams.login_main.login` authenticates with the AMS API, returning session details.
- :py:func:`teamworksams.user_main.get_user` fetches user data as a pandas DataFrame, with interactive feedback enabled.
- The output includes user IDs, names, and group affiliations, ready for analysis.

Next Steps
----------

- Explore :ref:`credentials` for advanced credential management, caching, and authentication details.
- Learn about user management in :ref:`user_management`.
- Dive into the :ref:`reference` for detailed function documentation.