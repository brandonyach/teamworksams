.. teamworksams documentation master file, created by
   sphinx-quickstart on Thu May 22 08:46:52 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

teamworksams
============
A Python wrapper for the Teamworks AMS (Athlete Management System) API.
------------

**teamworksams** is a Python package that connects to the Teamworks AMS API, enabling
users to return a flat export of Teamworks AMS data, import data from Python to
Teamworks AMS, create and edit users, upload and attach files to events, update user
avatars, work with database forms and entries, and retrieve form metadata and schemas.
It streamlines automation and data management for Teamworks AMS, leveraging Python’s
data processing capabilities.

Installation
------------

.. note::

   Until available on PyPI, install from GitHub:

   .. code-block:: bash

      pip install git+https://github.com/brandonyach/teamworksams.git

Requirements
------------

- Python 3.8 or higher
- ``pandas``
- Valid Teamworks AMS API credentials (``AMS_URL``, ``AMS_USERNAME``, ``AMS_PASSWORD``)
- Teamworks AMS version 6.14 or greater (or 6.13 with superadmin/site owner privileges)
- Calendar versioning (e.g., 2023.1, 2023.2) is supported

.. note::

   Use your Teamworks AMS username, not email address, for authentication.

Security
--------

**teamworksams** respects all permissions configured in your Teamworks AMS instance.
For example, if you lack access to a form in the native platform, you cannot access it
via the **teamworksams** package. Similarly, delete permissions in AMS apply to
**teamworksams** operations.

.. warning::

   **teamworksams** is powerful but requires caution:

   - Read all documentation thoroughly.
   - Test extensively in a non-production environment.
   - Contact Teamworks Support or your Teamworks AMS Product Success Manager for
     assistance.

Usage
-----

Below are examples of core functions:

**Import Event Form Data**

.. code-block:: python

   from teamworksams import insert_event_data, InsertEventOption
   from pandas import DataFrame
   df = DataFrame({
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

**Output**:

.. code-block:: text

   ℹ Inserting 2 events for 'Training Log'
   ✔ Processed 2 events for 'Training Log'
   ℹ Form: Training Log
   ℹ Result: Success
   ℹ Records inserted: 2
   ℹ Records attempted: 2

**Retrieve Event Form Data**

.. code-block:: python

   from teamworksams import get_event_data, EventFilter, EventOption
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

**Output**:

.. code-block:: text

   ℹ Requesting event data for 'Training Log' between 01/01/2025 and 31/01/2025
   ✔ Retrieved 10 event records for form 'Training Log'.
      about      user_id  event_id       form     start_date  duration intensity
   0  John Doe    12345   67890    Training Log  01/01/2025      60      High
   1  Jane Smith  12346   67891    Training Log  02/01/2025      45      Medium
   ...

Get Started
-----------

To securely provide credentials, store them in a ``.env`` file:

.. code-block:: text

   AMS_URL=https://example.smartabase.com/site
   AMS_USERNAME=user
   AMS_PASSWORD=pass

Read more in the :ref:`vignettes/getting_started` vignette.

Further Reading
---------------

Explore the documentation for detailed guides:

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   vignettes/getting_started

.. toctree::
   :maxdepth: 2
   :caption: Vignettes

   vignettes/credentials
   vignettes/user_management
   vignettes/exporting_data
   vignettes/importing_data
   vignettes/database_operations
   vignettes/uploading_files
   vignettes/managing_forms
   vignettes/deleting_data

.. toctree::
   :maxdepth: 3
   :caption: Reference

   reference/reference

Indices
-------

* :ref:`genindex`