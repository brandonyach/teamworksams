# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
project = 'teamworksams'
copyright = '2025, Brandon Yach'
author = 'Brandon Yach'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_tabs.tabs'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinxawesome_theme'
html_static_path = ['_static']
html_logo = '_static/ams_logo.png'
html_theme_options = {
    'show_scroll_to_top': True,
}

html_permalinks_icon = '<span>#</span>'

# -- Autodoc settings --------------------------------------------------------
autodoc_member_order = 'bysource'

napoleon_use_param = True
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__'
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

primary_domain = 'py'
default_role = 'any'

source_suffix = {
    '.rst': 'restructuredtext'
}

# -- Custom CSS --------------------------------------------------------------
html_css_files = ['custom.css']
