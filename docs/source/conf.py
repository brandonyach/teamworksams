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
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinxawesome_theme'
html_static_path = ['_static']
html_logo = '_static/ams_logo.png'
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
}
html_permalinks_icon = '<span>#</span>'

# -- Autodoc settings --------------------------------------------------------
autodoc_member_order = 'bysource'
napoleon_google_docstring = True
napoleon_use_param = True
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

primary_domain = 'py'

# -- Custom CSS --------------------------------------------------------------
html_css_files = ['custom.css']
