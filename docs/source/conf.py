import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'teamworksams'
copyright = '2025, Brandon Yach'
author = 'Brandon Yach'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_tabs.tabs',
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
    'imported-members': True,
}

autodoc_mock_imports = [
    'pandas',
    'requests',
    'requests_toolbelt',
    'python_dotenv',
    'tqdm',
    'keyring',
    'dotenv',
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

primary_domain = 'py'
default_role = 'py:obj'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinxawesome_theme'
html_static_path = ['_static']
html_logo = '_static/ams_logo.png'
html_css_files = ['custom.css']
html_theme_options = {}

html_permalinks_icon = '<span>#</span>'
source_suffix = {'.rst': 'restructuredtext'}