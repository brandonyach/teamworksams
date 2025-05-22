from setuptools import setup, find_packages, os

setup(
    name="teamworksams",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests", 
        "requests-toolbelt",
        "pandas", 
        "keyring",
        "os",
        "tqdm",
        "typing",
        "datetime",
        "hashlib",
        "mimetype"
        ],
    extras_require={"test": ["pytest>=7.0", "pytest-cov>=4.0", "responses>=0.23"]},
    author="Brandon Yach", 
    author_email="yachb35@gmail.com",
    description="A Python library for interacting with the Teamworks AMS API",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/brandonyach/teamworksams", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ]
)